#!/usr/bin/env python3
"""Read a built talk into one manifest: frames, pages, notes, narration, text.

    python3 scripts/talk_manifest.py <slug>          # print the manifest
    python3 scripts/talk_manifest.py <slug> --write  # also save build/talk.json

The web and video converters start from this. It combines two sources:

* talk.tex, parsed for the title block, sections, frame titles, labels,
  \\note, \\narration and \\yjsource. Zero-argument macros defined with
  \\newcommand in talk.tex or an \\input file (data/numbers.tex) are expanded,
  so numbers read the same as on the slides.
* build/talk-slides.nav, which beamer writes with the page range of every
  frame. Frames are matched to page ranges in order; the manifest refuses to
  build when the counts disagree, instead of guessing.

Section divider frames (from yjtalk's \\AtBeginSection) appear as frames of
kind "section". Nothing here runs TeX; build the talk first.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TALKS = ROOT / "talks"

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν",
    "xi": "ξ", "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "phi": "φ", "varphi": "φ",
    "chi": "χ", "psi": "ψ", "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ",
    "Lambda": "Λ", "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
SYMBOLS = {
    "cdot": "·", "times": "×", "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "approx": "≈",
    "pm": "±", "infty": "∞", "int": "∫", "sum": "Σ", "prod": "Π", "to": "→", "rightarrow": "→",
    "leftarrow": "←", "partial": "∂", "neq": "≠", "ne": "≠", "in": "∈", "ldots": "…",
    "dots": "…", "cdots": "…", "quad": " ", "qquad": " ", "textbackslash": "\\",
    "textperiodcentered": "·", "LaTeX": "LaTeX", "TeX": "TeX",
}
# Commands whose single argument is kept as text (optionally marked as code).
KEEP = {"emph", "textit", "textbf", "textsc", "textrm", "textsf", "text", "mathrm", "mathbf",
        "mathit", "boldsymbol", "yjkey", "alert", "structure", "mbox", "hbox", "textnormal",
        "operatorname", "underline", "overline", "mathcal", "uncover", "only", "visible",
        "invisible", "onslide", "textcolor", "color"}
DROP_WITH_ARG = {"label", "vspace", "hspace", "vskip", "hskip", "yjsource", "note", "narration",
                 "pause", "centering", "par", "raggedright", "noindent", "small", "footnotesize",
                 "scriptsize", "tiny", "large", "Large", "LARGE", "huge", "Huge", "normalsize",
                 "bigskip", "medskip", "smallskip", "left", "right", "big", "Big", "bigg", "Bigg",
                 "displaystyle", "limits", "nolimits"}


def fail(msg):
    sys.exit(f"talk_manifest: {msg}")


# ---------------------------------------------------------------- TeX reading
def strip_comments(src):
    return "\n".join(re.split(r"(?<!\\)%", line, maxsplit=1)[0] for line in src.splitlines())


def read_group(s, i, open_="{", close="}"):
    """Return (content, index after the group) for a balanced group at s[i]."""
    if i >= len(s) or s[i] != open_:
        return None, i
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == open_:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    fail(f"unbalanced {open_}{close} near: {s[i:i + 60]!r}")


def skip_ws(s, i):
    while i < len(s) and s[i] in " \t\n":
        i += 1
    return i


def read_command_args(s, i):
    """After a command name: optional <spec>, [opt], then {arg}. Returns dict."""
    out = {"spec": None, "opt": None, "arg": None}
    j = skip_ws(s, i)
    if j < len(s) and s[j] == "<":
        end = s.index(">", j)
        out["spec"], j = s[j + 1:end], skip_ws(s, end + 1)
    if j < len(s) and s[j] == "[":
        out["opt"], j = read_group(s, j, "[", "]")
        j = skip_ws(s, j)
    if j < len(s) and s[j] == "<" and out["spec"] is None:
        end = s.index(">", j)
        out["spec"], j = s[j + 1:end], skip_ws(s, end + 1)
    if j < len(s) and s[j] == "{":
        out["arg"], j = read_group(s, j)
    return out, j


def find_commands(s, name):
    """Yield (args, start, end) for every \\name in s."""
    for m in re.finditer(r"\\" + name + r"(?![A-Za-z])", s):
        args, end = read_command_args(s, m.end())
        yield args, m.start(), end


def read_macros(src, talk_dir, seen=None):
    """Zero-argument \\newcommand / \\renewcommand / \\def macros, following \\input."""
    seen = seen if seen is not None else set()
    macros = {}
    for m in re.finditer(r"\\(?:re)?newcommand\s*\{?\\([A-Za-z]+)\}?\s*\{", src):
        body, _ = read_group(src, m.end() - 1)
        macros[m.group(1)] = body
    for m in re.finditer(r"\\input\{([^}]+)\}", src):
        path = talk_dir / m.group(1)
        if path.suffix != ".tex":
            path = path.with_suffix(".tex")
        if path.is_file() and path not in seen:
            seen.add(path)
            macros.update(read_macros(strip_comments(path.read_text()), talk_dir, seen))
    return macros


# ---------------------------------------------------------------- TeX to text
def expand(s, macros):
    for _ in range(3):
        s = re.sub(r"\\([A-Za-z]+)(?![A-Za-z])\s?",
                   lambda m: macros[m.group(1)] if m.group(1) in macros else m.group(0), s)
    return s


def math_to_text(m):
    m = re.sub(r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"(\1)/(\2)", m)
    m = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"√(\1)", m)
    m = re.sub(r"\\mathbb\s*\{E\}", "𝔼", m)
    m = re.sub(r"\\mathbb\s*\{([A-Z])\}", r"\1", m)
    m = re.sub(r"\^\{([^{}]*)\}", lambda g: "^" + (g.group(1) if len(g.group(1)) == 1 else f"({g.group(1)})"), m)
    m = re.sub(r"_\{([^{}]*)\}", lambda g: "_" + (g.group(1) if len(g.group(1)) == 1 else f"({g.group(1)})"), m)
    m = m.replace("\\,", " ").replace("\\;", " ").replace("\\!", "").replace("\\ ", " ")
    return m


def tex_to_text(s, macros, code=False):
    """Readable plain text from a TeX fragment. code=True keeps `...` for \\texttt."""
    s = expand(strip_comments(s), macros)
    # \textbackslash must not merge with the next word into a new command.
    s = re.sub(r"\\textbackslash(?![A-Za-z])\s*(\{\})?", "\x01", s)
    s = re.sub(r"\$([^$]*)\$", lambda m: math_to_text(m.group(1)), s)
    s = s.replace("\\\\", " ").replace("~", " ")
    for a, b in (("---", "—"), ("--", "–"), ("``", "“"), ("''", "”")):
        s = s.replace(a, b)
    s = s.replace("\\{", "\x02").replace("\\}", "\x03")
    s = re.sub(r"\\([%&_#$])", r"\1", s)
    s = re.sub(r"\\[,;:! ]", " ", s)
    # \texttt{...}: keep as code in Markdown, plain otherwise
    while True:
        m = re.search(r"\\texttt\s*\{", s)
        if not m:
            break
        body, end = read_group(s, m.end() - 1)
        s = s[:m.start()] + (f"`{body}`" if code else body) + s[end:]
    # commands that keep their text; strip overlay specs first
    s = re.sub(r"\\([A-Za-z]+)\s*<[^>]*>", r"\\\1", s)
    for _ in range(4):
        def repl(m):
            name = m.group(1)
            if name in GREEK:
                return GREEK[name]
            if name in SYMBOLS:
                return SYMBOLS[name]
            return "" if name in DROP_WITH_ARG or name not in KEEP else "\x00" + name
        s = re.sub(r"\\([A-Za-z]+)(?![A-Za-z])\s*", repl, s)
        # \x00name{arg} -> arg ; drop color-like first arguments
        s = re.sub(r"\x00(?:textcolor|color)\{[^{}]*\}", "", s)
        s = re.sub(r"\x00[A-Za-z]+", "", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("$", "").replace("\x01", "\\").replace("\x02", "{").replace("\x03", "}")
    return re.sub(r"\s+", " ", s).strip()


def slugify(text, words=5):
    parts = re.findall(r"[a-z0-9]+", text.lower())
    return "-".join(parts[:words]) or "frame"


# ---------------------------------------------------------------- talk.tex
def parse_talk(talk_dir):
    src_raw = (talk_dir / "talk.tex").read_text()
    src = strip_comments(src_raw)
    if "\\begin{document}" not in src:
        fail("talk.tex has no \\begin{document}")
    pre, body = src.split("\\begin{document}", 1)
    macros = read_macros(pre, talk_dir)

    def meta(name):
        for args, _, _ in find_commands(pre, name):
            if args["arg"] is not None:
                return tex_to_text(args["arg"], macros)
        return ""

    info = {k: meta(k) for k in ("title", "subtitle", "author", "institute", "date")}
    section_pages = "\\yjsectionpagesfalse" not in src
    data_files = sorted({m.group(1) for m in re.finditer(r"\\pgfplotstableread(?:\[[^\]]*\])?\{([^}]+)\}", src)})

    events = []  # (position, kind, payload)
    for m in re.finditer(r"\\section(\*?)(?![A-Za-z])", body):
        args, _ = read_command_args(body, m.end())
        if args["arg"] is not None:
            events.append((m.start(), "section", {"star": bool(m.group(1)), "title": args["arg"]}))
    for m in re.finditer(r"\\begin\{frame\}", body):
        args, j = read_command_args(body, m.end())
        end = body.find("\\end{frame}", j)
        if end < 0:
            fail("\\begin{frame} without \\end{frame}")
        content = body[j:end]
        title = args["arg"]
        if title is None:
            ft = next(find_commands(content, "frametitle"), None)
            title = ft[0]["arg"] if ft else ""
        # A frame with a title group directly after the options has content after it;
        # a frame with no title group has its whole body in `content` already.
        events.append((m.start(), "frame", {"spec": args["spec"] or "", "opt": args["opt"] or "",
                                            "title": title, "body": content}))
    events.sort(key=lambda e: e[0])

    frames, section, section_no = [], "", 0
    for _, kind, ev in events:
        if kind == "section":
            section = tex_to_text(ev["title"], macros)
            if not ev["star"]:
                section_no += 1
                if section_pages:
                    frames.append({"kind": "section", "title": section, "section": section,
                                   "section_number": section_no, "label": "", "notes": [],
                                   "narration": "", "source": ""})
            continue
        spec = ev["spec"].replace(" ", "")
        if re.search(r"(^|\|)(beamer|presentation):0", spec):
            continue  # not on the slides
        body_ = ev["body"]
        notes = [tex_to_text(a["arg"], macros, code=True)
                 for a, _, _ in find_commands(body_, "note") if a["arg"] is not None]
        narration = " ".join(tex_to_text(a["arg"], macros)
                             for a, _, _ in find_commands(body_, "narration") if a["arg"] is not None)
        source = next((tex_to_text(a["arg"], macros) for a, _, _ in find_commands(body_, "yjsource")
                       if a["arg"] is not None), "")
        label = (re.search(r"label\s*=\s*([^,\]\s]+)", ev["opt"]) or [None, ""])[1]
        is_title = "\\titlepage" in body_
        frames.append({"kind": "title" if is_title else "frame",
                       "title": info["title"] if is_title else tex_to_text(ev["title"], macros),
                       "section": section, "label": label, "notes": notes,
                       "narration": narration, "source": source})
    return info, frames, data_files


# ---------------------------------------------------------------- pages
def read_nav(path):
    if not path.is_file():
        fail(f"{path.relative_to(ROOT)} missing: build the talk first (python3 scripts/build.py <slug> --only slides,dark)")
    return [(int(a), int(b)) for a, b in re.findall(r"\\beamer@framepages \{(\d+)\}\{(\d+)\}", path.read_text())]


def page_text(pdf, page):
    out = subprocess.run(["pdftotext", "-q", "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    return re.sub(r"[ \t]+", " ", out).strip()


def build_manifest(slug):
    talk_dir = TALKS / slug
    if not (talk_dir / "talk.tex").is_file():
        fail(f"no talks/{slug}/talk.tex")
    info, frames, data_files = parse_talk(talk_dir)
    build = talk_dir / "build"
    ranges = read_nav(build / "talk-slides.nav")
    if len(ranges) != len(frames):
        found = ", ".join(f"{f['kind']}:{f['title'][:24]!r}" for f in frames)
        fail(f"talk-slides.nav has {len(ranges)} frames but talk.tex parses to {len(frames)}: {found}. "
             "Rebuild the slides; \\againframe and frames generated by macros are not supported.")
    dark_nav = build / "talk-dark.nav"
    if dark_nav.is_file() and read_nav(dark_nav) != ranges:
        fail("talk-dark.nav disagrees with talk-slides.nav; rebuild both")

    used = set()
    for n, (frame, (a, b)) in enumerate(zip(frames, ranges, strict=True), start=1):
        if frame["kind"] == "title":
            stem = "title"
        elif frame["kind"] == "section":
            stem = "section-" + slugify(frame["title"], 4)
        else:
            stem = slugify(frame["label"] or frame["title"])
        fid = f"s{n:02d}-{stem}"
        if fid in used:
            fail(f"duplicate frame id {fid}")
        used.add(fid)
        frame.update({"n": n, "id": fid, "pages": list(range(a, b + 1)),
                      "text": page_text(build / "talk-slides.pdf", b)})
    pages = ranges[-1][1] if ranges else 0
    return {
        "slug": slug, **info, "pages": pages,
        "frames": frames,
        "data": [{"path": p} for p in data_files if (talk_dir / p).is_file()],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--write", action="store_true", help="save talks/<slug>/build/talk.json")
    args = ap.parse_args()
    manifest = build_manifest(args.slug)
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        out = TALKS / args.slug / "build" / "talk.json"
        out.write_text(text)
        print(f"wrote {out.relative_to(ROOT)}: {len(manifest['frames'])} frames, {manifest['pages']} pages")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
