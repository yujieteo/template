#!/usr/bin/env python3
"""Scaffold talks/<slug>/talk.tex from starter/talk.tex.

    python3 scripts/new_talk.py my-talk --title "My talk" --date "1 October 2026"

Refuses to overwrite an existing talk. The date defaults to today, written
into the file once, so later builds stay reproducible.
"""
import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_author():
    try:
        return subprocess.run(["git", "config", "user.name"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="kebab-case directory name under talks/")
    ap.add_argument("--title", default="Title that states the claim")
    ap.add_argument("--author", default=git_author() or "Author")
    ap.add_argument("--date", default=datetime.date.today().strftime("%-d %B %Y"))
    args = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        sys.exit("slug must be kebab-case, e.g. options-and-density")
    dest = ROOT / "talks" / args.slug
    if dest.exists():
        sys.exit(f"talks/{args.slug} already exists; edit it instead")
    text = (ROOT / "starter" / "talk.tex").read_text()
    for key, value in {"SLUG": args.slug, "TITLE": args.title, "AUTHOR": args.author, "DATE": args.date}.items():
        text = text.replace("{{" + key + "}}", value)
    dest.mkdir(parents=True)
    (dest / "talk.tex").write_text(text)
    print(f"created talks/{args.slug}/talk.tex; build it with: make check TALK={args.slug}")


if __name__ == "__main__":
    main()
