---
name: talk-template-maintenance
description: How the shared template works and what a change to it must preserve, covering yjtalk.sty modes and theme, the starter talk, the Python scripts and their tests, output variants, and the web and video runtimes. Use when changing any of those, since a change there reaches every talk.
---

# Template maintenance

Playbook: [template-change](../../playbooks/template-change.md).

Every talk depends on `tex/yjtalk.sty`, `starter/talk.tex` and
`scripts/build.py`. A change there is a change to all talks.

## How modes work

beamerswitch reads the jobname suffix: `-slides`, `-handout`, `-trans`,
`-article` pick beamer's mode. Any other suffix compiles in beamer mode, and
`yjtalk.sty` detects two more with `\IfEndWith*{\JobName}{...}`:

- `-dark`: the dark palette;
- `-notes`: `\setbeameroption{show notes on second screen=right}`;
- `-script`: switches to handout mode (`\gdef\beamer@currentmode{handout}`) so
  overlays collapse, defines `\beamerswitch@nup` so beamerswitch adds no page
  layout, then `\setbeameroption{show only notes}`;
- `-handout`: our pgfpages layout `yj handout` (3 frames down an A4 page) and
  `\yj@handoutdecor`, run from beamerswitch's per-page hook
  `\beamerswitch@footer`, which draws the header, frame borders, ruled note
  lines for filled slots only, and the page footer.

Section dividers come from `\AtBeginSection` and are excluded from the
handout, script and trans (`<handout:0|trans:0>`) so page counts still agree.

## Where a variant is declared

A new suffix is detected in `yjtalk.sty` next to `-notes` and `-script`, and
listed in:

- `VARIANTS` in `scripts/build.py`, with a one-line description, plus a
  page-count rule in `build_talk` if one holds;
- the Makefile's `VARIANTS`;
- the README outputs table;
- the mode notes in `talks/feature-gallery/talk.tex`, if they change.

## Theme rules

- Colours only through the working names (`yjBackground`, `yjAccent`, ...).
  Add or change a colour in `theme-tokens.json` for both `light` and `dark`,
  run `make tokens`, and check contrast: body text at least 4.5:1 and chart
  marks at least 3:1 against `background` in both modes.
- The dark variant only swaps the palette (`\yjusepalette{D}`); anything drawn
  with a named colour follows. Handouts always use the light palette
  (`yjL...` names) because they are printed.
- Fonts: Palatino for text and maths (`mathpazo`), from
  texlive-fonts-recommended. A new font must be in a Debian package CI
  installs.
- Keep `\mode<presentation>{}` for slide templates and `\mode<article>{}` for
  article layout; an unguarded beamer command breaks the article.
- Keep the determinism block (`\pdftrailerid{}`, `\pdfinfoomitdate`,
  `\pdfsuppressptexinfo`) first. Removing it makes `--check` fail.

## Scripts and their tests

`scripts/*.py` are stdlib-only Python 3.12 and have unit tests in `tests/`,
one file per script (`tests/test_build.py` for `scripts/build.py`). The tests
cover what runs without TeX: the talk lint, token rendering, the scaffold,
TeX-to-text and frame parsing, notes and timing maths, and the skills check.
A behaviour change to a script comes with a test that fails without it.
`tests/conftest.py` puts `scripts/` on the import path and provides
`make_talk`, which writes a minimal talk into a temp directory.

Test cost stays flat: tests run without TeX, network or Manim, and the whole
`make test` suite takes well under a second. Time `make test` before and after
adding a test and quote both; a test that needs a build belongs in
`make check` or CI's build job, not in `tests/`.

## Shared runtimes

`web/shell.html` (web deck) and `manim/talkscene.py` (video) serve every talk.
`talkscene.py` keeps generate-explainer-video's timing API (`begin`, `at`,
`finish`, `hold_until`, `budget`) and its `timings.json` format; do not
diverge from them. It imports Manim, so ruff lints it but tests do not import
it.
