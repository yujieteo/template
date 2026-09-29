# Thin wrapper over scripts/build.py. TALK=<slug> limits to one talk.
#   make                    all talks, all seven variants
#   make check              same, plus lint, generated-data and reproducibility checks
#   make slides TALK=x      one variant (also: dark notes script handout trans article)
#   make new SLUG=x TITLE="..."   scaffold talks/x/talk.tex from starter/
#   make watch TALK=x       recompile the slides on every save
#   make present TALK=x     open the notes build in pdfpc (presenter + audience screens)
#   make tokens             regenerate tex/yjtokens.tex from theme-tokens.json
PY ?= python3
TALK ?=
VARIANTS := slides dark notes script handout trans article

.PHONY: all check $(VARIANTS) new watch present tokens clean

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

tokens:
	$(PY) scripts/sync_tokens.py

clean:
	rm -rf talks/*/build
