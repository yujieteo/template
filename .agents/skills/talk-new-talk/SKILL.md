---
name: talk-new-talk
description: Start a talk or edit one: scaffold talks/<slug>/talk.tex, storyboard frames, pick techniques from the feature gallery, and write a presenter note for every frame.
---

# New talk or talk edit

## Scaffold

`make new SLUG=<kebab-slug> TITLE="<claim as a sentence>"`. It writes the date
once; keep it hand-written after that. If `talks/<slug>/` exists, you are
editing: keep frame order and labels unless told otherwise.

## Storyboard before LaTeX

1. One disputable sentence the talk proves. It becomes `\subtitle` or the last frame.
2. Arc: question, mechanism, evidence, a turn where it gets complicated, what
   to remember. About one frame per minute.
3. Each frame title states its finding as a full sentence.
4. Mark which frames need data; those go through
   `.agents/skills/talk-data-from-visuals/SKILL.md` first.

## Write frames

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

Data charts: follow `talks/breeden-litzenberger/talk.tex` (`\pgfplotstableread`
from `data/*.csv`, `\yjsource{...}` on every chart frame).

Article: put the argument in full sentences between frames; readers of
`talk-article.pdf` see it, the room does not.

## Presenter notes

Every frame gets `\note{...}` (the build fails otherwise). Write cues, not a
script, under about 80 words:

- first sentence: the one thing to stress;
- what to point at on chart frames;
- time only if the frame is unusually long;
- a transition that names the next frame's question;
- likely question and a one-line answer where the frame invites one.

Use `\note[item]{...}` for bullet cues. Ground every fact in the frame or its
data; mark anything unchecked with `verify:`. The `presentation-coach` skill
gives the same rules in more depth; its output goes into `\note{}`, not a
separate `notes.md`.

## Done when

`make check TALK=<slug>` passes, and you have looked at `talk-slides.pdf` and
`talk-script.pdf` page by page (render with `pdftoppm -r 50 -png`): titles fit
on two lines, nothing clipped, each note matches its frame.
