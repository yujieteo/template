# SKILLS.md

Router for agents working in this repo: one-source beamer talks built with
beamerswitch. Each `talks/<slug>/talk.tex` builds seven PDFs (slides light
and dark, notes, script, handout, trans, article) reproducibly. Layout and
commands: [README.md](README.md).

## How to work here

1. Match the task to a playbook in the table below and open it.
2. Copy its numbered steps into your todo list verbatim, before any
   task-specific items. A step you choose not to do stays in the list as
   `skip: <reason>`.
3. A step names the skill that holds the detail. Read that skill in full when
   you reach the step; playbooks give the order of work, skills the reference.
4. Finish with the gates for what you changed, then write the playbook's
   **Reply**.

No playbook fits: follow the Always rules and the principles, load the skills
whose "Use when" matches, and finish with the gates.

## Always

- One talk, one `talk.tex`. Never split a talk into per-output files; use modes
  (`<handout:0>`, `\only<article>`, `\mode<article>{}`) instead.
- Never hand-edit generated files: `tex/yjtokens.tex`, `talks/*/data/*.csv`,
  `talks/*/data/numbers.tex`, anything in `talks/*/build/` (web deck, video
  script, `notes.md`). Change the input, then regenerate.
- Never type a number that a derive script can produce.
- `talks/*/build/` is output; do not commit it.
- Finish every change with its gates passing (below).
- Do not edit the visuals repo from here, push, or publish unless asked.

## Principles

- **Fix the source, never the check.** A lint error, page-count mismatch or
  hash difference is a finding about the talk or the template. Loosening
  `scripts/build.py`, a test or a lint rule to get green is never the fix.
- **Prove it on the real output.** "It compiled" is a proxy. Look at the
  rendered pages (`pdftoppm -r 50 -png`), the web deck in a browser, the
  video's review frames. Quote the command output you relied on.
- **A template change is a change to every talk.** `tex/`, `starter/`,
  `scripts/`, `web/shell.html` and `manim/talkscene.py` serve every talk;
  verify both example talks, not only the one you had in mind.
- **Encode a repeated lesson as a check.** When you write the same instruction
  a second time, make it a lint in `scripts/build.py`, a test in `tests/`, or a
  rule in `scripts/check_skills.py` instead of more prose.

## Playbooks

| Task | Playbook |
| --- | --- |
| Start a talk; write, restructure or re-note frames | [new-talk](.agents/playbooks/new-talk.md) |
| A failing build, lint, test or CI job | [fix-build](.agents/playbooks/fix-build.md) |
| Chart data or numbers from the visuals repo; refresh a snapshot | [data-from-visuals](.agents/playbooks/data-from-visuals.md) |
| Web deck or narrated video; `\narration`; a native Manim frame | [web-and-video](.agents/playbooks/web-and-video.md) |
| Theme, colours, `yjtalk.sty`, starter, scripts, shared runtimes, a new variant | [template-change](.agents/playbooks/template-change.md) |
| Add or change a skill, a playbook or this router | [skill-change](.agents/playbooks/skill-change.md) |

## Skills

| Skill | Holds |
| --- | --- |
| [talk-new-talk](.agents/skills/talk-new-talk/SKILL.md) | Scaffolding, storyboard, gallery frame patterns, presenter notes |
| [talk-build-verify](.agents/skills/talk-build-verify/SKILL.md) | Build and check commands, the failure table, CI |
| [talk-data-from-visuals](.agents/skills/talk-data-from-visuals/SKILL.md) | The snapshot and `derive.py` contract, chart colours |
| [talk-web-and-video](.agents/skills/talk-web-and-video/SKILL.md) | Web deck checks, narration, video, native Manim frames |
| [talk-template-maintenance](.agents/skills/talk-template-maintenance/SKILL.md) | How modes work, theme rules, variants, shared runtimes |

## Gates

| Changed | Run |
| --- | --- |
| Anything | `make lint test`: ruff, markdownlint, the skills check, pytest. No TeX needed. |
| A talk | `make check TALK=<slug>` |
| `tex/`, `starter/`, `theme-tokens.json`, `scripts/` | `make check` (every talk) |
| `web/shell.html`, `manim/`, `scripts/to_web.py`, `scripts/to_manim.py` | Also rebuild and look at the web deck or video ([talk-web-and-video](.agents/skills/talk-web-and-video/SKILL.md)) |

`make ci` runs everything CI runs: the lint and test jobs, then `make check`.

## Reply

Every playbook ends with a reply to whoever asked. Say what changed and for
whom (the audience of the talk, or the next person editing the template), then
the evidence: each gate you ran with its pass or fail line, and what you
looked at. Label anything you did not verify. Name the files a reviewer should
read first. Each playbook's **Reply** line adds what is specific to it.
