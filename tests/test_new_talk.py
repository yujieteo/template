import shutil
import sys

import pytest

import build
import new_talk


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / "starter").mkdir()
    shutil.copy(new_talk.ROOT / "starter" / "talk.tex", tmp_path / "starter" / "talk.tex")
    (tmp_path / "talks").mkdir()
    monkeypatch.setattr(new_talk, "ROOT", tmp_path)
    return tmp_path


def run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["new_talk.py", *args])
    new_talk.main()


def test_scaffold_fills_every_placeholder_and_is_lint_clean(repo, monkeypatch):
    run(monkeypatch, "my-talk", "--title", "Prices imply a density", "--author", "Ada", "--date", "1 October 2026")
    text = (repo / "talks" / "my-talk" / "talk.tex").read_text()
    assert "{{" not in text
    assert "\\title{Prices imply a density}" in text
    assert "\\date{1 October 2026}" in text
    assert build.lint(repo / "talks" / "my-talk") == []


def test_scaffold_refuses_an_existing_talk(repo, monkeypatch):
    (repo / "talks" / "taken").mkdir()
    with pytest.raises(SystemExit, match="already exists"):
        run(monkeypatch, "taken")


@pytest.mark.parametrize("slug", ["My_Talk", "trailing-", "two--dashes", "has space"])
def test_scaffold_rejects_a_slug_that_is_not_kebab_case(repo, monkeypatch, slug):
    with pytest.raises(SystemExit, match="kebab-case"):
        run(monkeypatch, slug)
    assert list((repo / "talks").iterdir()) == []
