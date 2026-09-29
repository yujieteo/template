# SKILLS.md

Router for agents working in this repo: one-source beamer talks built with
beamerswitch. Each `talks/<slug>/talk.tex` builds seven PDFs (slides light
and dark, notes, script, handout, trans, article) reproducibly. Layout and commands: `README.md`.

## Always

- One talk, one `talk.tex`. Never split a talk into per-output files; use modes
  (`<handout:0>`, `\only<article>`, `\mode<article>{}`) instead.
- Never hand-edit generated files: `tex/yjtokens.tex`, `talks/*/data/*.csv`,
  `talks/*/data/numbers.tex`. Change the input, then regenerate.
- Never type a number that a derive script can produce.
- `talks/*/build/` is output; do not commit it.
- Finish every change with `make check` (or `make check TALK=<slug>`) passing.
- Do not edit the visuals repo from here, push, or publish unless asked.

## Playbook: load one sub-skill by task

| Task | Load |
| --- | --- |
| Start a talk, write or restructure frames, write presenter notes | `.agents/skills/talk-new-talk/SKILL.md` |
| Build, verify, fix a failing check or CI, prove reproducibility | `.agents/skills/talk-build-verify/SKILL.md` |
| Chart data or numbers from the visuals repo, refresh a snapshot | `.agents/skills/talk-data-from-visuals/SKILL.md` |
| Change the theme or colours, `yjtalk.sty`, the starter, or add an output variant | `.agents/skills/talk-template-maintenance/SKILL.md` |

Quick check for any change: `python3 scripts/build.py --check`
