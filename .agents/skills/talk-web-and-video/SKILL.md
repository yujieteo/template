---
name: talk-web-and-video
description: Turn a talk into its interactive web deck or its narrated Manim video, write the \narration those need, add a native Manim animation for one frame, and verify both.
---

# Web deck and video

Both converters start from `scripts/talk_manifest.py`, which reads `talk.tex`
(titles, sections, `\note`, `\narration`, `\yjsource`, `label=`) and matches
frames to page ranges from `build/talk-slides.nav`. Build the slides first:
`python3 scripts/build.py --only slides,dark <slug>`.

## Web deck

`python3 scripts/to_web.py <slug>` writes `talks/<slug>/build/web/` and checks
it (placeholders, external dependencies, one SVG per page per theme, notes in
slide order, size). Then look at it:

1. `python3 -m http.server -d talks/<slug>/build/web` and open it in a browser
   at 1280x800 and at a phone width.
2. Step with `→` through a frame with overlays; press `T`, `O`, `/` with a
   word from a slide, `C`, `D`; load `#5`; open `P` and confirm the presenter
   window follows and shows notes.
3. `await Talk.audit()` must return `[]`; the console must have no errors.

Change behaviour in `web/shell.html` (every talk shares it), never in a
generated `index.html`. Keep it dependency-free and keep notes out of the
WebMCP tools.

## Narration

`\narration{...}` inside a frame is what the video says; it prints nowhere.
Write for the ear: short sentences, one idea each, numbers through the talk's
macros (`\blPzero`), initialisms spelled as spoken. One sentence per overlay
step: step k appears on sentence k. About 130 words a minute; a frame of 20-40
words is 10-20 seconds. Section dividers say "Part N. Title." on their own;
a frame without narration speaks only its title (the script prints which).

## Video

`python3 scripts/to_manim.py <slug> [--quality l|m|h] [--theme dark|light]`
writes `talks/<slug>/build/video/`, renders, and checks the runtime against
the timeline, then saves one review frame per scene in `frames/`. Open every
frame: slide readable, caption below the slide not over it, the frame's last
step shown by its last sentence.

- Silent draft: with no `narration.wav`, timings are estimated.
- Narrated: run generate-explainer-video's `synthesize.py` on
  `build/video/script.json` (its `--out` defaults to that folder; pass
  `--target-seconds` near the estimate and a wide `--tolerance`), then rerun
  `to_manim.py`. It keeps Kokoro's timings only while they match the script;
  edit narration, and it falls back to the estimate until you resynthesize.
- Install: `pip install -r manim/requirements.txt` in a venv, ffmpeg with
  libass, Cairo, Pango, `fonts-urw-base35`. Pass `--python <venv>/bin/python`
  or set `MANIM_PYTHON`.

## Native frame animation

`talks/<slug>/manim/<label>.py` (the frame's `label=`, else its id) defines
`animate(scene, frame)` and replaces that frame's slide images. It runs inside
the frame's window: use `scene.swap_to(group)` first, `scene.at(sentence,
fraction)` to place beats, `scene.budget(t)` to cap run times, and `text()`,
`PALETTE`, `SLIDE_SCALE` from `talkscene`. Read numbers from the talk's
generated data, never type them. Copy `talks/breeden-litzenberger/manim/density.py`.
