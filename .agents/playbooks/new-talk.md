# New talk or talk edit

**You own the argument, not only the LaTeX.** Detail:
[talk-new-talk](../skills/talk-new-talk/SKILL.md).

1. New talk: `make new SLUG=<kebab-slug> TITLE="<claim as a sentence>"`.
   Existing talk: read the whole `talk.tex` first, and keep frame order and
   labels unless told otherwise.
2. Storyboard before LaTeX: the one disputable sentence, the arc, a finding
   as each frame title. List the frames that need data.
3. Data frames: run [data-from-visuals](data-from-visuals.md) for them now, so
   the frames read generated numbers from the start.
4. Write frames by copying the matching `talks/feature-gallery/talk.tex`
   pattern. Article prose goes between frames.
5. Write a `\note{...}` for every frame as you go, following the presenter
   notes rules. Add `\narration{...}` if the talk will become a video
   ([web-and-video](web-and-video.md)).
6. `make check TALK=<slug>`. On failure, run [fix-build](fix-build.md).
7. Render and look at `talk-slides.pdf` and `talk-script.pdf` page by page
   (`pdftoppm -r 50 -png`): titles fit on two lines, nothing is clipped, each
   note matches its frame.
8. `make lint test`.

**Reply:** the claim the talk proves, the frame count and arc in one line
each, which frames draw on data, the `make check TALK=<slug>` result with page
counts, and any note marked `verify:` that still needs a fact checked.
