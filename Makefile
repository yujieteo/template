# Thin wrapper over scripts/build.py. TALK=<slug> limits to one talk.
#   make                    all talks, all seven variants
#   make check              same, plus lint, generated-data and reproducibility checks
#   make slides TALK=x      one variant (also: dark notes script handout trans article)
#   make new SLUG=x TITLE="..."   scaffold talks/x/talk.tex from starter/
#   make watch TALK=x       recompile the slides on every save
#   make present TALK=x     open the notes build in pdfpc (presenter + audience screens)
#   make web TALK=x         interactive web deck in talks/x/build/web (serve it over HTTP)
#   make video TALK=x [Q=m] narrated Manim video in talks/x/build/video (needs manim, ffmpeg)
#   make tokens             regenerate tex/yjtokens.tex from theme-tokens.json
#   make decks              web deck and video inputs for every talk (after make check)
#   make lint test          ruff, markdownlint, skills check, pytest; no TeX
#                           (tools: .venv from requirements-dev.txt, and Node for npx)
#   make ci                 everything CI runs: lint, test, check, decks
# The venv from requirements-dev.txt if there is one, so make lint test finds ruff and pytest.
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
TALK ?=
VARIANTS := slides dark notes script handout trans article
SLUGS = $(or $(TALK),$(patsubst talks/%/talk.tex,%,$(wildcard talks/*/talk.tex)))
MARKDOWNLINT ?= npx --yes markdownlint-cli2@0.23.3

.PHONY: all check $(VARIANTS) new watch present web video decks tokens clean \
	lint lint-py lint-md lint-skills test ci

all:
	$(PY) scripts/build.py $(TALK)

check:
	$(PY) scripts/build.py --check $(TALK)

$(VARIANTS):
	$(PY) scripts/build.py --only $@ $(TALK)

new:
	$(PY) scripts/new_talk.py $(SLUG) $(if $(TITLE),--title "$(TITLE)")

watch:
	@test -n "$(TALK)" || (echo "usage: make watch TALK=<slug>"; exit 2)
	cd talks/$(TALK) && TEXINPUTS=$(CURDIR)/tex//: latexmk -pdf -pvc -no-shell-escape \
	  -interaction=nonstopmode -outdir=build -jobname=talk-slides talk.tex

present:
	@test -n "$(TALK)" || (echo "usage: make present TALK=<slug>"; exit 2)
	pdfpc --notes=right talks/$(TALK)/build/talk-notes.pdf

web:
	@test -n "$(TALK)" || (echo "usage: make web TALK=<slug>"; exit 2)
	$(PY) scripts/build.py --only slides,dark $(TALK)
	$(PY) scripts/to_web.py $(TALK)

video:
	@test -n "$(TALK)" || (echo "usage: make video TALK=<slug> [Q=l|m|h]"; exit 2)
	$(PY) scripts/build.py --only slides,dark $(TALK)
	$(PY) scripts/to_manim.py $(TALK) --quality $(or $(Q),l)

# Needs the slides built; renders no video.
decks:
	set -e; for slug in $(SLUGS); do \
	  $(PY) scripts/to_web.py $$slug; \
	  $(PY) scripts/to_manim.py $$slug --prepare-only; \
	done

tokens:
	$(PY) scripts/sync_tokens.py

lint: lint-py lint-md lint-skills

lint-py:
	$(PY) -m ruff check .

lint-md:
	$(MARKDOWNLINT)

lint-skills:
	$(PY) scripts/check_skills.py

test:
	$(PY) -m pytest

# In order: decks needs check's PDFs, even under make -j.
ci:
	$(MAKE) lint test
	$(MAKE) check
	$(MAKE) decks

clean:
	rm -rf talks/*/build
