# One-source beamer talks

Write a talk once, in one `talk.tex`, and build every output from it: projector
slides in light and dark, slides with presenter notes, a printable script, an
audience handout, transparencies, and a written article. The build is deterministic: the same
source and TeX Live produce byte-identical PDFs, and CI proves it on every push.

It uses [beamerswitch](https://ctan.org/pkg/beamerswitch), which picks the
beamer mode from the jobname suffix, so one file compiles seven ways without
edits. The approach follows the style of [Ingo Blechschmidt's
talks](https://www.ingo-blechschmidt.eu/): slides, handout and article all come
from one source file. Chart data can come from the
[visuals](https://github.com/yujieteo/visuals) repo.

## Look

An editorial theme: ivory paper, ink text and a single navy accent, with
Palatino for both text and maths. Frame titles are large roman type under a
small-caps section kicker; sections open with a numbered divider slide; lists
use navy markers; blocks sit on a soft blue-grey tint. The dark variant swaps
the palette for navy paper with light text and a lighter blue accent; every named colour follows
it, so charts need no changes. Colours live in `theme-tokens.json` (both
palettes, same keys) and are checked for contrast; handouts always print in
the light palette.

## Quick start

```sh
sudo apt-get install texlive-latex-extra texlive-latex-recommended \
  texlive-fonts-recommended texlive-pictures latexmk cm-super
make check                                  # build and verify both example talks
make new SLUG=my-talk TITLE="My claim"      # scaffold talks/my-talk/talk.tex
make watch TALK=my-talk                     # recompile slides on save
make check TALK=my-talk                     # all seven outputs, verified
make present TALK=my-talk                   # present with pdfpc
```

Outputs land in `talks/<slug>/build/` (git-ignored), with a `SHA256SUMS`.

## Outputs

| File | Mode | For |
| --- | --- | --- |
| `talk-slides.pdf` | beamer | the projector, light; every overlay step is a page |
| `talk-dark.pdf` | beamer, dark palette | the projector in a dark room, or a dark-themed venue |
| `talk-notes.pdf` | beamer + notes on a second screen | presenting: `pdfpc --notes=right talk-notes.pdf` shows slides to the room, notes to you |
| `talk-script.pdf` | handout + notes only | a printed script: one page per frame, the slide beside its notes |
| `talk-handout.pdf` | handout | the audience: A4 with a running header, 3 frames down the left, ruled note lines beside each, page footer |
| `talk-trans.pdf` | trans | one page per frame, no overlays |
| `talk-article.pdf` | article | readers who were not there: styled title block, numbered sections, frames set as figures within the prose |

`slides`, `handout`, `trans` and `article` are beamerswitch's own suffixes.
`dark`, `notes` and `script` are added by `tex/yjtalk.sty`. Section divider
slides appear only in `slides`, `dark` and `notes`; `\yjsectionpagesfalse` in
the preamble turns them off.

## Writing a talk

A talk is `talks/<slug>/talk.tex` and whatever it reads (`data/`, `figures/`).
Start from `make new`, or copy a frame from the examples:

- [`talks/feature-gallery/talk.tex`](talks/feature-gallery/talk.tex) — one frame
  per technique: overlays, `\pause`, TikZ and pgfplots built up in steps,
  theorem blocks, columns with images, tables, code listings, multi-item notes,
  mode-specific content, slides-only frames, bibliography, appendix and
  backup-slide buttons. Copy from here for any complexity.
- [`talks/breeden-litzenberger/talk.tex`](talks/breeden-litzenberger/talk.tex) —
  a complete argued talk whose charts and numbers are derived from the
  visuals repo's `data/breeden-litzenberger-density/` by `derive.py`.

Rules the build enforces (`scripts/build.py` lints before compiling):

- `\documentclass[...]{beamerswitch}` then `\usepackage{yjtalk}`.
- Every frame has a `\note{...}` (or `% no-note` inside it). Add
  `\narration{...}` too if the talk will become a video.
- `\date{...}` is written by hand; `\today` is rejected.
- No shell escape and no beamerswitch `also=` option; the build runs the variants.
- No overfull boxes over 1 pt, undefined references, or missing glyphs in any variant.
- Variants agree: notes has as many pages as slides; script and trans one per
  frame; handout a third of that.

Conventions the build cannot check:

- Text between frames appears only in the article (`ignorenonframetext`).
  Wrap longer article-only material in `\mode<article>{...}`.
- Numbers on slides come from a generated `data/numbers.tex`, never typed.
- `<handout:0>` hides something from paper outputs; `\only<article>` shows it
  only to readers.
- `\yjsource{...}` puts a chart's source line in the footline.
- `\yjkey{...}` marks the one thing to remember, in the accent colour.

## Web deck and video

The same talk also becomes an interactive web page and a narrated video. Both
start from the built PDFs, so any frame the slides can show, they show.

```sh
make web TALK=my-talk            # talks/my-talk/build/web/
python3 -m http.server -d talks/my-talk/build/web
make video TALK=my-talk Q=m      # talks/my-talk/build/video/my-talk.mp4
```

**Web deck** (`scripts/to_web.py`, runtime in `web/shell.html`): every slide
page as SVG in light and dark, no external dependencies. Arrow keys and swipe
step through overlays; `O` overview, `/` search (titles, slide text,
transcript), `T` light or dark, `C` transcript, `D` the talk's CSV data with
download, `P` presenter window (notes, next slide, clock, kept in sync), `F`
fullscreen, `#n` deep links. Read-only WebMCP tools (`get_metadata`,
`get_slide`, `search_slides`, `get_data`) never expose notes. Speaker notes go
to `notes.md` in presentation-coach's format and load only over HTTP; publish
the folder without it to keep them private. Same PDFs, same bytes.

**Video** (`scripts/to_manim.py`, runtime in `manim/talkscene.py`): one scene
per frame, spoken from `\narration{...}` (invisible in every PDF; section
dividers say "Part N. Title."). Each frame fades in and each overlay step lands
on the next sentence; captions are burned in below the slide. It writes
generate-explainer-video's `script.json` with a British English Kokoro voice
(`bf_emma`; `--voice bm_george` for a male voice, `af_heart` for American), so
real narration is one step:

```sh
python <skills>/generate-explainer-video/scripts/synthesize.py \
  talks/my-talk/build/video/script.json --target-seconds <estimate> --tolerance 30
make video TALK=my-talk Q=m      # now muxes narration.wav
```

Without that step the timeline is estimated at 130 words a minute and the
video is silent, which is enough to check pacing. `talks/<slug>/manim/<label>.py`
replaces one frame with a native Manim animation: the Breeden–Litzenberger talk
draws its density curve and second differences from `data/curves.csv`
(`manim/density.py`). Rendering needs `pip install -r manim/requirements.txt`,
ffmpeg, Cairo, Pango and `fonts-urw-base35`; 480p takes about a minute.

## Data from visuals

A talk that charts data keeps a snapshot of its source and a derive script:

```
talks/<slug>/data/raw.json, meta.json   # copied from visuals/data/<viz-slug>/
talks/<slug>/derive.py                  # snapshot -> CSVs + numbers.tex
```

`python3 talks/<slug>/derive.py --sync ../visuals` refreshes the snapshot;
`derive.py` regenerates; `derive.py --verify` (run by the build) fails when
outputs are stale. Talks build without a visuals checkout.

Colours: edit `theme-tokens.json` (keep `light` and `dark` in step), then
`make tokens` regenerates `tex/yjtokens.tex`; the build fails if it is stale.
In charts use the working names `yjForeground`, `yjAccent`, `yjWarm`,
`yjGreen`, `yjSecondary`, `yjBorder`, never hex values.

## Reproducibility

`tex/yjtalk.sty` removes the PDF timestamps and trailer ID; the build pins
`SOURCE_DATE_EPOCH` (the talk directory's last commit time, or 0),
`FORCE_SOURCE_DATE=1`, `TZ=UTC` and `LC_ALL=C`. `make check` builds everything
twice in separate directories and fails if any byte differs. Hashes are stable
for a given TeX Live release; a different release may produce different bytes.

## Layout

```
talks/<slug>/talk.tex    the one source per talk
starter/talk.tex         template for make new
tex/yjtalk.sty           modes, theme, notes, handout layout, determinism
tex/yjtokens.tex         colours, generated from theme-tokens.json
theme-tokens.json        light and dark palettes
scripts/build.py         lint, compile, verify
scripts/new_talk.py      scaffold a talk
scripts/sync_tokens.py   theme-tokens.json -> tex/yjtokens.tex
scripts/talk_manifest.py talk.tex + beamer .nav -> frames, pages, notes, narration
scripts/to_web.py        interactive web deck
scripts/to_manim.py      narrated Manim video
web/shell.html           web deck runtime
manim/talkscene.py       video runtime (timing API of generate-explainer-video)
.agents/skills/          playbooks for agents working in this repo
```

Agents: start at [`SKILLS.md`](SKILLS.md).
