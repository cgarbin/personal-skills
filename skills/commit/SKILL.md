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
- Body: only when the subject does not already state the "why". Default: no body. When you do write one, separate with a blank line and wrap at 72.

End with the trailers the harness gives you, `Co-Authored-By` and `Claude-Session`, as their own paragraph. Do not copy them from an older commit. The author name moves with the model, and the session link is per session. Trailers register only from the last paragraph, so one with no blank line above it is body text.

Write each group's message to its own file outside the repository so it doesn't show up as untracked in `git status`.

When a group's message has a body, load `christian-writing-style` and write the body under it. A subject line does not need the register guide.

Check every message:

```bash
scripts/commit_group.py --check <message-file>
```

`error:` lines block the commit, `warning:` lines do not. Fix the errors before Step 5 so the plan you present is the plan that commits.

## Step 5: Review

If an approval-skip argument was passed, skip to Step 6. Otherwise, present the plan in this format and wait for approval:

```
Plan:
- Files: <list>
- Subject: <text>
- Body: <short summary or "none">
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
