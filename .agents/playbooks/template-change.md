# Template change

**A change here is a change to every talk.** Detail:
[talk-template-maintenance](../skills/talk-template-maintenance/SKILL.md).

1. Name what every talk will see differently, before editing.
2. Make the change where the skill says it lives: colours in
   `theme-tokens.json` then `make tokens`; a variant in every place the skill
   lists; runtime behaviour in `web/shell.html` or `manim/talkscene.py`,
   never in generated output.
3. Script change: write or update the test in `tests/` first and see it fail,
   then change the script and see it pass. Time `make test` before and after.
4. `make check`: both example talks pass unchanged.
5. Render and look at one page per variant of both examples
   (`pdftoppm -r 50 -png`), especially notes and script pages.
6. Starter or scaffold change: build a throwaway talk from it, then delete it.

   ```sh
   python3 scripts/new_talk.py zz-smoke
   python3 scripts/build.py --check zz-smoke
   rm -r talks/zz-smoke
   ```

7. New check: break a copy of a talk the way the check targets and confirm the
   build fails with the intended message.
8. Shared runtime change: rebuild both examples with `to_web.py` and
   `to_manim.py`, drive the web deck, and look at the video's review frames
   ([web-and-video](web-and-video.md)).
9. `make lint test`.

**Reply:** what every talk now does differently, the `make check` result for
both examples, the variants you looked at, the negative test for any new
check, and `make test`'s time before and after any added test.
