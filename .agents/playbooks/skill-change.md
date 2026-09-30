# Skill or playbook change

**Keep only prose that changes a decision.**

1. Put knowledge in a skill and order of work in a playbook. A skill is
   reference an agent reads when a step sends it there; a playbook is
   numbered steps that end in a check.
2. Skill: `.agents/skills/<name>/SKILL.md`, kebab-case `name` equal to the
   directory, and a `description` that says what it holds and, starting
   "Use when", which tasks load it. No `<` or `>` in the description.
3. Playbook: `.agents/playbooks/<name>.md`, a level-one heading, one bold line of
   stance and a link to its skill, numbered steps, and a final `**Reply:**`
   line naming what the reply must contain beyond the router's Reply rules.
4. Point at other skills, playbooks and files by relative link or path; do
   not restate them. Name a command once, where it is used.
5. Route it: add the playbook or skill to the tables in `SKILLS.md`, and
   remove rows for anything deleted.
6. `make lint-skills lint-md`. Test cases for a new check go in
   `tests/test_check_skills.py`.

**Reply:** what the skill or playbook now tells an agent to do differently,
the router rows added or changed, and the lint result.
