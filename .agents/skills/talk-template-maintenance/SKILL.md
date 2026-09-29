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

- `-notes`: `\setbeameroption{show notes on second screen=right}`;
- `-script`: switches to handout mode (`\gdef\beamer@currentmode{handout}`) so
  overlays collapse, defines `\beamerswitch@nup` so beamerswitch adds no page
  layout, then `\setbeameroption{show only notes}`.

## Add a variant

1. Pick a suffix; detect it in `yjtalk.sty` next to `-notes` and `-script`.
2. Add it to `VARIANTS` in `scripts/build.py` with a one-line description,
   and a page-count rule in `build_talk` if one holds.
3. Add it to the Makefile's `VARIANTS`, the README outputs table, and the
   mode notes in `talks/feature-gallery/talk.tex` if they change.
4. `make check`.

## Change the theme

- Colours only through `yjtokens.tex` names; new colours go into
  `design-tokens.json` upstream in visuals first, then `make tokens`.
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
