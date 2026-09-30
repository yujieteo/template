#!/usr/bin/env python3
"""Build every output of a talk from its one talk.tex, reproducibly.

    python3 scripts/build.py                      # all talks, all variants
    python3 scripts/build.py breeden-litzenberger # one talk
    python3 scripts/build.py --only slides,notes  # some variants
    python3 scripts/build.py --check              # also prove the build is
                                                  # byte-reproducible

A talk is a directory talks/<slug>/ holding talk.tex. Each variant is the
same file compiled under a different jobname; beamerswitch and tex/yjtalk.sty
read the suffix. PDFs and SHA256SUMS land in talks/<slug>/build/.

Before compiling, the build lints talk.tex and checks that generated inputs
(tex/yjtokens.tex, and data from talks/<slug>/derive.py if present) are
current. After compiling, it fails on TeX errors, overfull boxes, undefined
references, and page counts that disagree between variants. --check compiles
everything a second time in a fresh directory and fails unless every PDF is
byte-identical.
"""
import argparse
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TALKS = ROOT / "talks"
TEX = ROOT / "tex"

# Jobname suffix -> what it is. Order is the order of SHA256SUMS.
VARIANTS = {
    "slides": "projector slides with overlays, light",
    "dark": "projector slides with overlays, dark",
    "notes": "slides with notes on a second screen (pdfpc --notes=right)",
    "script": "one page of notes per frame, to print",
    "handout": "3 frames per A4 page for the audience",
    "trans": "one page per frame, no overlays",
    "article": "the talk as a written article",
}
HANDOUT_NUP = 3
# Overfull boxes up to this width are invisible in print and on a projector.
OVERFULL_TOLERANCE_PT = 1.0
IGNORED_WARNINGS = ("Unused global option(s)",)


def fail(msg):
    sys.exit(f"build: {msg}")


def source_date_epoch(talk_dir):
    """Pin \\today and any embedded time: env, else last commit, else 0."""
    if os.environ.get("SOURCE_DATE_EPOCH"):
        return os.environ["SOURCE_DATE_EPOCH"]
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(talk_dir)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or "0"
    except (OSError, subprocess.CalledProcessError):
        return "0"


def lint(talk_dir):
    """Rules that keep one source file producing every output deterministically."""
    src = (talk_dir / "talk.tex").read_text()
    code = "\n".join(re.split(r"(?<!\\)%", line, maxsplit=1)[0] for line in src.splitlines())
    problems = []
    if not re.search(r"\\documentclass\s*(\[[^\]]*\]|\[(?:[^\[\]]|\{[^{}]*\})*\])?\s*\{beamerswitch\}", code, re.S):
        problems.append("talk.tex must use \\documentclass{beamerswitch}")
    if re.search(r"\balso\w*\s*=?", code.split("{beamerswitch}", 1)[0]):
        problems.append("do not use beamerswitch's also* options: they spawn compilers via shell escape; the build runs every variant")
    if "\\usepackage{yjtalk}" not in code:
        problems.append("talk.tex must \\usepackage{yjtalk} straight after \\documentclass")
    if "\\today" in code:
        problems.append("write the date by hand in \\date{...}; \\today changes with the build time")
    if not re.search(r"\\date\{[^}]+\}", code):
        problems.append("set \\date{...} explicitly")
    if re.search(r"\\write18|\\ShellEscape|\\immediate\\write18", code):
        problems.append("no shell escape: the build compiles with -no-shell-escape")
    for m in re.finditer(r"\\begin\{frame\}(.*?)\\end\{frame\}", src, re.S):
        body = m.group(1)
        if "\\note" not in body and "% no-note" not in body:
            line = src.count("\n", 0, m.start()) + 1
            problems.append(f"frame at line {line} has no \\note{{...}} (add one, or '% no-note' to opt out)")
    return problems


def check_generated(talk_dirs):
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_tokens.py"), "--verify"], check=True)
    for talk_dir in talk_dirs:
        derive = talk_dir / "derive.py"
        if derive.is_file():
            subprocess.run([sys.executable, str(derive), "--verify"], check=True)


def compile_variant(talk_dir, variant, outdir, epoch):
    job = f"talk-{variant}"
    env = dict(os.environ)
    env.update({
        "TEXINPUTS": f"{TEX}//{os.pathsep}",
        "SOURCE_DATE_EPOCH": epoch,
        "FORCE_SOURCE_DATE": "1",
        "TZ": "UTC",
        "LC_ALL": "C",
    })
    cmd = ["latexmk", "-pdf", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
           "-file-line-error", f"-outdir={outdir}", f"-jobname={job}", "talk.tex"]
    proc = subprocess.run(cmd, cwd=talk_dir, env=env, capture_output=True, text=True)
    log = Path(outdir) / f"{job}.log"
    log_text = log.read_text(errors="replace") if log.is_file() else ""
    problems = []
    if proc.returncode != 0:
        errors = [line for line in log_text.splitlines() if re.match(r"^(!|.*:\d+: )", line)]
        problems.append("compile failed: " + ("; ".join(errors[:3]) or proc.stdout[-500:]))
    for m in re.finditer(r"Overfull \\([hv])box \(([\d.]+)pt too (?:wide|high)\) (.*)", log_text):
        if float(m.group(2)) > OVERFULL_TOLERANCE_PT:
            problems.append(f"overfull \\{m.group(1)}box {m.group(2)}pt {m.group(3).strip()}")
    for m in re.finditer(r"^(?:LaTeX|Package \w+) Warning: (.*)$", log_text, re.M):
        text = m.group(1)
        if any(text.startswith(w) for w in IGNORED_WARNINGS):
            continue
        if re.search(r"undefined|Citation|multiply defined|Rerun", text):
            problems.append(f"warning: {text}")
    if "Missing character" in log_text:
        problems.append("a glyph is missing from the font (see log)")
    pages = re.search(r"Output written on .*?\((\d+) pages?", log_text)
    return variant, (int(pages.group(1)) if pages else 0), sorted(set(problems))


def build_talk(talk_dir, variants, outdir, epoch):
    outdir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=min(len(variants), os.cpu_count() or 2)) as pool:
        results = list(pool.map(lambda v: compile_variant(talk_dir, v, outdir, epoch), variants))
    pages = {v: p for v, p, _ in results}
    problems = [f"{v}: {p}" for v, _, ps in results for p in ps]

    # Cross-variant structure: the variants must agree on the frame count.
    frames = pages.get("trans")
    expect = {
        "notes": pages.get("slides"),
        "dark": pages.get("slides"),
        "script": frames,
        "handout": math.ceil(frames / HANDOUT_NUP) if frames else None,
    }
    for v, n in expect.items():
        if v in pages and n is not None and pages[v] != n:
            problems.append(f"{v}: {pages[v]} pages, expected {n}")
    return pages, problems


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("talks", nargs="*", help="talk slugs under talks/ (default: all)")
    ap.add_argument("--only", help=f"comma-separated variants (default: {','.join(VARIANTS)})")
    ap.add_argument("--check", action="store_true", help="rebuild in a fresh directory and require identical bytes")
    args = ap.parse_args()

    if not shutil.which("latexmk"):
        fail("latexmk not found; install TeX Live (see README.md)")
    variants = args.only.split(",") if args.only else list(VARIANTS)
    unknown = [v for v in variants if v not in VARIANTS]
    if unknown:
        fail(f"unknown variant(s): {', '.join(unknown)}")
    slugs = args.talks or sorted(p.parent.name for p in TALKS.glob("*/talk.tex"))
    talk_dirs = [TALKS / s for s in slugs]
    missing = [str(d) for d in talk_dirs if not (d / "talk.tex").is_file()]
    if missing:
        fail(f"no talk.tex in {', '.join(missing)}")

    lint_problems = [f"{d.name}: {p}" for d in talk_dirs for p in lint(d)]
    if lint_problems:
        fail("lint failed:\n  " + "\n  ".join(lint_problems))
    check_generated(talk_dirs)

    failed = False
    for talk_dir in talk_dirs:
        epoch = source_date_epoch(talk_dir)
        outdir = talk_dir / "build"
        pages, problems = build_talk(talk_dir, variants, outdir, epoch)
        sums = {v: sha256(outdir / f"talk-{v}.pdf") for v in variants if (outdir / f"talk-{v}.pdf").is_file()}
        (outdir / "SHA256SUMS").write_text("".join(f"{h}  talk-{v}.pdf\n" for v, h in sums.items()))

        if args.check and not problems:
            with tempfile.TemporaryDirectory(prefix="talk-rebuild-") as tmp:
                _, again = build_talk(talk_dir, variants, Path(tmp), epoch)
                problems += again
                for v, h in sums.items():
                    if sha256(Path(tmp) / f"talk-{v}.pdf") != h:
                        problems.append(f"{v}: not reproducible, second build differs")

        print(f"{talk_dir.name} (SOURCE_DATE_EPOCH={epoch})")
        for v in variants:
            print(f"  talk-{v}.pdf  {pages.get(v, 0):3d} pages  {sums.get(v, '-')[:12]}  {VARIANTS[v]}")
        if problems:
            failed = True
            print("  FAILED:\n    " + "\n    ".join(problems))
        elif args.check:
            print("  verified: lint clean, no overfull boxes, page counts agree, byte-reproducible")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
