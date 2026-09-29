---
name: talk-template-maintenance
description: Change the shared template: the yjtalk.sty theme and modes, the starter talk, the build script, or add an output variant, without breaking any existing talk.
---

# Template maintenance

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

## Add a variant

1. Pick a suffix; detect it in `yjtalk.sty` next to `-notes` and `-script`.
2. Add it to `VARIANTS` in `scripts/build.py` with a one-line description,
   and a page-count rule in `build_talk` if one holds.
3. Add it to the Makefile's `VARIANTS`, the README outputs table, and the
   mode notes in `talks/feature-gallery/talk.tex` if they change.
4. `make check`.

## Change the theme

- Colours only through the working names (`yjBackground`, `yjAccent`, ...).
  Add or change a colour in `theme-tokens.json` for both `light` and `dark`,
  run `make tokens`, and check contrast: body text at least 4.5:1 and chart
  marks at least 3:1 against `background` in both modes.
- The dark variant only swaps the palette (`\yjusepalette{D}`); anything drawn
  with a named colour follows. Handouts always use the light palette
  (`yjL...` names) because they are printed.
- Fonts: Palatino for text and maths (`mathpazo`), from
  texlive-fonts-recommended. A new font must be in a Debian package CI installs.
- Keep `\mode<presentation>{}` for slide templates and `\mode<article>{}` for
  article layout; an unguarded beamer command breaks the article.
- Keep the determinism block (`\pdftrailerid{}`, `\pdfinfoomitdate`,
  `\pdfsuppressptexinfo`) first. Removing it makes `--check` fail.

## Verify a template change

1. `make check` for all talks: both examples must pass unchanged.
2. Render and look at one page per variant of both examples
   (`pdftoppm -r 50 -png`), especially notes and script pages.
3. Scaffold and build a throwaway talk to test the starter:
   `python3 scripts/new_talk.py zz-smoke && python3 scripts/build.py --check zz-smoke && rm -r talks/zz-smoke`.
4. Negative test for any new check: break a copy of a talk the way the check
   targets and confirm the build fails with the intended message.

## Shared runtimes

`web/shell.html` (web deck) and `manim/talkscene.py` (video) serve every talk.
After changing either, rebuild both examples with `to_web.py` and
`to_manim.py`, drive the web deck in a browser (see talk-web-and-video), and
look at the video's review frames. `talkscene.py` keeps
generate-explainer-video's timing API (`begin`, `at`, `finish`, `hold_until`,
`budget`) and its `timings.json` format; do not diverge from them.

