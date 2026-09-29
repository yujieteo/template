---
name: talk-data-from-visuals
description: Bring data or numbers from the sibling visuals repo into a talk: snapshot the source, write derive.py, emit CSV and numbers.tex, and keep them verifiable.
---

# Data from visuals

Talks never read the visuals repo at build time. They keep a snapshot, and a
script derives everything the slides show. The pattern is
`talks/breeden-litzenberger/derive.py`; copy it.

## Add data to a talk

1. Find the story in visuals: `data/<viz-slug>/raw.*` and `meta.json`, and the
   builder `scripts/build_<viz>.py` for the maths it already verifies.
2. Snapshot: copy `raw.*` and `meta.json` into `talks/<slug>/data/`. Keep
   raw files small; if raw is large, derive from it once and snapshot a trimmed
   file plus a note in `derive.py` saying how it was trimmed.
3. Write `talks/<slug>/derive.py` with `--sync VISUALS_DIR` and `--verify`:
   - stdlib only; deterministic (fixed row order, fixed decimals, no clock);
   - emit `data/*.csv` for charts and `data/numbers.tex` of `\newcommand`s for
     every number a slide or note says;
   - re-assert the terminal values the visuals builder asserts, so drift fails;
   - label any assumption that is not in the visuals data (the example's quote
     error `EPSILON`) and say it on the slide.
4. In `talk.tex`: `\input{data/numbers.tex}`, `\pgfplotstableread[col sep=comma]{data/x.csv}\x`,
   and `\yjsource{...}` naming the data and whether it is synthetic.
5. `python3 talks/<slug>/derive.py`, then `make check TALK=<slug>`.

Macro names in `numbers.tex` are letters only (`\blPzero`, not `\bl_p0`).
Prefix them per talk.

## Refresh

`python3 talks/<slug>/derive.py --sync ../visuals && python3 talks/<slug>/derive.py`,
then read the diff of `data/`. If a headline number moved, re-read every
frame and note that says it; the macro updates the number, not the claim.

## Colours in charts

Use the theme's names, never hex values: `yjForeground`, `yjAccent` (navy,
the one thing to look at), `yjWarm`, `yjGreen`, `yjSecondary` for labels,
`yjBorder` for reference bands. The `yj` pgfplots style cycles series in that
order. Named colours switch automatically in the dark variant.
