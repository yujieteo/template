# Fix a failing build, lint, test or CI job

**Fix the cause in the source; never loosen the check.** Detail:
[talk-build-verify](../skills/talk-build-verify/SKILL.md).

1. Reproduce it locally with the exact failing command. From CI, read the
   failed step (`gh run view <run-id> --log-failed`) and run the same make
   target: `make lint-py`, `make lint-md`, `make lint-skills`, `make test`, or
   `make check TALK=<slug>`.
2. Read the first real error, not the last line. For a compile failure, open
   `talks/<slug>/build/talk-<variant>.log` at the reported line.
3. Find the cause in the failure table. Not there: bisect it. Build one
   variant (`--only`), comment frames out, or diff the two builds for a
   reproducibility failure, until one change flips the result.
4. Fix the source: the talk, the template, the script, or the doc a check
   names. Change a check, test or lint rule only when it is wrong, and say
   why in the commit.
5. Rerun the same command and see it pass, then run the gates for everything
   the fix touched.
6. A check that should have caught this earlier but did not: add it, per the
   principle **Encode a repeated lesson as a check**.

**Reply:** the failing command and its first error line, the root cause, the
fix, and the same command passing. Quote both outputs trimmed to the decisive
lines.
