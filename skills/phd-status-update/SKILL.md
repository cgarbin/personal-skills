---
name: phd-status-update
description: >
  Comprehensive update of all PhD dissertation planning documents. Trigger on
  explicit full-update requests like "update all the phd plans", "do a full phd
  state update", "bring all phd plans up to date", "sync the phd documents",
  "update phd status", "refresh the dissertation plans", or any request to bring
  multiple PhD planning documents into sync with recent work. Do NOT trigger on
  single-document edits, individual PhD questions, or daily note operations.
---

# PhD Status Update

You are updating the dissertation's living planning documents to reflect recent work. Your job is to record what happened and fix anything that's stale. You are not proposing next steps, suggesting priorities, or making strategic recommendations unless explicitly asked.

## Why this matters

Christian tracks his PhD progress across several interconnected documents. When one gets updated (say, a task is completed in the code repo), others may become stale (the execution plan still says that task is pending). Stale documents mislead future sessions and waste time. This skill keeps the documents consistent.

## What to update

Two layers, in order of priority:

### 1. Planning documents

Key file paths:

- Execution plan: `PhD dissertation - temporal EHR summary/dissertation execution plan.md`
- Writing plan: `PhD dissertation - temporal EHR summary/dissertation writing plan.md`
- Repository map: `PhD dissertation - temporal EHR summary/Supporting material/Repository map.md`

**Execution plan** contains:

- A **progress log** with dated entries. Add a new entry if meaningful progress has been made since the last entry (not for routine small tasks). Each entry should be 2-4 sentences summarizing what changed at the phase level.
- **Phase headers** with date ranges. If a phase completed or slipped, update the dates and status markers.
- A **"Next concrete action"** section at the bottom. Update this to reflect what's actually next, based on recent daily notes and what was completed.
- A **Gantt chart** (Mermaid). Update if phase dates shifted.
- A **phase table** with dates. Update if dates shifted.

**Writing plan** contains checkboxed tasks organized by chapter. Check off tasks that have been completed based on daily notes and git history. Don't check off tasks that are only partially done.

Only touch sections where something actually changed. Don't rewrite content that's still accurate.

### 2. Cross-document consistency

After updating the above, check for inconsistencies:

- Does the most recent daily note's "Next tasks" section match what the execution plan says is next?
- If daily notes show tasks or phases as completed, are they marked done in the execution plan?
- Are any date references in the execution plan now in the past but still described in future tense?

Fix inconsistencies in place. If you're unsure whether something is stale or intentional, flag it for Christian rather than changing it.

## How to do the update

1. **Read first.** Read recent daily notes (for context on what was worked on since the last progress log entry), the execution plan, and the repository map. Check git logs from all repos listed in the repository map using `git log --oneline --since=<date of last progress log entry>` for each repo. Don't hardcode repo paths -- read the repository map at runtime.
2. **Draft changes.** For each document you plan to modify, describe what you'll change and why. Show this to Christian before editing.
3. **Apply edits.** Use the Edit tool. Make targeted changes, not wholesale rewrites.
4. **Show the diff.** After editing, run `git diff` in the phd-dissertation-writing folder so Christian can review what changed. Do not commit -- Christian will decide when to commit.

## What NOT to do

- Don't propose next steps or suggest what to work on next. The daily note's "Next tasks" section is Christian's domain.
- Don't create snapshot documents.
- Don't update documents in code repos. This skill only touches the dissertation-writing vault.
- Don't rewrite sections that are still accurate just to improve wording.
- Don't add speculative content ("this suggests we should..." or "consider whether...").
- Don't touch the dissertation paper itself, the proposal, or any document in the Snapshots folder.
