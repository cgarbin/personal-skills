---
name: code-comments
description: Rules for comments and docstrings in Christian's code. Use when comments or docstrings are part of the work: writing or editing them, thinning out comments an agent generated, adding docstrings to a module or a function, refactoring code that already has them, reviewing the comments in a diff or a PR, or judging whether one comment earns its place. Also when a repo mandates decision-point comments in SQL. Not for error strings, log messages, commit messages, or PR description prose, which follow christian-writing-style Short snippets. Read with christian-writing-style.
---

# Code Comments

Comment-specific rules on top of **christian-writing-style**, Short snippets. That section decides whether a snippet earns its place at all. These rules decide what a comment may say once it has.

**Scope: comments and docstrings.** Commit messages, PR descriptions, log messages, and error strings follow Short snippets instead. The road-not-taken rule in particular does not reach them, because a commit body arguing against a rejected design is doing its job.

## Rules

1. **Plain language over jargon.** No "guard", "invariant", "idempotent", "canonical layout", "downstream", "load-bearing". Say "the check above", "so we don't re-download every run", "the file the script reads". Jargon names the category and leaves the reader to map it back to this code.
2. **Comment the unit's own contract, not things outside it.** No other-module rules, no naming the consumer, no "why current callers work", no who-sets-this-field. Let types and tests speak.
3. **Docstrings lead with the plain action**, not a noun-pile. No metaphor: counts don't "land", rows don't "drift apart", spans aren't "coordinate systems". Someone scanning for what the function does should have it from the first few words.
4. **Cut redundancy and drift.** Delete anything the signature, summary line, or a referenced definition already says. No field lists another constant owns. Every clause true of the exact thing it sits on, using in-scope names. Reach for delete before rephrase, because a rephrased duplicate drifts from its source on the next edit and a deleted one cannot.
5. **Three over-explanation patterns, cut on sight:** naming the caller's use for each return value, explaining another function's internals, re-arguing a decision a review or a benchmark already settled. Also don't narrate what the code does *not* do.
6. **Road not taken.** Every sentence about a rejected alternative goes, however good the reasoning. The rejected design drags its vocabulary in with it. That knowledge belongs in a test or in the plan.
7. **"A future edit could violate this" is not enough.** The constraint must also be invisible in the code it sits on. Survivors answer a question the reader cannot resolve by looking.
8. **No comments about code that no longer runs.** Grep `used to`, `no longer`, `after decoupling`, `the old`, `the deleted`. Exception: when comparing old vs new behavior *is* the subject.
9. **No labels from the plan that produced the code.** "Cluster A1", "F1:", "E1", "Step 3", "this task". The plan is not in the repo, so the label points nowhere. Runtime log phase numbers are fine. A numbering scheme used consistently across files is a decision, so raise it once and leave it.
10. **SQL is the exception where a repo mandates it.** Where AGENTS.md requires decision-point comments in plain English, contrastive explanations and written-out alternative implementations are required, not redundancy. Check before cutting inside a SQL string.

## Scan

Rules 1, 8, and 9 are the mechanical ones. Search the comment lines of the diff for these stems before reading it, so the read is spent on the rules that need judgment.

- Rule 1, jargon: `guard`, `invariant`, `idempotent`, `canonical`, `downstream`, `load-bearing`.
- Rule 8, code that no longer runs: `used to`, `no longer`, `after decoupling`, `the old`, `the deleted`.
- Rule 9, plan labels: `Cluster`, `Step` followed by a digit, `this task`, and a bare letter-digit label opening a comment (`F1:`, `E1`).

Every stem here is also ordinary code vocabulary, so a file-wide search buries the hits in identifiers and string literals. Hits are candidates, not verdicts.

## What a survivor looks like

Rule 7 decides most comments.

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

**christian-writing-style**, Short snippets, has a longer docstring example and shows the contract-first opening.

## Where this fits

- **christian-writing-style**, Short snippets: two of its paragraphs are rules from this list stated for every snippet type. "Do not document what the code shows" is rule 2. "Lead with the contract, then the why" is rule 3. Change them there, not here.
- **text-review**, code-comment test: reading a comment against the code it sits on during a review.
