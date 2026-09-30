# Web deck and video

**Check the output in the medium it is for.** Detail:
[talk-web-and-video](../skills/talk-web-and-video/SKILL.md).

1. Build the slides: `python3 scripts/build.py --only slides,dark <slug>`.
2. Web deck: `python3 scripts/to_web.py <slug>`, then serve it and drive it
   in a browser at desktop and phone widths, through the keys the skill
   lists. `await Talk.audit()` returns `[]`; the console has no errors.
3. Narration: write `\narration{...}` for every frame the video should say
   more than its title for, one sentence per overlay step.
4. Native frame, if asked: `talks/<slug>/manim/<label>.py`, from a copy of
   `talks/breeden-litzenberger/manim/density.py`.
5. Video: `python3 scripts/to_manim.py <slug>` for a silent draft, then
   synthesize narration and rerun for the voiced cut.
6. Open every review frame in `talks/<slug>/build/video/frames/`.
7. `make check TALK=<slug>` and `make lint test`.

**Reply:** what was built and where, the web checks you drove, the video's
length and voice (or "silent draft"), and every review frame you flagged.
