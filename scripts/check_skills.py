#!/usr/bin/env python3
"""Check that the agent playbook's parts agree: SKILLS.md, skills, playbooks.

    python3 scripts/check_skills.py

* Every .agents/skills/<name>/ holds a SKILL.md whose frontmatter has a
  `name` equal to the directory and a `description` that says what the skill
  covers and, with "Use when", when to load it.
* Every .agents/playbooks/<name>.md opens with a `# ` heading, has numbered
  steps, and ends with a **Reply:** line.
* SKILLS.md links every skill and playbook, and nothing under .agents/ that
  does not exist.
* A repo path written in backticks or as a link in SKILLS.md, README.md, a
  skill or a playbook exists. Paths with placeholders (<slug>, *) and build
  outputs are not checked.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
MAX_NAME, MAX_DESCRIPTION = 64, 1024
REF = re.compile(r"\.agents/(?:skills/([^/\s)`]+)/SKILL\.md|playbooks/([^/\s)`]+)\.md)")


def frontmatter(text):
    """The `key: value` pairs between the opening and closing `---`, or None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        m = re.match(r"([A-Za-z][\w-]*):\s*(.*)$", line)
        if m:
            value = m.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            fields[m.group(1)] = value
    return None


def check_skill(skill_dir):
    rel = skill_dir.relative_to(skill_dir.parents[2]).as_posix()
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return [f"{rel}: no SKILL.md"]
    fields = frontmatter(path.read_text())
    if fields is None:
        return [f"{rel}/SKILL.md: no frontmatter between --- lines"]
    problems = []
    name, description = fields.get("name", ""), fields.get("description", "")
    if name != skill_dir.name:
        problems.append(f"{rel}/SKILL.md: name {name!r} must equal the directory name {skill_dir.name!r}")
    if not NAME.fullmatch(skill_dir.name) or len(skill_dir.name) > MAX_NAME:
        problems.append(f"{rel}: directory name must be kebab-case, at most {MAX_NAME} characters")
    if not description:
        problems.append(f"{rel}/SKILL.md: description is empty")
    elif len(description) > MAX_DESCRIPTION:
        problems.append(f"{rel}/SKILL.md: description is over {MAX_DESCRIPTION} characters")
    elif "Use when" not in description:
        problems.append(f"{rel}/SKILL.md: description must say when to load it (\"Use when ...\")")
    if re.search(r"[<>]", description):
        problems.append(f"{rel}/SKILL.md: description must not contain < or > (read as XML tags)")
    return problems


def check_playbook(path):
    rel = path.relative_to(path.parents[2]).as_posix()
    text = path.read_text()
    problems = []
    if not text.startswith("# "):
        problems.append(f"{rel}: must open with a '# ' heading")
    if not re.search(r"^1\. ", text, re.M):
        problems.append(f"{rel}: has no numbered steps")
    if not re.search(r"^\*\*Reply:\*\*", text, re.M):
        problems.append(f"{rel}: has no **Reply:** line")
    return problems


def check_router(root, skills, playbooks):
    router = root / "SKILLS.md"
    if not router.is_file():
        return ["SKILLS.md is missing"]
    text = router.read_text()
    linked_skills, linked_playbooks = set(), set()
    for skill, playbook in REF.findall(text):
        if skill:
            linked_skills.add(skill)
        else:
            linked_playbooks.add(playbook)
    problems = []
    for kind, linked, present in (("skill", linked_skills, skills), ("playbook", linked_playbooks, playbooks)):
        problems += [f"SKILLS.md: {kind} {n} is not in the router" for n in sorted(present - linked)]
        problems += [f"SKILLS.md: routes to {kind} {n}, which does not exist" for n in sorted(linked - present)]
    return problems


def repo_paths(text):
    """Path-like words from inline code spans and link targets, fences removed."""
    text = re.sub(r"^```.*?^```", "", text, flags=re.M | re.S)
    words = [w for span in re.findall(r"`([^`\n]+)`", text) for w in span.split()]
    words += re.findall(r"\]\(([^)\s#]+)", text)
    return words


def check_paths(root, doc):
    top = {p.name for p in root.iterdir()} - {".git"}
    problems = []
    for word in repo_paths(doc.read_text()):
        path = word.split("#")[0].rstrip("/.,;:")
        if re.search(r"[<>*{}$\[\]]|://", path) or "/" not in path:
            continue
        if path.split("/")[0] not in top or "/build/" in f"/{path}/":
            continue
        if not (root / path).exists():
            problems.append(f"{doc.relative_to(root).as_posix()}: {path} does not exist")
    return problems


def check(root=ROOT):
    skills_dir, playbooks_dir = root / ".agents" / "skills", root / ".agents" / "playbooks"
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
    playbook_files = sorted(playbooks_dir.glob("*.md")) if playbooks_dir.is_dir() else []
    problems = []
    for d in skill_dirs:
        problems += check_skill(d)
    for p in playbook_files:
        problems += check_playbook(p)
    problems += check_router(root, {d.name for d in skill_dirs}, {p.stem for p in playbook_files})
    docs = [root / "SKILLS.md", root / "README.md", *playbook_files]
    docs += [d / "SKILL.md" for d in skill_dirs]
    for doc in docs:
        if doc.is_file():
            problems += check_paths(root, doc)
    return problems, len(skill_dirs), len(playbook_files)


def main():
    problems, skills, playbooks = check()
    if problems:
        sys.exit("check_skills: failed:\n  " + "\n  ".join(problems))
    print(f"verified: {skills} skills and {playbooks} playbooks, all routed from SKILLS.md, paths resolve")


if __name__ == "__main__":
    main()
