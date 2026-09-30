import re

import to_web


def test_shade_darkens_below_one_and_lightens_above():
    assert to_web.shade("#808080", 0.5) == "#404040"
    assert to_web.shade("#000000", 1.5) == "#808080"
    assert to_web.shade("#123456", 1) == "#123456"


def test_theme_css_sets_light_and_dark_variables():
    palette = {"background": "#FFFFFF", "surface": "#EEEEEE", "foreground": "#111111", "secondary": "#555555",
               "border": "#CCCCCC", "accent": "#1F3A5F", "accent_text": "#FFFFFF"}
    css = to_web.theme_css({"light": palette, "dark": dict(palette, background="#101820")})
    light, dark = css.splitlines()
    assert light.startswith(":root{--bg:#FFFFFF;") and "--chrome:#EEEEEE" in light
    assert dark.startswith(":root[data-theme=dark]{--bg:#101820;")
    assert "--chrome:#0B1116" in dark  # background darkened to 70%


def test_seconds_for_budgets_130_words_a_minute_plus_a_pause():
    assert to_web.seconds_for("") == 3
    assert to_web.seconds_for(" ".join(["word"] * 130)) == 62


def test_mmss_and_sentences():
    assert to_web.mmss(75) == "1:15"
    assert to_web.sentences("One. Two? Three!  ") == ["One.", "Two?", "Three!"]


def manifest(*frames):
    return {"title": "Prices imply a density", "subtitle": "", "frames": list(frames)}


def frame(fid, notes, kind="frame", narration="", **extra):
    return {"id": fid, "kind": kind, "title": fid, "notes": notes, "narration": narration, **extra}


def test_notes_markdown_splits_a_note_into_coach_fields():
    note = ("Stress the spot. Point at the curve. Likely question: Why synthetic? "
            "Answer: To isolate the method. Transition: What do prices imply?")
    md = to_web.notes_markdown(manifest(frame("s01-spot", [note], narration="Four words said here.")))
    assert "**Emphasise:** Stress the spot." in md
    assert "**Say:** Point at the curve." in md
    assert "**Transition:** What do prices imply?" in md
    assert "- Why synthetic? To isolate the method." in md
    assert "**Time:** 0:04" in md


def test_notes_markdown_has_one_section_per_frame_in_order():
    md = to_web.notes_markdown(manifest(
        frame("s01-title", ["Open."], kind="title"),
        frame("s02-section-question", [], kind="section", section_number=1),
        frame("s03-cues", ["First cue.", "Second cue."]),
    ))
    assert re.findall(r"^## (\S+)$", md, re.M) == ["deck", "s01-title", "s02-section-question", "s03-cues"]
    assert "**Say:** Section 1: s02-section-question." in md
    assert "**Cues:**\n- First cue.\n- Second cue." in md
