import json

import pytest

import sync_tokens


def tokens(light=None, dark=None):
    return {"light": light or {"background": "#FFFFFF", "accent_text": "#123456"},
            "dark": dark or {"background": "#000000", "accent_text": "#abcdef"}}


def test_tex_name_camel_cases_snake_keys():
    assert sync_tokens.tex_name("accent_text") == "AccentText"


def test_render_defines_both_palettes_and_the_switch():
    text = sync_tokens.render(tokens())
    assert "\\definecolor{yjLBackground}{HTML}{FFFFFF}" in text
    assert "\\definecolor{yjDAccentText}{HTML}{ABCDEF}" in text
    assert "  \\colorlet{yjAccentText}{yj#1AccentText}%" in text


def test_render_rejects_palettes_with_different_keys():
    with pytest.raises(SystemExit, match="same keys"):
        sync_tokens.render(tokens(dark={"background": "#000000"}))


def test_render_rejects_a_colour_that_is_not_rrggbb():
    with pytest.raises(SystemExit, match="not a #RRGGBB"):
        sync_tokens.render(tokens(light={"background": "white", "accent_text": "#123456"}))


def test_committed_tokens_file_is_current():
    assert sync_tokens.OUT.read_text() == sync_tokens.render(json.loads(sync_tokens.TOKENS.read_text()))
