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

## Step 2: Group into logical commits

Split the session changes into logical groups. Each group becomes one commit. Examples of good groupings: a config change separate from the code it enables, test files with the code they test, a refactor separate from a feature addition.

Do not go overboard. Do not use `git add -p` or patch extraction just to split a single file across commits. If a file has changes that belong to two logical groups but splitting requires patch-level extraction, put it in the most relevant group.

## Step 3: Plan the commits

For each logical group, draft:
- The list of files to stage
- A commit message (1-2 sentences, focused on "why")

Append to every commit message:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Step 4: Review

If the user passed `do not ask`, skip to Step 5.

Otherwise, present the commit plan (groups, files, messages) and wait for approval. The user may adjust grouping or messages.

## Step 5: Commit

For each group, stage the files by name (never `git add -A` or `git add .`) and commit. Use a HEREDOC for the commit message to preserve formatting.

Do not push. Leave that to the user.
