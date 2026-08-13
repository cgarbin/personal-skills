# Eval fixtures

Input files for the behavioral evals in `../evals.json`. **Do not clean these up.**

The defects in them are the test. `chunker.py` has fifteen planted comment violations, one or more per `code-comments` rule, plus one comment that has to survive:

```python
# 8192 is the largest input the tokenizer accepts in one call.
```

That keeper is why the fixture works. An agent that deletes every comment satisfies all fifteen "removes X" assertions and is still wrong, and without a comment worth keeping the eval would score that run as a success.

This matters because `claude-md/CLAUDE.md` tells every session to apply the `code-comments` rules to comments it writes or edits. A session working elsewhere in this repo could reasonably read these files as sloppy and tidy them. Tidying them deletes the eval.

## Changing a fixture

Change one only alongside the assertions in `../evals.json` that name it, and re-run the evals afterward. An assertion quotes the comment it expects to be removed, so editing the wording on either side alone leaves an assertion that can never pass.

The executable code is a separate matter and should stay correct. Bugs unrelated to the comments pull the agent's attention toward them and away from what the fixture is for, and every future round rediscovers the same ones. `chunker.py` is importable and its chunking works, including keeping markdown table blocks whole.
