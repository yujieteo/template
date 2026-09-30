import pytest

import check_skills

SKILL = """---
name: {name}
description: What it holds. Use when the task needs it.
---

# {name}
"""

PLAYBOOK = """# Do a thing

**Stance.**

1. Step.

**Reply:** what changed.
"""


@pytest.fixture
def tree(tmp_path):
    """A minimal repo whose skills, playbooks and router agree."""
    skill = tmp_path / ".agents" / "skills" / "talk-demo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(SKILL.format(name="talk-demo"))
    playbooks = tmp_path / ".agents" / "playbooks"
    playbooks.mkdir()
    (playbooks / "demo.md").write_text(PLAYBOOK)
    (tmp_path / "SKILLS.md").write_text(
        "# SKILLS.md\n\n[demo](.agents/playbooks/demo.md) uses `.agents/skills/talk-demo/SKILL.md`.\n"
    )
    return tmp_path


def problems(root):
    return check_skills.check(root)[0]


def test_the_repo_passes():
    found, skills, playbooks = check_skills.check()
    assert found == []
    assert skills and playbooks


def test_an_agreeing_tree_passes(tree):
    assert problems(tree) == []


def test_a_skill_directory_without_skill_md_fails(tree):
    (tree / ".agents" / "skills" / "talk-empty").mkdir()
    assert ".agents/skills/talk-empty: no SKILL.md" in problems(tree)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("# no frontmatter\n", "no frontmatter"),
        ("---\nname: other\ndescription: x. Use when y.\n---\n", "must equal the directory name"),
        ("---\nname: talk-demo\n---\n", "description is empty"),
        ("---\nname: talk-demo\ndescription: Holds things.\n---\n", "Use when"),
        ("---\nname: talk-demo\ndescription: Use when editing talks/<slug>.\n---\n", "must not contain < or >"),
        ("---\nname: talk-demo\ndescription: " + "x" * 1025 + "\n---\n", "over 1024 characters"),
    ],
)
def test_bad_frontmatter_fails(tree, text, message):
    (tree / ".agents" / "skills" / "talk-demo" / "SKILL.md").write_text(text)
    assert any(message in p for p in problems(tree)), problems(tree)


def test_quoted_frontmatter_values_are_unquoted(tree):
    text = '---\nname: "talk-demo"\ndescription: \'Holds it. Use when needed.\'\n---\n'
    (tree / ".agents" / "skills" / "talk-demo" / "SKILL.md").write_text(text)
    assert problems(tree) == []


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (PLAYBOOK.replace("# Do a thing", "Do a thing"), "must open with a '# ' heading"),
        (PLAYBOOK.replace("1. Step.", "- Step."), "has no numbered steps"),
        (PLAYBOOK.replace("**Reply:**", "Reply:"), "has no **Reply:** line"),
    ],
)
def test_a_playbook_missing_a_part_fails(tree, text, message):
    (tree / ".agents" / "playbooks" / "demo.md").write_text(text)
    assert any(message in p for p in problems(tree)), problems(tree)


def test_an_unrouted_skill_or_playbook_fails(tree):
    (tree / "SKILLS.md").write_text("# SKILLS.md\n")
    assert problems(tree) == [
        "SKILLS.md: skill talk-demo is not in the router",
        "SKILLS.md: playbook demo is not in the router",
    ]


def test_a_route_to_nothing_fails(tree):
    with (tree / "SKILLS.md").open("a") as f:
        f.write("[gone](.agents/playbooks/gone.md) and `.agents/skills/talk-gone/SKILL.md`\n")
    assert "SKILLS.md: routes to skill talk-gone, which does not exist" in problems(tree)
    assert "SKILLS.md: routes to playbook gone, which does not exist" in problems(tree)


def test_a_missing_repo_path_fails_but_placeholders_and_outputs_do_not(tree):
    (tree / "scripts").mkdir()
    (tree / "scripts" / "build.py").write_text("")
    (tree / "talks").mkdir()
    (tree / "README.md").write_text(
        "Run `python3 scripts/build.py --check` and [link](scripts/build.py#L1).\n"
        "Edit `talks/<slug>/talk.tex`, read `talks/*/build/`, and `talks/demo/build/talk-slides.pdf`.\n"
        "Elsewhere: `data/viz/raw.json`, `../visuals`, `https://example.com/a/b`.\n"
        "```sh\npython3 scripts/fenced-is-not-checked.py\n```\n"
        "Stale: `scripts/gone.py`.\n"
    )
    assert problems(tree) == ["README.md: scripts/gone.py does not exist"]
