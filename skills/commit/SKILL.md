---
name: commit
description: Use when Christian asks to commit changes. Commits only session changes, split into logical groups, with a review step before committing. Supports "do not ask" argument to skip review.
---

# Commit Session Changes

Commit only the changes from the current session, split into logical groups.

## Arguments

- No arguments: show the commit plan and wait for approval before committing.
- `do not ask`: skip the review step and commit immediately.

## Step 1: Identify session changes

Use `git status` and `git diff` to see all uncommitted changes. Cross-reference with conversation context to identify which changes were made in this session. Ignore changes that were present before the session started (check the git status snapshot from session start if available).

If unsure whether a change is from this session, ask.

## Step 2: Check for stale documentation

Before grouping commits, check whether the session changes affect anything described in the repo's documentation files.

### Which files to check

Scan for these patterns in the repo root and one level deep: `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `docs/**/*.md`. Skip files larger than 500 lines (they need targeted review, not a sweep).

### What to look for

Extract key identifiers from the diff: changed or removed function/class/variable names, renamed files, modified CLI flags, config keys, and file paths. Grep the documentation files for these identifiers. Also check whether any documentation file explicitly references a file that was renamed or deleted in this session.

### What to do

- If a doc file references something that changed, update it in the same logical commit as the code change (Step 3).
- If the doc update is substantial (new section, restructured content), flag it during the review step (Step 4) so the user can confirm the approach.
- If you are unsure whether a doc reference is stale or still valid, include it as a question in the review step rather than silently changing it.

## Step 3: Group into logical commits

Split the session changes into logical groups. Each group becomes one commit. Examples of good groupings: a config change separate from the code it enables, test files with the code they test, a refactor separate from a feature addition. Include documentation updates in the same group as the code they describe so docs and code stay in sync.

Do not go overboard. Do not use `git add -p` or patch extraction just to split a single file across commits. If a file has changes that belong to two logical groups but splitting requires patch-level extraction, put it in the most relevant group.

## Step 4: Plan the commits

For each logical group, draft:
- The list of files to stage
- A commit message (1-2 sentences, focused on "why")

Append to every commit message:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Step 5: Review

If the user passed `do not ask`, skip to Step 6.

Otherwise, present the commit plan (groups, files, messages) and wait for approval. If the doc check in Step 2 found stale references or flagged uncertain matches, list them here. The user may adjust grouping, messages, or doc updates.

## Step 6: Commit

For each group, stage the files by name (never `git add -A` or `git add .`) and commit. Use a HEREDOC for the commit message to preserve formatting.

Do not push. Leave that to the user.
