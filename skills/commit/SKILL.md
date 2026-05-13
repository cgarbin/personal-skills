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
- Body: only when the subject does not already carry the "why". Default: no body. When you do write one, separate with a blank line and wrap at 72.

Append:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Step 5: Review

If an approval-skip argument was passed, skip to Step 6. Otherwise, present the plan in this format and wait for approval:

```
Plan:
- Files: <list>
- Subject: <text>
- Body: <short summary or "none">
- Doc check: <findings or "skipped">
```

One block per group. Auto mode does not override the gate. Invocation triggers the skill but is not approval.

## Step 6: Pre-commit checks

- If `.git/hooks/pre-commit` or `.pre-commit-config.yaml` is installed: do not pre-run anything. The hook fires at commit.
- Otherwise: scan `AGENTS.md`, root `CLAUDE.md`, and `.claude/CLAUDE.md` for documented checks and run them on the files being committed. Fix any failures before continuing.
- If neither exists: skip.

## Step 7: Commit

For each group, stage files by name (never `git add -A` or `git add .`) and commit.

If a format hook rewrites files and aborts the commit (common with ruff-format), re-stage the formatter's changes and re-run the same `git commit`. Do not amend, since no commit was created.

Do not push.
