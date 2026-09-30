import pytest

import talk_manifest as tm
from conftest import FRAME, PREAMBLE


def test_strip_comments_keeps_escaped_percent():
    assert tm.strip_comments("5\\% rate % a comment\nnext") == "5\\% rate \nnext"


def test_read_group_returns_balanced_content_and_the_index_after_it():
    s = "{a {b} \\} c}rest"
    content, end = tm.read_group(s, 0)
    assert content == "a {b} \\} c"
    assert s[end:] == "rest"


def test_read_group_fails_on_an_unbalanced_group():
    with pytest.raises(SystemExit, match="unbalanced"):
        tm.read_group("{never closed", 0)


@pytest.mark.parametrize(
    ("tex", "text"),
    [
        ("\\emph{Prices} imply a \\textbf{density}", "Prices imply a density"),
        ("$\\frac{a}{b} = x^{2} + y_{ij}$", "(a)/(b) = x^2 + y_(ij)"),
        ("$\\alpha\\le\\sigma$", "α≤σ"),
        ("pages 3--5 --- ``quoted''", "pages 3–5 — “quoted”"),
        ("\\alert<2->{now} visible", "now visible"),
        ("5\\% of \\{a\\}", "5% of {a}"),
        ("\\textcolor{yjAccent}{navy}", "navy"),
    ],
)
def test_tex_to_text_reads_like_the_slide(tex, text):
    assert tm.tex_to_text(tex, {}) == text


def test_tex_to_text_marks_texttt_as_code_only_when_asked():
    assert tm.tex_to_text("run \\texttt{make}", {}) == "run make"
    assert tm.tex_to_text("run \\texttt{make}", {}, code=True) == "run `make`"


def test_tex_to_text_expands_zero_argument_macros_eating_the_space_like_tex():
    assert tm.tex_to_text("spot \\blSzero{} today", {"blSzero": "100"}) == "spot 100 today"
    assert tm.tex_to_text("spot \\blSzero today", {"blSzero": "100"}) == "spot 100today"


def test_slugify_keeps_the_first_words():
    assert tm.slugify("Prices imply a density, and more words here") == "prices-imply-a-density-and"
    assert tm.slugify("!!!") == "frame"


def test_read_macros_follows_input_files(make_talk):
    talk_dir = make_talk(files={"data/numbers.tex": "\\newcommand{\\blSzero}{100}\n"})
    macros = tm.read_macros("\\newcommand{\\here}{x}\n\\input{data/numbers}", talk_dir)
    assert macros == {"here": "x", "blSzero": "100"}


def test_parse_talk_reads_frames_sections_notes_and_narration(make_talk):
    body = (
        "\\begin{frame}[plain]\n  \\titlepage\n  \\note{Open.}\n\\end{frame}\n"
        "\\section{Question}\n"
        "\\begin{frame}[label=first]{Spot is \\blSzero}\n"
        "  \\note{Stress the spot.}\n  \\narration{Spot is \\blSzero. Next.}\n"
        "  \\yjsource{Synthetic data}\n\\end{frame}\n"
        "\\begin{frame}<beamer:0>{Paper only}\n  \\note{Hidden.}\n\\end{frame}\n"
        "\\section*{Unnumbered}\n" + FRAME
    )
    preamble_macro = "\\newcommand{\\blSzero}{100}\n"
    info, frames, data = tm.parse_talk(make_talk(body=body, preamble=PREAMBLE + preamble_macro))
    assert info["title"] == "Prices imply a density"
    assert [(f["kind"], f["title"]) for f in frames] == [
        ("title", "Prices imply a density"),
        ("section", "Question"),
        ("frame", "Spot is 100"),
        ("frame", "A frame states its finding"),
    ]
    first = frames[2]
    assert first["label"] == "first"
    assert first["notes"] == ["Stress the spot."]
    assert first["narration"] == "Spot is 100. Next."
    assert first["source"] == "Synthetic data"
    assert frames[1]["section_number"] == 1
    assert frames[3]["section"] == "Unnumbered"
    assert data == []


def test_parse_talk_omits_section_frames_when_dividers_are_off(make_talk):
    talk_dir = make_talk(body="\\section{Question}\n" + FRAME, preamble=PREAMBLE + "\\yjsectionpagesfalse\n")
    _, frames, _ = tm.parse_talk(talk_dir)
    assert [f["kind"] for f in frames] == ["frame"]


def test_read_nav_reads_frame_page_ranges(tmp_path):
    nav = tmp_path / "talk-slides.nav"
    nav.write_text("\\headcommand {\\beamer@framepages {1}{1}}\n\\headcommand {\\beamer@framepages {2}{4}}\n")
    assert tm.read_nav(nav) == [(1, 1), (2, 4)]


@pytest.mark.parametrize("slug", sorted(p.parent.name for p in tm.TALKS.glob("*/talk.tex")))
def test_every_example_talk_parses_with_a_note_on_every_frame(slug):
    _, frames, _ = tm.parse_talk(tm.TALKS / slug)
    assert frames
    assert all(f["notes"] for f in frames if f["kind"] != "section")
