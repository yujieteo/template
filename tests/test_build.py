import pytest

import build
from conftest import FRAME, PREAMBLE


def test_a_talk_following_the_rules_is_lint_clean(make_talk):
    assert build.lint(make_talk()) == []


def test_every_example_talk_is_lint_clean():
    for talk in sorted(build.TALKS.glob("*/talk.tex")):
        assert build.lint(talk.parent) == [], talk


@pytest.mark.parametrize(
    ("preamble", "message"),
    [
        (PREAMBLE.replace("{beamerswitch}", "{beamer}"), "must use \\documentclass{beamerswitch}"),
        (PREAMBLE.replace("beameroptions=", "also=handout,beameroptions="), "also* options"),
        (PREAMBLE.replace("\\usepackage{yjtalk}\n", ""), "\\usepackage{yjtalk}"),
        (PREAMBLE.replace("1 October 2026", "\\today"), "\\today"),
        (PREAMBLE.replace("\\date{1 October 2026}\n", ""), "set \\date{...} explicitly"),
        (PREAMBLE + "\\immediate\\write18{ls}\n", "no shell escape"),
    ],
)
def test_lint_rejects_each_rule_break(make_talk, preamble, message):
    problems = build.lint(make_talk(preamble=preamble))
    assert any(message in p for p in problems), problems


def test_lint_names_the_line_of_a_frame_without_a_note(make_talk):
    body = FRAME + "\\begin{frame}{No note here}\n  Body.\n\\end{frame}\n"
    talk_dir = make_talk(body=body)
    line = talk_dir.joinpath("talk.tex").read_text().splitlines().index("\\begin{frame}{No note here}") + 1
    assert build.lint(talk_dir) == [
        f"frame at line {line} has no \\note{{...}} (add one, or '% no-note' to opt out)"
    ]


def test_no_note_comment_opts_a_frame_out(make_talk):
    assert build.lint(make_talk(body="\\begin{frame}\n  % no-note\n  \\includegraphics{x}\n\\end{frame}\n")) == []


def test_commented_out_rule_breaks_are_ignored(make_talk):
    preamble = PREAMBLE + "% \\today and \\write18 in a comment are fine\n"
    assert build.lint(make_talk(preamble=preamble)) == []


def test_source_date_epoch_prefers_the_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1234")
    assert build.source_date_epoch(tmp_path) == "1234"


def test_source_date_epoch_is_zero_for_an_uncommitted_talk(monkeypatch, tmp_path):
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    assert build.source_date_epoch(tmp_path / "never-committed") == "0"
