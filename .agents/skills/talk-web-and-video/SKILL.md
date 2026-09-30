---
name: talk-web-and-video
description: How a talk becomes its interactive web deck and its narrated Manim video, including writing the narration macro, native Manim frames, and what to check in each. Use when building or checking a web deck or video, writing narration, or animating one frame in Manim.
---

# Web deck and video

Playbook: [web-and-video](../../playbooks/web-and-video.md).

Both converters start from `scripts/talk_manifest.py`, which reads `talk.tex`
(titles, sections, `\note`, `\narration`, `\yjsource`, `label=`) and matches
frames to page ranges from `build/talk-slides.nav`. Build the slides first:
`python3 scripts/build.py --only slides,dark <slug>`.

## Web deck

`python3 scripts/to_web.py <slug>` writes `talks/<slug>/build/web/` and checks
it (placeholders, external dependencies, one SVG per page per theme, notes in
slide order, size). Then drive it in a browser:

- Serve it: `python3 -m http.server -d talks/<slug>/build/web`. Open it at
  1280x800 and at a phone width.
- Step with `→` through a frame with overlays; press `T`, `O`, `/` with a
  word from a slide, `C`, `D`; load `#5`; open `P` and confirm the presenter
  window follows and shows notes.
- `await Talk.audit()` returns `[]`, and the console has no errors.

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
writes `talks/<slug>/build/video/`, renders, checks the runtime against the
timeline, then saves one review frame per scene in `frames/`. In each review
frame: the slide is readable, the caption sits below the slide and not over
it, and the frame's last step shows by its last sentence.

- Silent draft: with no `narration.wav`, timings are estimated.
- Voice: British English `bf_emma` by default (`--voice bm_george`, or
  `af_heart` for American). Kokoro reads the language from the id's first
  letter, so write British spelling in `\narration` for a `b` voice.
- Narrated: run generate-explainer-video's `synthesize.py` on
  `build/video/script.json` (its `--out` defaults to that folder; pass
  `--target-seconds` near the estimate and a wide `--tolerance`), then rerun
  `to_manim.py`. It keeps Kokoro's timings only while they match the script
  and its voice; change either, and it falls back to the estimate until you
  resynthesize.
- Install: `pip install -r manim/requirements.txt` in a venv, ffmpeg with
  libass, Cairo, Pango, `fonts-urw-base35`. Pass `--python <venv>/bin/python`
  or set `MANIM_PYTHON`.
- CI builds only the inputs (`to_manim.py <slug> --prepare-only`); rendering
  runs locally.

## Native frame animation

`talks/<slug>/manim/<label>.py` (the frame's `label=`, else its id) defines
`animate(scene, frame)` and replaces that frame's slide images. It runs inside
the frame's window: use `scene.swap_to(group)` first, `scene.at(sentence,
fraction)` to place beats, `scene.budget(t)` to cap run times, and `text()`,
`PALETTE`, `SLIDE_SCALE` from `talkscene`. Read numbers from the talk's
generated data, never type them. Copy
`talks/breeden-litzenberger/manim/density.py`.
