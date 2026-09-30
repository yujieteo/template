---
name: talk-build-verify
description: The build and every check that guards it, from lint, TeX errors, overfull boxes and page counts to stale generated data, reproducibility, Python and Markdown lint, the skills check, unit tests and CI. Use when building talks, running any check, or fixing a failing one locally or in CI.
---

# Build and verify

Playbook: [fix-build](../../playbooks/fix-build.md).

## Commands

| Goal | Command |
| --- | --- |
| Everything CI runs | `make ci` |
| Lint and tests, no TeX | `make lint test` |
| Every talk, verified | `make check` (`python3 scripts/build.py --check`) |
| One talk | `make check TALK=<slug>` |
| One variant while iterating | `python3 scripts/build.py --only slides <slug>` |
| Live preview | `make watch TALK=<slug>` |
| One lint | `make lint-py`, `make lint-md`, `make lint-skills` |

`make lint test` needs the pinned tools in `.venv`
(`python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`),
which the Makefile uses when it exists, and Node for markdownlint, which runs
through `npx`.

The talk pipeline, in order: lint `talk.tex` -> `sync_tokens.py --verify` ->
`derive.py --verify` (if the talk has one) -> compile seven variants in
parallel with latexmk -> check logs -> check page counts -> with `--check`,
rebuild in a temp dir and compare SHA-256.

## Failures

Fix the cause in the source, never loosen the check.

| Message | Cause and fix |
| --- | --- |
| `frame at line N has no \note` | Write the note ([talk-new-talk](../talk-new-talk/SKILL.md)). `% no-note` only for frames with nothing to say. |
| `\today` / `\date` / `also` / shell escape | Write the date by hand; remove beamerswitch `also=`; the build runs every variant. |
| `stale: ...; run python3 derive.py` | Inputs changed. Run the named script, review the diff of the generated files, commit them together. |
| `compile failed: ./talk.tex:N: ...` | Read `talks/<slug>/build/talk-<variant>.log` at line N. If only `article` fails, the construct is presentation-only: `\verb` in an argument, `\againframe`, beamer-only options. Guard it with `\mode<presentation>{}` or rewrite. |
| `overfull \hbox Xpt` | Content wider than the frame or column: shorten, move a formula out of a column, shrink a chart `width=`. Line numbers point at the frame's end. |
| `overfull \vbox` | Frame too tall: split it or cut content. |
| `Label ... multiply defined` | A `label=` shown twice (e.g. `\againframe`). Use a `\hyperlink` button instead. |
| `notes: N pages, expected M` | Notes pages must equal slides pages; a note outside a frame or a frame-level overlay spec disagrees. |
| `handout/script: N pages, expected M` | A frame is excluded from `trans` but not `handout` (or vice versa). Use the same `<handout:0\|trans:0>` on both. |
| `not reproducible` | Something embeds time or randomness: `\today`, a random seed, a new package that writes dates, a removed `\pdftrailerid{}`. Find it by diffing `pdftotext` or `qpdf --qdf` output of the two builds. |
| ruff finding | Fix the code. `ruff check --fix` is safe for import order; read any other autofix before keeping it. Rules live in `pyproject.toml`. |
| markdownlint finding | Fix the Markdown. Rules and their reasons live in `.markdownlint-cli2.jsonc`. |
| `check_skills: ...` | A skill, playbook or router entry disagrees; see [skill-change](../../playbooks/skill-change.md). A missing path means a doc names a file that moved: fix the doc. |
| pytest failure | Read the assertion. A test pins behaviour a talk or converter relies on; change the test only when that behaviour is meant to change, in the same commit. |

## CI

Two workflows run on every push and pull request. Both pin each action to a
commit SHA, with the release tag in a comment.

- `.github/workflows/checks.yml`, "Lint and test": one job each for
  `make lint-py`, `make lint-md`, `make lint-skills` and `make test`, on
  Ubuntu 24.04's Python with `requirements-dev.txt`. No TeX.
- `.github/workflows/build.yml`, "Build talks": installs TeX Live from Ubuntu
  24.04's apt, runs `build.py --check`, builds every web deck and the video
  inputs, and uploads the PDFs and web decks as the `talks` artifact.

A package missing in CI but present locally means the package is not in the
apt list: add the Debian package that ships it (`apt-file search <name>.sty`),
not a vendored `.sty`. A lint or test that passes locally but fails in CI
usually means an unpinned local tool: install from `requirements-dev.txt`.
Read a failed job with `gh run view <run-id> --log-failed`.
