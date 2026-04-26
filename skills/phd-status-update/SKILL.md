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

# PhD Status Update Skill

You are updating the dissertation's living planning documents to reflect recent work. Your job is to record what happened and fix anything that's stale. You are not proposing next steps, suggesting priorities, or making strategic recommendations unless explicitly asked.

## Why this matters

Christian tracks his PhD progress across several interconnected documents. When one gets updated (say, a task is completed in the code repo), others may become stale (the execution plan still says that task is pending). Stale documents mislead future sessions and waste time. This skill keeps the documents consistent.

Planning documents drift *over time*; snapshots drift *at creation* and are never corrected. Snapshots therefore need more upfront rigor than planning docs, not less.

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

1. **Read first.** Read the most recent snapshot in `PhD dissertation - temporal EHR summary/Supporting material/Snapshots/` to establish the baseline — its date tells you how far back to look. Read daily notes since that date, the execution plan, and the repository map. Check git logs from all repos listed in the repository map using `git log --oneline --since=<snapshot date>` for each repo. Don't hardcode repo paths -- read the repository map at runtime.
2. **Draft changes.** For each document you plan to modify, describe what you'll change and why. Show this to Christian before editing.
3. **Apply edits.** Use the Edit tool. Make targeted changes, not wholesale rewrites.
4. **Show the diff.** After editing, run `git diff` in the phd-dissertation-writing folder so Christian can review what changed. Do not commit -- Christian will decide when to commit.

## Creating snapshots

Only create a snapshot when the request explicitly says so -- phrases like "update and snapshot" or "also create a snapshot", or an automated trigger whose prompt includes "snapshot". Absent that, skip this section. Save to `PhD dissertation - temporal EHR summary/Supporting material/Snapshots/Progress assessment YYYY-MM-DD.md`.

### Required sections

1. **Warning banner** (the standard `> [!warning]` block used by existing snapshots).
2. **What got done** — grouped by phase or theme, not chronology.
3. **Timeline assessment** — planned vs. actual dates, status markers (see legend below).
4. **What's working** — concrete, quantified where possible.
5. **Risks to watch** — each risk names (a) what specifically triggered it this period and (b) a concrete forcing function, not just a description.
6. **What's next** — *summarized from the execution plan*, not invented. This is the one exception to "don't propose next steps": a snapshot states the plan-of-record, it does not recommend deviations from it.
7. **Stale documents** — docs that need refresh before the next planning cycle.

### Status-marker legend

Use these consistently in timeline tables:

- ✅ — on time and complete
- ⚠️ — slipped but complete
- 🚧 — in progress
- ❌ — blocked

Never combine ✅ with a slip. "✅ +4 days" is a mixed signal; use ⚠️ instead.

### Internal-consistency checklist

Run this before writing the snapshot to disk. Every item must pass.

- [ ] **No contradictory claims across sections.** If one section says results exist, another can't say "no results have been produced" without qualification.
- [ ] **Every filepath and repo reference matches reality described elsewhere in the doc.** If a repo split is described, earlier references to the old path must be corrected or annotated.
- [ ] **Every source citation is a `[[wikilink]]` or a backticked path.** No bare prose references ("the model selection document"). Mirrors Christian's general writing rule.
- [ ] **Numeric claims are either precise per-item or aggregated with a single hedge — never mixed.** "Apr 2 (6), Apr 3 (4), Apr 5 (4-5), Apr 8 (varied)" is fake precision. Either commit to integers or drop the breakdown and cite the daily notes.
- [ ] **Headline claims appear in one section.** If "~1 week behind" is the headline, other sections reference it rather than restate it.
- [ ] **No adjacent softening of risks.** If a risk is named as active, the "What's working" section cannot praise the behavior that triggered it. Pick one framing.
- [ ] **No vague praise.** "Paying forward," "unusual discipline," "strong habit," "held up well" do no work. Replace with quantified or concrete claims, or cut the sentence.
- [ ] **Every filepath exists.** Run Glob or Read to verify every cited path. If a path fails verification, flag it and do not rewrite from memory.
- [ ] **Status markers follow the legend.**

### Snapshot workflow

1. **Gather inputs.** Snapshot baseline, daily notes since then, planning docs, repo git logs. Same as the planning-doc update.
2. **Draft sections.** Write against the required-sections list above.
3. **Run the internal-consistency checklist.** Fix everything that fails before showing the draft.
4. **Show Christian the draft before writing to disk.** Do not commit.

## What NOT to do

- Don't propose next steps for planning docs. The daily note's "Next tasks" section is Christian's domain. (Snapshots may summarize the plan-of-record; they still don't recommend deviations.)
- Don't create snapshots unless the request explicitly says so (interactive ask or automated trigger prompt containing "snapshot").
- Don't update documents in code repos. This skill only touches the dissertation-writing vault.
- Don't rewrite sections that are still accurate just to improve wording.
- Don't add speculative content ("this suggests we should..." or "consider whether...").
- Don't touch the dissertation paper itself or the proposal. Don't modify existing snapshots (they're frozen).
- Don't soften risk statements with adjacent praise.
- Don't let planning docs accumulate file-by-file listings that belong in the repository map. Keep pointers, not inventories.
