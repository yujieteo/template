# Data from visuals

**Every number on a slide is generated.** Detail:
[talk-data-from-visuals](../skills/talk-data-from-visuals/SKILL.md).

1. Find the story in visuals: the data under `data/<viz-slug>/` and the
   builder that verifies it.
2. Snapshot `raw.*` and `meta.json` into `talks/<slug>/data/`, trimmed if
   large.
3. Write `talks/<slug>/derive.py` to the contract, starting from a copy of
   `talks/breeden-litzenberger/derive.py`. Refreshing an existing talk
   instead: `python3 talks/<slug>/derive.py --sync ../visuals`.
4. `python3 talks/<slug>/derive.py`, then read the diff of `data/`.
5. Wire the CSVs and `numbers.tex` into `talk.tex`, with `\yjsource{...}` on
   every chart frame.
6. If a headline number moved, re-read every frame and note that says it: the
   macro updates the number, not the claim.
7. `make check TALK=<slug>`, then look at every chart frame in
   `talk-slides.pdf` and `talk-dark.pdf`.

**Reply:** the visuals source and snapshot date, the numbers the talk now
states and any that moved, assumptions not in the visuals data, and the
`make check TALK=<slug>` result.
