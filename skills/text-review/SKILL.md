---
name: text-review
description: >-
  Review Christian's writing for accuracy, organization, and clarity: prose, the writing inside code (comments, docstrings, commit messages, PR descriptions), and sets of edits on their own, short of a whole document (a diff, an edit pass, another round after changes). Use whenever he asks to review, critique, proofread, or give feedback on anything already written, down to a single comment or a single edit, including casual asks like "check this" or "does this read well". Always use with the christian-writing-style skill.
---

# Text Review

How to review Christian's writing: what to examine, in what order, and how to present feedback. For voice, tone, sentence patterns, and formatting conventions, consult **christian-writing-style**.

Always load **christian-writing-style** alongside this skill, plus the reference file for the register under review: `references/blog.md` or `references/academic.md`. Short snippets need neither. Several checks below cite rules that live only in those files.

---

## Before you start

Three things shape what feedback is useful. Settle them first.

- **Register.** Blog post, journal paper, email, commit message? christian-writing-style routes these at the top of its SKILL.md, and the reference file to load follows from that routing.
- **Draft stage.** Ask if unclear. Early drafts: feedback on structure, argument, missing pieces. Late drafts: sentence-level editing and polish. Reviewing an early draft for comma placement wastes time. Reviewing a final draft without checking the argument is worse.
- **Scope.** A whole document, or a single comment, commit subject, or paragraph. A snippet needs the mechanical scan and, for comments, the code-comment test. Layers 1, 2, and 4 and the two-phase gate assume a document.

**Reviewing an edit pass is not reviewing a draft.** When the subject is a set of changes, read each changed passage together with the passages that depend on it, in full and in order, whether or not they changed. Read each added passage against the rules that already govern it. "Check what a pass left inconsistent" under Applying changes names the kinds to look for. A diff shows the side that changed and hides the side that depended on it, so coupling breakage is invisible from the diff by construction.

---

## Review layers

Work through these in order. Each builds on the previous.

### 1. Accuracy and technical correctness

The most important layer. Elegant prose built on wrong claims is worse than clunky prose built on right ones.

- **Factual claims.** Verify statements about specific numbers, dates, algorithms, papers, results. Flag anything that looks wrong or that you can't verify.
- **Technical terminology.** Used correctly and consistently? Watch for terms that are close but not quite right, or that shift meaning between paragraphs.
- **Citations and attributions.** Do cited sources actually say what the text claims? Are ideas attributed correctly? Claims that need a citation but lack one? Three failure modes to watch:
  - Crediting a popularizer instead of the originator.
  - Naming a real source that argues something adjacent to the claim being made.
  - Verbs that overstate how settled the evidence is ("X established that" when X argued it, or when it stays contested).
- **Logic and reasoning.** Argument holds together? Watch for unstated assumptions, logical jumps, conclusions that don't follow from evidence, correlation-causation conflation, overgeneralization.
- **Numbers and data.** Add up? Percentages consistent with raw counts? Fair comparisons (same baseline, same conditions)?

**Memory-sourced citations are unverified by default.** A citation written from recall is not a checked citation, even when it looks precise and turns out to be right. Author lists, years, journal names, page numbers, book titles, and "X coined this" claims feel certain and are often wrong by one name or one year. Flag every one as Must fix, including citations *you* wrote. If checking isn't possible now, suggest marking it unverified in the text, which leaving it alone does not.

Two related checks:

- **"Needs a source" versus "has a source nobody checked."** Different problems, different fixes, and the second one hides better.
- **Primary versus secondary sourcing.** If claims about a work come from summaries, reviews, or interviews, suggest the piece say so. A short "sources and confidence" note at the end tells a future reader which claims are safe to cite onward.

### 2. Argument and organization

- **Clear purpose.** Can you state the takeaway in one sentence? If not, the piece may be doing too many things.
- **Structure serves the argument.** Sections in logical sequence, each building on what came before. If you have to re-read a section because it depends on something introduced later, the order is wrong.
- **Gaps.** Places where the reader would ask "but what about...?" or "why?" and the text doesn't answer.
- **Unnecessary material.** Sections, paragraphs, sentences that don't contribute. Tangents. Background the audience already knows.
- **Two copies of a fact need a mechanism.** Say which copy goes, or what check fails when they diverge. A comment asking a human to keep them in step is not a mechanism. In one paper repository, figure scripts held captions copied from the paper, and two tables shared a column with an HTML comment asking an editor to keep them synchronized. Both had drifted by the time anyone checked.
- **Transitions.** Each section connects to the next. Reader can follow opening to conclusion without getting lost.
- **Tables, figures, lists.** Look for places where prose does work that structure would do better: comparisons across multiple items, step-by-step processes, chronological progressions, dense numerical results. Christian's tables are a signature strength. If a paragraph is "X does A, Y does B, Z does C," suggest a table. If a process would be clearer as a diagram, say so. Parallel alternatives (options explored, candidate approaches, variants, rejected designs) often read better as a bulleted list than as prose.
- **Overloaded existing tables.** If a table tries to capture too many dimensions, suggest splitting into focused tables that each make one clear point.
- **Academic papers:** structure matches conventions for the paper type (empirical, systematic review, tutorial). christian-writing-style `references/academic.md` documents these.

### 3. Clarity and readability

- **Ambiguous sentences.** Two readings possible. Pronouns with unclear antecedents. Modifiers that could attach to different parts.
- **Jargon and assumed knowledge.** Terms used without explanation that the target audience might not know. Blog audience is broader than academic. In an example, ask whether the reader must understand it or only see its shape. Only the first needs vocabulary the audience already has.
- **Sentence complexity.** Sentences that try to do too much. christian-writing-style covers heavy left-branching, subject-verb separation, nominalizations.
- **Paragraph focus.** One main idea per paragraph. Split if it covers two or three. Merge if consecutive paragraphs make the same point.
- **Conciseness.** Filler ("it is worth noting that"), redundancy ("each and every"), throat-clearing ("as mentioned previously").
- **Decoding-step test.** Ask whether each precise word sits in the slot the thing itself belongs in (christian-writing-style, Name the concrete thing). Name the step the reader has to take, or it is not a finding. The sweep below runs this test over a manuscript.
- **Paragraph-tail test.** Read the last sentence of each paragraph on its own and ask what it adds beyond the paragraph. Editorial close-outs are almost always final sentences. They are invisible while reading forward because they feel like the landing. Run this as a separate pass. Following the argument hides these. Restatements go, conclusions stay (christian-writing-style, side commentary).
- **Paragraph-opening test.** Read the first clause of each paragraph on its own. Flag runs of consecutive paragraphs that open on a reaction to the material. One such opening is voice and belongs in the blog register. Three in a row means every paragraph tells the reader how to feel before saying what the thing is. The fact arrives late each time. Run it in the same pass as the tail test (christian-writing-style, `references/blog.md`).
- **Code-comment test.** Read each comment against the code it sits on and ask what a reader who skipped it would get wrong. Flag the ones where the answer is nothing. A one-line comment restates the code as easily as a four-line one. When the review covers comments or docstrings, read **code-comments** and run its scan first.

### 4. Style alignment

Consult christian-writing-style for the full specification. Common issues:

- **Wrong register.** Blog informality in an academic paper, academic stiffness in a blog post.
- **Voice drift.** Sections that shift more formal, more casual, more aggressive, or more hedged than Christian's norm.
- **Missing "why does this matter?"** Christian's writing connects technical content to real-world significance. Flag sections that present results without that connection.
- **Overclaiming or underclaiming.** Christian is measured. Watch both directions.
- **Limitations absent or thin.** Christian treats limitations as a contribution. Flag if a piece (especially academic) skips or rushes through them.

### 5. Mechanical scan

Backstop for patterns judgment alone misses. `scripts/scan.py` has the patterns and the reasoning behind each one. It exits 0 clean, 1 with hits, 2 on a usage error. `scripts/test_scan.py` pins the behavior a regex cannot state, from where a sentence boundary falls to which units have no sentence at all.

Hits come grouped by the action they need, `FIX` before `REWRITE` before `TEST`, so a find-and-replace does not sit in the same list as a call that needs judgment. Each group prints the fix or the test once, then the hits under it with the sentence around each one.

```bash
scripts/scan.py draft.md                    # prose
scripts/scan.py draft.md src/chunker.py     # any mix, routed by extension
scripts/scan.py --summary draft.md          # counts per check
scripts/scan.py --only citation paper.md    # named checks, and the only way to run citation
scripts/scan.py --skip-html-comments paper.md   # published prose, no <!-- --> notes
```

The voice checks run on everything, since a rule about his voice holds wherever the text sits. They cover:

- em-dashes, semicolons, and British spelling
- filler openers and nominalization leads
- side commentary and the this-not-that construction
- two independent clauses joined by a semicolon or by a comma and "and"
- feeling-words and layout announcements
- soft verbs used as jargon, and vocabulary that stands in for the concrete thing
- vague quantifiers, and quantities written out in words where a number belongs

The extension decides what gets read. The rules that apply are the same either way. A source file is reduced to its comment lines first, because `guard` and `canonical` are ordinary identifiers and a file-wide search buries the hits. Anything else is read as prose, with hard-wrapped lines joined so a phrase split across a line break still matches.

Source files get the three code-comments stems, jargon, dead-code, and plan-label, held back from prose because "Step 1" is a heading there. Prose gets two of its own. `specialist-term` asks the curse-of-knowledge question about the same words the jargon stem bans outright in a comment. `long-sentence` counts the words between two sentence boundaries and stays out of source files, where the comment pass reads one physical line at a time and a wrapped sentence never reaches the limit in one unit.

The em-dash check reads every line of a source file, because nothing in code needs one and the comment pass cannot see an error string or a log message. British spelling is not read that way, since it would match every word inside this script's own pattern list.

Two checks need a read instead:

- Inconsistent capitalization or spelling of recurring technical terms.
- Whether each citation key and named attribution was checked against a source, including ones you wrote yourself. A recalled one counts as unchecked. `--only citation` finds the keys but not where they came from. It stays opt-in because eighty citations in a paper would drown every other check.

Report every `FIX` and `REWRITE` hit, false positives included. Reporting them matters most during iterative editing, where corrections in one round reintroduce patterns cleaned up in the previous one.

Side commentary, the concrete-thing vocabulary, nominalization leads, soft verbs, and specialist terms fire often enough on correct prose that reporting them raw buries the real findings, since "axis" and "stack" are ordinary words in a paper about models, "Precision improved to 0.8" is not a zombie noun, and "API surface" is a noun. `dead-code-ref` is tagged for the same reason: "the target no longer exists" usually describes a missing file. So are `long-sentence`, `unquantified`, and `possession-verb`. A sentence that runs long because it enumerates is doing its job, "a few paragraphs" as a bold lead-in labels a case, and a reader left holding evidence is the idiom. Feeling-words are tagged for a different reason. One per piece is fine when the reaction is itself information, and the script cannot count across a document.

`contrastive-voice` and `comma-join` are `REWRITE`, so no test applies. The first replaced a `TEST` that asked whether a contrast was informative, which is the wrong property: on a manuscript arguing by elimination every instance passed that test and 91 still had to be restated. The judgment half of the old check lives on in `side-commentary`, whose stems reach the tails this pattern misses. The second holds to about 85% precision on a full manuscript, 22 of 26. Its false positives are a two-item list after a colon, a coordinated pair of `that` clauses, a coordinated noun phrase, and a gapped coordination. It reads `and` alone, since every other coordinator states a relationship a period would drop.

Markdown files get `--skip-html-comments`, which reads the published prose and skips `<!-- -->` notes. Use it on a drafting file. Half of one dissertation manuscript is storyline and provenance comments, and scanning them alongside the prose buried the real hits three to two.

Answer a `TEST` hit in writing whenever you decide to leave the text as it is. Quote the printed test and answer it in one line. Reasoning that never states the test drifts back to the wording the check flagged.

The sweep below reads for what no stem can state. On a manuscript, run it after this layer.

---

## The decoding-step sweep

The companion to the scan. The scan catches inflated words. This catches precise words in the wrong slot, which no regex reaches.

The three patterns are in christian-writing-style (Name the concrete thing).

**The one test.** Name the step the reader currently has to take. Christian's own diagnosis, on "Llama's median is the fastest at every stratum through 64K":

> "Llama's median" forces the reader to stop and think "median of what?". Then comes "fastest", and the reader thinks "perhaps time then?". Don't generate all this extraneous cognitive load. Simpler: "Llama's generation time".

If you cannot name a concrete decoding step, it is not a finding.

The six steps below are for a manuscript. On a section, a diff, or a blog post, the decoding-step test in layer 3 is the whole of it.

**Procedure.** One chapter at a time, one agent per chapter, run in parallel.

1. Extract the range to a scratchpad file. Scan it with `--skip-html-comments`. Expect the `FIX` hits to be false positives in a Pandoc manuscript: the multi-citation separator `[@a; @b]`, `&nbsp;` in table cells, and LaTeX spacing like `\;`. Thirty of thirty were. Triage them and answer the `TEST` groups before dispatching, so the agent does not spend findings on them.
2. Dispatch a read-only agent with the test above, the three patterns, and accepted fixes from a chapter already done. The worked examples are what keep the report at ten usable findings instead of thirty padded ones.
3. Give it four guards, or it returns a rewrite pass. Clear cases only, a word or a clause, never a paragraph restructure. Repetition is not a defect, so a restated figure never becomes a cross-reference. Precision beats brevity: units, intervals, version pins, and thresholds stay. The document's defined terms never get simplified away, so list them.
4. Verify every factual claim in the report against the source table before presenting any of it. Three of one chapter's ten rested on table arithmetic. A review agent in the same session got the arithmetic backwards. The reviewer relayed it to Christian without checking.
5. Present as a table: line, current, the step the reader takes, proposed. He strikes what he does not want.
6. Apply in one pass with `assert t.count(old) == 1` per edit, then rescan only the changed lines and answer any surviving `TEST` hit in one line.

**What the sweep is not for.** It finds no wrong claims and no missing arguments, because it never asks whether a passage should exist. Run it after the claim-level review.

---

## Presenting the review

Organize by severity. Within each severity level, give feedback in document order.

```
Review:

Must fix:
- <where>: <what>. <why>. <how>.
- ...

Should fix:
- ...

Consider:
- ...
```

- **Must fix.** Factual errors, logical flaws, missing critical content, technical mistakes.
- **Should fix.** Structural issues, unclear passages, gaps in the argument, significant style misalignments.
- **Consider.** Minor improvements, alternative phrasings, optional polish.

For every issue:

- **Where.** Quote or closely identify the passage.
- **What.** State the problem.
- **Why.** Why it's a problem (for the reader, for accuracy, for the argument).
- **How.** Suggest a fix or alternative. If multiple options, mention them briefly.

Avoid vague feedback like "this section could be improved." Say specifically what should change.

### Calibrate depth to draft length

- **A few paragraphs:** inline feedback. Walk through nearly every sentence if needed.
- **A blog post:** focus on highest-impact issues. No line-by-line edits unless asked.
- **A full paper:** start with a 2-3 sentence overall assessment, then section-by-section feedback at the paragraph level. Save sentence-level edits for passages that are actively confusing or wrong.

### What not to do

- Don't rewrite large sections unprompted. Point out the problem and suggest a direction.
- Don't pad with praise for things that are fine. Reserve positive comments for genuinely strong work worth preserving.
- Don't flag style preferences as errors. If a sentence is clear and accurate but you'd have written it differently, leave it alone.

---

## Applying changes

Two phases. First, present the full review. Stop and wait. Do not start making changes until Christian asks to proceed.

### Phase 1: Summarize all findings

Present the complete review using the severity structure above. This gives Christian the full picture so he can prioritize, push back, or skip items before edits begin.

### Phase 2: Walk through changes one at a time

When Christian is ready, work through findings as a task list. Order them logically. Severity does not set the order. Structural reorganization comes before polishing prose that will move. Factual fixes come before refining the sentences they appear in. If applying one change makes another irrelevant or requires re-doing it, put the upstream change first.

**The unit of a change is the argument.** While ordering, merge findings that are two symptoms of one argument spread across passages. They are one change: rewrite those passages together and read them back before moving on. Applied separately, each fix satisfies its own finding and breaks the pair, and the breakage shows up as a new must-fix in the next round.

For each change:

1. **Show the current text.** Quote the passage.
2. **Show the proposed change.** Revised version with a brief explanation of what changed and why.
3. **Wait for Christian's decision.** Accept, ask for a different approach, or skip.
4. **Do not move to the next finding** until Christian says he is done with the current one.

No batching. One change at a time, at his pace.

### Check what a pass deleted

Before an anchored find-and-replace, confirm the anchor begins a paragraph and matches exactly once. An anchor that matches nothing replaces nothing and still reports success.

After the pass, read every line it deleted. `-U0` drops the unchanged lines that would otherwise hide them:

```bash
git diff -U0 <commit the pass started from> -- draft.md
```

An anchor that starts mid-paragraph removes more than the edit names. The removal reads as an ordinary deletion in the diff. One such replacement dropped a sentence defining three symbols along with the display math that built them, leaving an orphan clause pointing at a section that no longer explained it. It survived three commits. A reader found it before any review did.

The baseline is the commit the pass started from, never HEAD. On a pass already committed, HEAD returns nothing, and the check reports clean on exactly the edits it exists to catch.

### Check what a pass left inconsistent

Before marking any change done, list what the pass could have left wrong: passages that were only correct because of the fact you changed, and the sentences the pass added. Grep finds the old wording. It does not find a passage that reads fine on its own and is now wrong in context, which is the failure that survives review. Find the kinds below by reading in full, and look beyond the file you edited:

- **Restatements.** Another passage states the same fact. Adding detail in one place makes the other a duplicate. Removing detail makes it the only copy. A duplicate that predates the edit is a layer 2 finding.
- **Derivations.** Another passage ranks, counts, or orders by the fact. A priority list built from a table, a total that has to sum, a count repeated in a second document.
- **Negations.** Another passage says what the fact is not, departs from it, or reconciles it with something else. Delete the fact and the negation is left denying nothing.
- **Descriptions of the passage.** A comment, storyline note, or rule that says what the passage does or how it is built. Reword the passage and the description still describes the old one. It sits inches from the text it describes and reads as background, so it survives the read that catches the others.

**Text you added is a dependent passage too.** Every kind above starts from a change you made, so a stale passage is one that disagrees with the new text. A sentence you wrote has no prior version to disagree with, and nothing about it looks stale. Read it against the constraints already governing the passage, including the ones this pass is not editing: the rules stated where it sits, the definitions of the terms it uses, and the claims on either side of it. In a source file those rules sit in the comment block around it. In a manuscript they sit in a storyline note or in the surrounding section. The rule being correct is why a sentence contradicting it stays invisible while you write.

Renames are the case a scan catches, because the old term is still sitting somewhere as a string, however hard it is to spot from inside the edit. Additions, deletions, and changed numbers are the case it misses. They leave no stale string to search for, whether the broken passage is elsewhere in the document or the sentence the pass just added.

### Responding to refinements

When Christian asks for a different approach, don't treat it as a literal instruction. Use judgment.

- His suggestion may be exactly right.
- Or it may introduce a new problem (awkward sentence, factual softening that goes too far, structural change that breaks a downstream transition).
- If a better alternative exists, present both and explain the tradeoff.
- If his suggestion creates a new issue, say so directly and propose what you'd do instead.

Goal: collaborative back-and-forth between peers.

---

## Iterated reviews

A review that follows an earlier round of edits needs a stopping rule, because the loop can sustain itself indefinitely on its own output.

**Read what a round's findings are about. The count says nothing.** If they are confined to text introduced in the previous round, the review is chasing its own churn. Consolidate in one pass, verify mechanically, and stop. Say so plainly instead of running another round: a fourth pass that finds one defect you created in the third is not evidence the work is unsound.

**Prefer a script to another read for anything countable.** Cross-document totals, references that have to resolve, a table that recomputes from its source, a term that should have exactly one phrasing. Write the check, keep it, and re-run it instead of re-reading. It costs nothing per run and does not depend on judgment, which is what fails on the fifth pass over the same paragraph.

Recompute derived numbers from the current file every time. Never adjust them by arithmetic on what you believe changed, and never reconcile two scripts by hand. Two counting methods produce two answers. The difference between them looks exactly like a real change.

---

## Retrospective

Once the editing session is done, briefly check whether the session points to a broader change. Skip if nothing came up.

- **Same issue type, multiple times?** May signal a gap in christian-writing-style. Suggest adding guidance.
- **Friction in the review process itself?** Suggest an update to text-review.
- **A new kind of writing not covered?** (Grant proposal, conference talk abstract, different audience.) Suggest expanding existing skills or creating a new one.
- **A preference revealed by Christian's refinements?** (Shorter sentences, more examples, different transition style.) Suggest codifying it in christian-writing-style.

Brief observations only. Don't manufacture meta-feedback for its own sake.
