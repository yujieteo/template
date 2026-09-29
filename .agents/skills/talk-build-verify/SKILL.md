---
name: talk-build-verify
description: Build talks, run the verifier, and fix what it reports: lint errors, TeX errors, overfull boxes, page-count mismatches, stale generated data, non-reproducible PDFs, and CI failures.
---

# Build and verify

## Commands

| Goal | Command |
| --- | --- |
| Everything, verified | `python3 scripts/build.py --check` (`make check`) |
| One talk | `python3 scripts/build.py --check <slug>` |
| One variant while iterating | `python3 scripts/build.py --only slides <slug>` |
| Live preview | `make watch TALK=<slug>` |

The pipeline, in order: lint `talk.tex` -> `sync_tokens.py --verify` ->
`derive.py --verify` (if the talk has one) -> compile seven variants in parallel
with latexmk -> check logs -> check page counts -> with `--check`, rebuild in a
temp dir and compare SHA-256.

## Fixing failures

Fix the cause in the source, never loosen the check.

| Message | Cause and fix |
| --- | --- |
| `frame at line N has no \note` | Write the note (see talk-new-talk). `% no-note` only for frames with nothing to say, e.g. a pure image. |
| `\today` / `\date` / `also` / shell escape | Write the date by hand; remove beamerswitch `also=`; the build runs every variant. |
| `stale: ...; run python3 derive.py` | Inputs changed. Run the named script, review the diff of the generated files, commit them together. |
| `compile failed: ./talk.tex:N: ...` | Read `talks/<slug>/build/talk-<variant>.log` at line N. If only `article` fails, the construct is presentation-only: `\verb` in an argument, `\againframe`, beamer-only options. Guard it with `\mode<presentation>{}` or rewrite. |
| `overfull \hbox Xpt` | Content wider than the frame or column: shorten, move a formula out of a column, shrink a chart `width=`. Line numbers point at the frame's end. |
| `overfull \vbox` | Frame too tall: split it or cut content. |
| `Label ... multiply defined` | A `label=` shown twice (e.g. `\againframe`). Use a `\hyperlink` button instead. |
| `notes: N pages, expected M` | Notes pages must equal slides pages; a note outside a frame or a frame-level overlay spec disagrees. |
| `handout/script: N pages, expected M` | A frame is excluded from `trans` but not `handout` (or vice versa). Use the same `<handout:0\|trans:0>` on both. |
| `not reproducible` | Something embeds time or randomness: `\today`, a random seed, a new package that writes dates, a removed `\pdftrailerid{}`. Find it by diffing `pdftotext` or `qpdf --qdf` output of the two builds. |

## CI

`.github/workflows/build.yml` installs TeX Live from Ubuntu 24.04 and runs
`build.py --check`; PDFs are uploaded as the `talks` artifact. A package
missing in CI but present locally means the package is not in the apt list:
add the Debian package that ships it (`apt-file search <name>.sty`), not a
vendored `.sty`.

## Report

Say which talks and variants built, page counts, whether `--check` passed, and
anything you changed to get there.
