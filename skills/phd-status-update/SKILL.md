---
name: phd-status-update
description: >-
  Comprehensive update of all PhD dissertation planning documents. Trigger on
  explicit full-update requests like "update all the phd plans", "do a full phd
  state update", "bring all phd plans up to date", "sync the phd documents",
  "update phd status", "refresh the dissertation plans", or any request to bring
  multiple PhD planning documents into sync with recent work. Do NOT trigger on
  single-document edits, individual PhD questions, or daily note operations.
---

# PhD Status Update Skill

You are updating the dissertation's living planning documents to reflect recent work. Your job is to record what happened and fix anything that's stale. You are not proposing next steps, suggesting priorities, or making strategic recommendations unless explicitly asked.

## What to update

Two layers, in order of priority.

### 1. Planning documents

Key file paths:

- Execution plan: `PhD dissertation - temporal EHR summary/dissertation execution plan.md`
- Writing plan: `PhD dissertation - temporal EHR summary/dissertation writing plan.md`
- Repository map: `PhD dissertation - temporal EHR summary/Supporting material/Repository map.md`

**Execution plan** contains:

- A **Status section** at the top with current phase, last milestone, in-progress work, and next gate. Update these lines when the phase advances, a milestone is committed, or the in-progress or gate items shift. No slip tracking here. That lives in the progress log.
- A **progress log** at the bottom with dated entries. Add a new entry when a phase completed, a phase slipped, or a deliverable in the writing plan was checked off. Each entry is a `### YYYY-MM-DD: short summary` section followed by 2-4 sentences of prose (split with `####` subheadings if it grows). Entries are chronological, oldest first.
- **Phase headers** with date ranges. If a phase completed or slipped, update the dates and status markers.
- A **"Next concrete action"** section. Update this to reflect what's actually next, based on recent daily notes and what was completed.
- A **Gantt chart** (Mermaid). Update if phase dates shifted.
- A **phase table** with dates. Update if dates shifted.

**Writing plan** contains checkboxed tasks organized by chapter. Check off tasks that have been completed based on daily notes and git history. Don't check off tasks that are only partially done.

Only touch sections where something actually changed. Don't rewrite content that's still accurate.

**Don't duplicate the repository map.** If information belongs in the repository map (repo locations, doc inventories, mount paths), planning docs should point at the map, not replicate it. If you see a table or list drifting into a full manifest of every file, trim it back to directory-level pointers.

### 2. Cross-document consistency

After updating the above, check for inconsistencies:

- Does the most recent daily note's "Next tasks" section match what the execution plan says is next?
- If daily notes show tasks or phases as completed, are they marked done in the execution plan?
- Are any date references in the execution plan now in the past but still described in future tense?

Fix inconsistencies in place. If an inconsistency has two plausible resolutions, flag both for Christian and do not edit.

## Writing style

All prose written or edited by this skill (planning docs and snapshots) must follow Christian's writing style: no em-dashes, no semicolons, prose for arguments and explanations (bullets fine for lists, steps, and specs), active voice, no hedging or filler. Invoke the `christian-writing-style` skill before writing prose.

## How to do the update

1. **Read first.** Read the most recent snapshot in `PhD dissertation - temporal EHR summary/Supporting material/Snapshots/` to establish the baseline. Its date tells you how far back to look. Then read:
   - Daily notes since that date.
   - The execution plan.
   - The repository map (read at runtime, do not hardcode repo paths).
   - Git logs for each repo in the map: `git log --oneline --since=<snapshot date>`.
2. **Draft changes.** For each document, describe what you'll change and why. Show Christian before editing. Auto mode does not override this gate.
3. **Apply edits.** Use the Edit tool. Targeted changes, not wholesale rewrites.
4. **Show the diff.** After editing, run `git diff` in the phd-dissertation-writing folder so Christian can review. Do not commit. Christian decides when to commit.

## Creating snapshots

Only create a snapshot when the request explicitly says so, in phrases like "update and snapshot" or "also create a snapshot", or an automated trigger whose prompt includes "snapshot". Absent that, skip this section.

When it applies, read `references/snapshots.md`. It has the required sections, the status-marker legend, the internal-consistency checklist, and the workflow.

## What NOT to do

- Don't propose next steps for planning docs. The daily note's "Next tasks" section is Christian's domain. Snapshots may summarize the plan-of-record but still don't recommend deviations.
- Don't update documents in code repos. This skill only touches the dissertation-writing vault.
- Don't rewrite sections that are still accurate just to improve wording.
- Don't add speculative content ("this suggests we should..." or "consider whether...").
- Don't touch the dissertation paper itself or the proposal. Don't modify existing snapshots (they're frozen).
- Don't soften risk statements with adjacent praise.
- Don't let planning docs accumulate file-by-file listings that belong in the repository map. Keep pointers, not inventories.
