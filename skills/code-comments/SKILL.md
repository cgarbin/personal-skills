---
name: code-comments
description: >-
  Rules for comments and docstrings in Christian's code. Use when comments or docstrings are part of the work: writing or editing them, thinning out comments an agent generated, adding docstrings to a module or a function, refactoring code that already has them, reviewing the comments in a diff or a PR, or judging whether one comment earns its place. Also when a repo mandates decision-point comments in SQL. Not for error strings, log messages, commit messages, or PR description prose, which follow christian-writing-style Short snippets. Read with christian-writing-style.
---

# Code Comments

Comment-specific rules on top of **christian-writing-style**, Short snippets. That section decides whether a snippet earns its place at all. These rules decide what a comment may say once it has.

**Scope: comments and docstrings.** Commit messages, PR descriptions, log messages, and error strings follow Short snippets instead. The road-not-taken rule does not reach them, and **commit** sets what a body may say.

## Rules

1. **Plain language over jargon.** No "guard", "invariant", "idempotent", "canonical layout", "downstream", "load-bearing". Say "the check above", "so we don't re-download every run", "the file the script reads". Jargon names the category and leaves the reader to map it back to this code.
2. **Comment the unit's own contract.** No other-module rules, no naming the consumer, no "why current callers work", no who-sets-this-field. Let types and tests speak.
3. **Docstrings lead with the plain action.** No metaphor: counts don't "land", rows don't "drift apart", spans aren't "coordinate systems". Someone scanning for what the function does should have it from the first few words.
4. **Cut redundancy and drift.** Delete anything the signature, summary line, or a referenced definition already says. No field lists another constant owns. Every clause true of the exact thing it sits on, using in-scope names. Reach for delete before rephrase, because a rephrased duplicate drifts from its source on the next edit and a deleted one cannot.
5. **Four over-explanation patterns, cut on sight:** naming the caller's use for each return value, explaining another function's internals, re-arguing a decision a review or a benchmark already settled, and narrating what the code does *not* do.
6. **Road not taken.** Every sentence about a rejected alternative goes, however good the reasoning. The rejected design drags its vocabulary in with it. That knowledge belongs in a test or in the plan. The rule breaks most often while defending a comment. Asked why one matters, the nearest contrast to reach for is the option you rejected, so it goes back in verbatim. Answer that challenge with the problem and its consequence alone.
7. **"A future edit could violate this" is not enough.** The constraint must also be invisible in the code it sits on. Survivors answer a question the reader cannot resolve by looking.
8. **No comments about code that no longer runs.** Watch for `used to`, `no longer`, `after decoupling`, `the old`, `the deleted`. Exception: when comparing old vs new behavior *is* the subject.
9. **No labels from the plan that produced the code.** "Cluster A1", "F1:", "E1", "Step 3", "this task". The plan is not in the repo, so the label points nowhere. Runtime log phase numbers are fine. A numbering scheme used consistently across files is a decision, so raise it once and leave it.
10. **SQL is the exception where a repo mandates it.** Where AGENTS.md requires decision-point comments in plain English, contrastive explanations and written-out alternative implementations are required there, whatever they look like. Check before cutting inside a SQL string.

## Scan

Rules 1, 8, and 9 are the mechanical ones. Run **text-review**'s scanner on the changed files before reading the diff, so the read is spent on the rules that need judgment. It sits at `text-review/scripts/scan.py` in the skills directory, which is `~/.claude/skills/text-review/scripts/scan.py` on a standard install.

```bash
~/.claude/skills/text-review/scripts/scan.py loader.py chunker.go
```

It covers the stems for all three. It reads the comment lines only. Every stem is also ordinary code vocabulary, so a file-wide search buries the hits in identifiers and string literals.

It also runs the **christian-writing-style** voice checks over those same comment lines. An em-dash, a semicolon joining two clauses, and British spelling are wrong in a comment for the same reason they are wrong in a paragraph. The em-dash check goes further and reads every line, since an error string or a log message is prose the comment pass never sees.

Hits are candidates for you to judge. **text-review** layer 5 explains how to read the output and what to do with a hit you decide to keep.

## What a survivor looks like

Rule 7 decides most comments. The test that applies it: finish the sentence "without this, X happens and you are left with Y". A comment with no such sentence is describing mechanics the code already shows, so it goes. When the answer is a policy and no failure exists, state the policy. A comment saying the code "handles" the case names nothing.

Weak, and rejected twice in one file: "the script stages the file again and re-runs the same commit, once." It narrates what the code does. Accepted: "Nothing is committed, and the file on disk no longer matches what was staged." It names the failure and the state it leaves.

Cut. The code already says it:

```python
# Process 8192 characters at a time.
CHUNK_SIZE = 8192
```

Keep. Nothing in the file says it, and the next person to raise the number needs it:

```python
# 8192 is the largest input the tokenizer accepts in one call.
CHUNK_SIZE = 8192
```

Reachability ("callers always pass a non-empty list") is rule 2. Position ("runs before the validation step") and the operation itself ("set the cache key") are visible in the code, so rule 7 cuts them. The reason behind the operation is not visible: "Cache key includes tenant id to avoid cross-tenant reuse."

Rule 3 decides how a survivor opens. State what the thing returns or does, then why it exists. Both as plain statements. Opening on an argument makes the reader accept a premise before learning what the code does.

```python
# True if the line starts a markdown table: a header row followed by a
# delimiter row of dashes.
#
# Table blocks stay in one chunk. Rows split away from their header row
# lose the column names, and retrieval then returns bare numbers.
```

Weak: "A markdown table only makes sense with its header row." True. It argues where it should describe, so the reader still does not know what the function returns.

Five lines is the upper bound for a comment. It is what a genuinely non-obvious constraint costs. Most comments state one fact and run one line.

A module or class docstring has no such bound, because it introduces a file to someone who has read none of it. Past two or three sentences it becomes prose. **christian-writing-style**, Short snippets hands it to the blog register. Rules 1 through 9 still apply to every line of it.

## Where this fits

- **christian-writing-style**, Short snippets: no semicolons, no em-dashes, US spelling, no zombie nouns, no filler, no marketing words.
- **text-review**, code-comment test: reading a comment against the code it sits on during a review.
