---
name: commit
description: Use when Christian asks to commit changes. Commits only session changes, split into logical groups, with a review step before committing. Accepts any approval-skip argument (e.g., "do not ask", "skip review", "yolo") to commit without review.
---

# Commit Session Changes

Commit only the changes from the current session, split into logical groups.

## Arguments

- No arguments: show the commit plan and wait for approval before committing.
- Any approval-skip argument (e.g., "do not ask", "skip review", "yolo", "just commit"): skip the review step and commit immediately. Treat any non-empty argument that signals "go ahead" as approval-skip.

## Step 1: Identify session changes

Use `git status` and `git diff` to see all uncommitted changes. Cross-reference with conversation context to identify which changes were made in this session. Ignore changes that were present before the session started (check the git status snapshot from session start if available).

If unsure whether a change is from this session, ask.

If there are no session changes to commit, report it and stop.

If files are already staged before this skill runs, ask whether to respect the existing staging or unstage and regroup.

## Step 2: Check for stale documentation

Before grouping commits, check whether the session changes affect anything described in the repo's documentation files.

Skip this step if the diff has no renames, deletions, or changes to public identifiers (function/class names, CLI flags, config keys, file paths). Pure formatting, comment, or internal-implementation changes do not need a doc sweep.

### Which files to check

Scan for these patterns in the repo root and one level deep: `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `docs/**/*.md`. Identifier grep is cheap regardless of file size, so do not skip large files for the grep itself. Only defer prose-staleness reading (looking for outdated narrative descriptions) on files larger than 500 lines.

### What to look for

Extract key identifiers from the diff: changed or removed function/class/variable names, renamed files, modified CLI flags, config keys, and file paths. Grep the documentation files for these identifiers. Also check whether any documentation file explicitly references a file that was renamed or deleted in this session.

### What to do

- If a doc file references something that changed, update it in the same logical commit as the code change (Step 3).
- If the doc update is substantial (new section, restructured content), flag it during the review step (Step 4) so the user can confirm the approach.
- If you are unsure whether a doc reference is stale or still valid, include it as a question in the review step rather than silently changing it.

## Step 3: Group into logical commits

Split the session changes into logical groups. Each group becomes one commit. Examples of good groupings: a config change separate from the code it enables, test files with the code they test, a refactor separate from a feature addition. Include documentation updates in the same group as the code they describe so docs and code stay in sync.

Do not go overboard. Do not use `git add -p` or patch extraction. If a file has changes belonging to two groups, put it in the most relevant one.

## Step 4: Plan the commits

For each logical group, draft:
- The list of files to stage
- A commit message with a short subject line (aim for 50 characters, hard limit 72, focused on "what") and an optional body separated by a blank line (focused on "why" and context). Wrap the body at 72 characters. The subject line should be concise enough to scan in `git log --oneline`. Put useful detail in the body, not the subject.

Do not use commit prefixes (`feat:`, `fix:`, `chore:`, etc.).

Append to every commit message:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Step 5: Review

If the user passed an approval-skip argument (see Arguments), skip to Step 6.

Otherwise, present the commit plan (groups, files, messages) and wait for approval. If the doc check in Step 2 found stale references or flagged uncertain matches, list them here. The user may adjust grouping, messages, or doc updates.

Auto mode does not override this review gate. The user's invocation message ("commit the changes") triggers the skill but is not approval of the plan. Wait for explicit approval unless an approval-skip argument was passed.

## Step 6: Pre-commit checks

If a pre-commit hook is installed (`.git/hooks/pre-commit` exists, or the repo has `.pre-commit-config.yaml`), do not pre-run linters, formatters, or tests. The hook will run them when `git commit` fires in Step 7. Pre-running duplicates work and conflicts with the "trust the pre-commit hook" preference.

If no hook is installed, fall back to documented checks: scan AGENTS.md, root `CLAUDE.md`, and `.claude/CLAUDE.md` for pre-commit instructions and run them on the files being committed. If any check fails, fix the issue before proceeding.

If neither a hook nor documented checks exist, skip this step.

## Step 7: Commit

For each group, stage the files by name (never `git add -A` or `git add .`) and commit. Use a HEREDOC for the commit message to preserve formatting.

If a pre-commit hook reformats files and aborts the commit (common with ruff-format), re-stage the formatter's changes and re-run the same `git commit`. Do not amend, since no commit was created.

Do not push. Leave that to the user.
