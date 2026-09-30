---
name: talk-new-talk
description: How a talk is written here, from scaffold and storyboard to gallery frame patterns and one presenter note per frame. Use when starting a talk, or writing, restructuring or re-noting frames in an existing talks/SLUG/talk.tex.
---

# New talk or talk edit

Playbook: [new-talk](../../playbooks/new-talk.md).

## Scaffold

`make new SLUG=<kebab-slug> TITLE="<claim as a sentence>"` copies
`starter/talk.tex` into `talks/<slug>/talk.tex`. It writes the date once; keep
it hand-written after that. It refuses an existing slug: if `talks/<slug>/`
exists you are editing, so keep frame order and labels unless told otherwise.

## Storyboard

- One disputable sentence the talk proves. It becomes `\subtitle` or the last
  frame.
- Arc: question, mechanism, evidence, a turn where it gets complicated, what
  to remember. About one frame per minute.
- Each frame title states its finding as a full sentence.
- Frames that need data go through
  [talk-data-from-visuals](../talk-data-from-visuals/SKILL.md) before LaTeX.

## Frame patterns

Copy the pattern from `talks/feature-gallery/talk.tex`; do not invent new
macros when a gallery frame does the job:

| Need | Gallery frame |
| --- | --- |
| Reveal list items / highlight | "Overlays reveal a frame step by step" |
| Derivation line by line | "`\pause` steps through a derivation" |
| Diagram built in steps | "TikZ diagrams build up..." (`visible on=<n->`) |
| Chart gaining series | "Charts add one series per step" |
| Definition / theorem / example | "Blocks mark..." |
| Figure beside text | "Columns put a figure..." |
| Table row by row | "Tables reveal one row at a time" |
| Code | "Code needs a fragile frame" (`[fragile]`, listing flush left) |
| Slides-only frame, hidden on paper | `\begin{frame}<handout:0\|trans:0>` |
| Backup slides | `\appendix` + `\hyperlink{label}{\beamerbutton{...}}` |

Data charts follow `talks/breeden-litzenberger/talk.tex`:
`\pgfplotstableread` from `data/*.csv`, and `\yjsource{...}` on every chart
frame.

Article: put the argument in full sentences between frames. Readers of
`talk-article.pdf` see it; the room does not.

## Presenter notes

Every frame gets `\note{...}`; the build fails otherwise. `% no-note` inside a
frame opts out, only for frames with nothing to say, such as a pure image.
Write cues, not a script, under about 80 words:

- first sentence: the one thing to stress;
- what to point at on chart frames;
- time only if the frame is unusually long;
- a transition that names the next frame's question;
- a likely question and a one-line answer where the frame invites one.

Use `\note[item]{...}` for bullet cues. Ground every fact in the frame or its
data; mark anything unchecked with `verify:`. The `presentation-coach` skill
gives the same rules in more depth; its output goes into `\note{}`, not a
separate `notes.md`.
