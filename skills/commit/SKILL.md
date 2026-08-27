---
name: commit
description: Use when Christian asks to commit. Commits session changes by logical group with a review gate. Pass an approval-skip phrase ("do not ask", "skip review", "yolo") to skip review.
---

# Commit Session Changes

Commit only the changes from the current session, split into logical groups.

## Arguments

- No arguments: show plan and wait for approval.
- Any approval-skip phrase (e.g., "do not ask", "skip review", "yolo", "just commit"): commit without review.

## Step 1: Identify session changes

Default: skip git inspection. If you made the edits in this session, the diff is already in your context and conversation history is the source of truth. Do not run `git status`, `git diff`, `git log`, or sample diffs as a "safety check" on your own work. Trust your context and proceed to Step 2.

Run git inspection only when:
- The session started with pre-existing modified files and you cannot tell from context what was changed before vs. during the session.
- You suspect external tooling (formatter hook, IDE save action) altered files outside your edits.
- The user reports unexpected state.

When inspection is warranted, the minimum is one `git status` to confirm what is unstaged. Cross-reference with conversation context. Ignore changes present before the session.

- If unsure whether a change is from this session, ask.
- If there are no session changes, report and stop.
- If files are already staged before this skill runs, ask whether to keep the staging or unstage and regroup.

## Step 2: Check for stale documentation

Skip if the diff has no renames, deletions, or changes to public identifiers (function/class names, CLI flags, config keys, file paths).

Otherwise, grep `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `docs/**/*.md` (root and one level deep) for the changed identifiers and renamed/deleted paths. Update referenced docs in the same commit. If the update is substantial, or you are unsure whether a reference is stale, raise it in review (Step 5).

## Step 3: Group into logical commits

If all session changes are in a single file, use one commit. Skip grouping.

Otherwise, split session changes into logical groups. Each becomes one commit. Include doc updates with the code they describe.

Do not use `git add -p` or patch extraction. If a file's changes belong to two groups, put it in the most relevant one.

## Step 4: Plan the commits

For each group, draft:
- Files to stage.
- Subject line: aim 50 chars, hard limit 72, focused on "what". No Conventional Commit prefixes (`feat:`, `fix:`, `chore:`, etc.). Examples: "Compress commit skill", "Add hook-reformat recovery", "Drop unused config flag".
- Body: default is no body. Read **Bodies** below before writing one. Separate with a blank line and wrap at 72.

End with the `Co-Authored-By` trailer the harness gives you, as its own paragraph. It is the only trailer to add. Never reconstruct it from an older commit, because the author name moves with the model.

Do not record a session link or any other per-session identifier. The commit is permanent and the link is not. It resolves for one account and nobody else. Rebase and cherry-pick copy it onto commits it does not describe. Older commits in these repos carry a `Claude-Session` trailer, which is not a reason to match them, and `--check` reports `trailer-session` if you do.

Trailers register only from the last paragraph, so one with no blank line above it is body text.

### Bodies

The diff is in the commit. A body that lists what changed, counts the changes, or names the review round says again what `git show` prints right under it.

A body states a fact the diff does not show:

- The constraint that forced this shape.
- The reason the obvious alternative fails.
- A consequence a reader would not predict from the change.

Before writing one, answer this: what would a reader of the diff get wrong without it? No answer, no body. If one clause answers it, that clause is the whole body.

Describing the commit:

```
Five changes in one commit, all § 2.4 refinements from this review
round: the hard-limit paragraph, the diagram move, "attends to" to
"depends on", the overhead definition, and the opening rewrite.
```

Stating what the diff does not show:

```
The § 2.4 numbers come from the August run. The caption cited the July
run, which had the tokenizer bug.
```

Load `christian-writing-style` for the wording. A subject line does not need the register guide.

### Checking the message

Write each group's message to its own file outside the repository so it doesn't show up as untracked in `git status`.

Check every message:

```bash
scripts/commit_group.py --check <message-file>
```

`error:` lines block the commit, `warning:` lines do not. Fix the errors before Step 5 so the plan you present is the plan that commits.

The four the body produces ask for different things:

- `error: prose/...`: an em-dash, a semicolon joining clauses, British spelling. The pattern decides these on its own, so fix the wording.
- `warning: prose/...`: the line names a test to apply or a rewrite to make. Do it, or answer in one line under `Message check` why the wording stays. Keeping it without answering drifts back to the draft.
- `warning: body-inventory`: the line quotes the phrase and says why it adds nothing. Rewrite, or say why the phrase stays.
- `warning: prose-scan`: the body was never read. Read it against **Bodies** yourself.

## Step 5: Review

If an approval-skip argument was passed, skip to Step 6. Otherwise, present the plan in this format and wait for approval:

```
Plan:
- Files: <list>
- Subject: <text>
- Body: <the body text, or "none">
- Without it: <what a reader of the diff would get wrong, or "n/a">
- Message check: <"clean", or what --check reported and what you changed>
- Doc check: <findings, "n/a" if Step 2 conditions not met, or "skipped">
```

One block per group. Auto mode does not override the gate. Invocation triggers the skill but is not approval.

## Step 6: Pre-commit checks

- If `.git/hooks/pre-commit` or `.pre-commit-config.yaml` is installed: do not pre-run anything. The hook fires at commit.
- Otherwise: scan `AGENTS.md`, root `CLAUDE.md`, and `.claude/CLAUDE.md` for documented checks and run them on the files being committed. Fix any failures before continuing.
- If neither exists: skip.

## Step 7: Commit

One call per group:

```bash
scripts/commit_group.py <message-file> <file> [<file> ...]
```

It re-runs the Step 4 checks, stages the paths you name and nothing else, and commits. When a format hook rewrites one of those paths and aborts the commit (common with ruff-format), the script stages the rewrite and runs the same commit again, once.

Exit 0 means the commit was created. Exit 2 is a usage error. Exit 1 means nothing was committed, for one of four reasons the output names:

- A message error.
- A path that is neither on disk nor tracked.
- An index already holding a path outside the group.
- A hook that failed for a reason a second run will not fix. Read the hook output and fix the cause. Do not re-run the script to get past it.

Do not push.
