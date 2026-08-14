# Creating snapshots

Save to `PhD dissertation - temporal EHR summary/Supporting material/Snapshots/Progress assessment YYYY-MM-DD.md`.

Snapshots are frozen at creation. Mistakes stay forever, so apply more rigor up front than for planning docs.

## Required sections

1. **Warning banner** (the standard `> [!warning]` block used by existing snapshots).
2. **What got done**: grouped by phase or theme, not chronology.
3. **Timeline assessment**: planned vs. actual dates, status markers (see legend below).
4. **What's working**: concrete, quantified where possible.
5. **Risks to watch**: each risk names (a) what specifically triggered it this period and (b) a concrete forcing function, not just a description.
6. **What's next**: *summarized from the execution plan*, not invented. This is the one exception to "don't propose next steps". A snapshot states the plan-of-record, it does not recommend deviations from it.
7. **Stale documents**: docs that need refresh before the next planning cycle.

## Status-marker legend

Use these consistently in timeline tables:

- ✅: on time and complete
- ⚠️: slipped but complete
- 🚧: in progress
- ❌: blocked

Never combine ✅ with a slip. "✅ +4 days" is a mixed signal. Use ⚠️ instead.

## Internal-consistency checklist

Run this before writing the snapshot to disk. Every item must pass.

- [ ] **No contradictory claims across sections.** If one section says results exist, another can't say "no results have been produced" without qualification.
- [ ] **Every filepath and repo reference matches reality described elsewhere in the doc.** If a repo split is described, earlier references to the old path must be corrected or annotated.
- [ ] **Every source citation is a `[[wikilink]]` or a backticked path.** No bare prose references ("the model selection document"). Mirrors Christian's general writing rule.
- [ ] **Numeric claims are either precise per-item or aggregated with a single hedge, never mixed.** "Apr 2 (6), Apr 3 (4), Apr 5 (4-5), Apr 8 (varied)" is fake precision. Either commit to integers or drop the breakdown and cite the daily notes.
- [ ] **Headline claims appear in one section.** If "~1 week behind" is the headline, other sections reference it rather than restate it.
- [ ] **No adjacent softening of risks.** If a risk is named as active, the "What's working" section cannot praise the behavior that triggered it. Pick one framing.
- [ ] **No vague praise.** "Paying forward," "unusual discipline," "strong habit," "held up well" do no work. Replace with quantified or concrete claims, or cut the sentence.
- [ ] **Every filepath exists.** Run Glob or Read to verify every cited path. If a path fails verification, flag it and do not rewrite from memory.
- [ ] **Status markers follow the legend.**

## Workflow

1. **Gather inputs.** Snapshot baseline, daily notes since then, planning docs, repo git logs. Same as the planning-doc update.
2. **Draft sections.** Write against the required-sections list above.
3. **Run the internal-consistency checklist.** Fix everything that fails before showing the draft.
4. **Show Christian the draft before writing to disk.** Auto mode does not override this gate. Do not commit.
