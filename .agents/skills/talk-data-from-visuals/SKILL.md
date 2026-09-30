---
name: talk-data-from-visuals
description: The contract for data in a talk, covering the snapshot of the sibling visuals repo, derive.py, the generated CSV and numbers.tex, and chart colours. Use when a talk needs chart data or numbers from visuals, when refreshing a snapshot, or when a derive.py --verify check fails.
---

# Data from visuals

Playbook: [data-from-visuals](../../playbooks/data-from-visuals.md).

Talks never read the visuals repo at build time. They keep a snapshot, and a
script derives everything the slides show. The pattern is
`talks/breeden-litzenberger/derive.py`; copy it.

## Where the data comes from

In visuals: `data/<viz-slug>/raw.*` and `meta.json` hold the data, and the
builder `scripts/build_<viz>.py` holds the maths it already verifies.

## Snapshot

`raw.*` and `meta.json` are copied into `talks/<slug>/data/`. Keep raw files
small; if raw is large, derive from it once and snapshot a trimmed file plus a
note in `derive.py` saying how it was trimmed.

## derive.py contract

`talks/<slug>/derive.py` takes `--sync VISUALS_DIR` (refresh the snapshot) and
`--verify` (recompute, fail if a committed output is stale, write nothing;
the build runs it). It is:

- stdlib only, and deterministic: fixed row order, fixed decimals, no clock;
- the only writer of `data/*.csv` for charts and of `data/numbers.tex`, a
  `\newcommand` for every number a slide or note says;
- a re-assertion of the terminal values the visuals builder asserts, so drift
  fails;
- explicit about any assumption that is not in the visuals data (the example's
  quote error `EPSILON`), which the slide also states.

Macro names in `numbers.tex` are letters only (`\blPzero`, not `\bl_p0`).
Prefix them per talk.

## Wiring into talk.tex

`\input{data/numbers.tex}`, `\pgfplotstableread[col sep=comma]{data/x.csv}\x`,
and `\yjsource{...}` naming the data and whether it is synthetic.

## Colours in charts

Use the theme's names, never hex values: `yjForeground`, `yjAccent` (navy,
the one thing to look at), `yjWarm`, `yjGreen`, `yjSecondary` for labels,
`yjBorder` for reference bands. The `yj` pgfplots style cycles series in that
order. Named colours switch automatically in the dark variant.
