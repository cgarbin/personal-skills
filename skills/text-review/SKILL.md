---
name: text-review
description: >-
  Review Christian's writing for accuracy, organization, and clarity: prose, the writing inside code (comments, docstrings, commit messages, PR descriptions), and sets of edits on their own, short of a whole document (a diff, an edit pass, another round after changes). Use whenever he asks to review, critique, proofread, or give feedback on anything already written, down to a single comment or a single edit, including casual asks like "check this" or "does this read well". Always use with the christian-writing-style skill.
---

# Text Review

How to review Christian's writing: what to examine, in what order, and how to present feedback. For voice, tone, sentence patterns, and formatting conventions, consult **christian-writing-style**.

Always load **christian-writing-style** alongside this skill, plus the reference file for the register under review: `christian-writing-style/references/blog.md`, `christian-writing-style/references/academic.md`, or both for the blended register. Short snippets need neither. Several checks below cite rules that live only in those files.

---

## Before you start

Settle the draft stage and the scope before you start. The register comes from christian-writing-style's routing, which the paragraph above already sends you to.
- **Draft stage.** Ask if unclear. Early drafts: feedback on structure, argument, missing pieces. Late drafts: sentence-level editing and polish. Reviewing an early draft for comma placement wastes time. Reviewing a final draft without checking the argument is worse.
- **Scope.** A whole document, or a single comment, commit subject, or paragraph. A snippet needs the mechanical scan and, for comments, the code-comment test. Layers 2 and 4, the two-phase gate, and the paragraph tests in layer 3 all assume a document. A single comment has no paragraphs. Layer 1 runs on a snippet, since a comment or a commit subject can state a false fact in one line, and so does the pointer test, since one sentence is enough to point at a noun that is not there.

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

**Memory-sourced citations are unverified by default.** A citation written from recall is not a checked citation, even when it looks precise and turns out to be right. Author lists, years, journal names, page numbers, book titles, and "X coined this" claims feel certain and are often wrong by one name or one year. Flag every citation *you* wrote from recall as Must fix. For the ones already on the page, ask once which were checked instead of flagging each. If checking isn't possible now, suggest marking it unverified in the text, which leaving it alone does not.

One related check:
- **Primary versus secondary sourcing.** If claims about a work come from summaries, reviews, or interviews, suggest the piece say so. A short "sources and confidence" note at the end tells a future reader which claims are safe to cite onward.

### 2. Argument and organization

- **Clear purpose.** Can you state the takeaway in one sentence? If not, the piece may be doing too many things.
- **Structure serves the argument.** Sections in logical sequence, each building on what came before. If you have to re-read a section because it depends on something introduced later, the order is wrong.
- **Gaps.** Places where the reader would ask "but what about...?" or "why?" and the text doesn't answer.
- **Unnecessary material.** Sections, paragraphs, sentences that don't contribute. Tangents. Background the audience already knows.
- **Two copies of a fact need a mechanism.** Say which copy goes, or what check fails when they diverge. A comment asking a human to keep them in step is not a mechanism. In one paper repository, figure scripts held captions copied from the paper, and two tables shared a column with an HTML comment asking an editor to keep them synchronized. Both had drifted by the time anyone checked.
- **Transitions.** Each section connects to the next. Reader can follow opening to conclusion without getting lost.
- **Tables, figures, lists.** Look for places where prose does work that structure would do better: comparisons across multiple items, step-by-step processes, chronological progressions, dense numerical results. If a paragraph is "X does A, Y does B, Z does C," suggest a table. If a process would be clearer as a diagram, say so. Parallel alternatives read better as a list (christian-writing-style, Show, don't tell).
- **Overloaded existing tables.** If a table tries to capture too many dimensions, suggest splitting into focused tables that each make one clear point.
- **Academic papers:** structure matches conventions for the paper type (empirical, systematic review, tutorial). christian-writing-style `references/academic.md` documents these.

### 3. Clarity and readability

- **Ambiguous sentences.** Two readings possible. Modifiers that could attach to different parts.
- **Jargon and assumed knowledge.** Terms used without explanation that the target audience might not know. Blog audience is broader than academic. An example is a separate case (christian-writing-style, Fight the curse of knowledge).
- **Sentence complexity.** Sentences that try to do too much. christian-writing-style covers heavy left-branching, subject-verb separation, nominalizations.
- **Paragraph focus.** One main idea per paragraph. Split if it covers two or three. Merge if consecutive paragraphs make the same point.
- **Conciseness.** Filler ("it is worth noting that"), redundancy ("each and every"), throat-clearing ("as mentioned previously").
- **Decoding-step test.** Ask whether each precise word sits in the slot the thing itself belongs in (christian-writing-style, Name the concrete thing). Name the step the reader has to take, or it is not a finding. The sweep below runs this test over a manuscript.
- **Paragraph-tail test.** Read the last sentence of each paragraph on its own and ask what it adds beyond the paragraph. Editorial close-outs are almost always final sentences. They are invisible while reading forward because they feel like the ending. Run this as a separate pass. Restatements go, conclusions stay (christian-writing-style, side commentary).
- **Paragraph-opening test.** Read the first clause of each paragraph on its own. One opening on a reaction to the material is voice and belongs in the blog register. Two in a section is the rate `references/blog.md` calls a tic, so flag the second and any after it. Run it in the same pass as the tail test (christian-writing-style, `references/blog.md`).
- **Pointer test.** Name the noun each pointer word points at (christian-writing-style, Point at a noun). Concentrate on the pointers whose noun has to come from an earlier sentence, since a pointer resolved inside its own sentence is visible at a glance. Flag the pointers whose nearest noun is something else, and those with no noun to find anywhere. Run it in the same pass as the tail test. Reading forward supplies the referent from what the passage means, so a pointer that resolves to the wrong noun reads correctly to everyone who already knows the answer, the writer first. The `pointer` check covers part of this ground. `references/scan.md` says which part.
- **Code-comment test.** Read each comment against the code it sits on and ask what a reader who skipped it would get wrong. Flag the ones where the answer is nothing. When the review covers comments or docstrings, read **code-comments** and run its scan first.

### 4. Style alignment

christian-writing-style is the specification. The checks below need the whole piece in view.

- **Voice drift.** Sections that shift more formal, more casual, more aggressive, or more hedged than the rest of the piece.
- **Overclaiming or underclaiming.** Christian is measured, so watch both directions. A hedge in the abstract and a flat assertion in the discussion are each defensible alone.
- **Missing "why does this matter?"** Christian's writing connects technical content to real-world significance. Name the sections that present results without it.
- **Limitations absent or thin.** Christian treats limitations as a contribution. Flag if a piece (especially academic) skips or rushes through them.

### 5. Mechanical scan

Backstop for patterns judgment alone misses. `scripts/scan.py` has the patterns and the reasoning behind each one. It exits 0 clean, 1 with hits, 2 on a usage error. A path that is not a file is skipped with a note on stderr and does not change the status, so a typo reads as a clean scan. On a standard install it sits at `~/.claude/skills/text-review/scripts/scan.py`.

```bash
scripts/scan.py draft.md                    # prose
scripts/scan.py draft.md src/chunker.py     # any mix, routed by extension
scripts/scan.py --summary draft.md          # counts per check
scripts/scan.py --only citation paper.md    # named checks, and the only way to run citation
scripts/scan.py --skip-html-comments paper.md   # published prose, no <!-- --> notes
```

Hits come grouped by the action they need, `FIX` before `REWRITE` before `TEST`, so a find-and-replace does not sit in the same list as a call that needs judgment. Each group prints the fix or the test once, then the hits under it with the sentence around each one, and a `see` line pointing at the rule behind the check. The line number points at the start of the prose unit holding the hit, so quote the sentence when you report it.

`FIX` and `REWRITE` hits print no test, and they still misfire on markup. A Pandoc citation separator, a semicolon inside a code fence or a shell command, an HTML entity in a table cell, and the contrastive comment a repo mandates in SQL (**code-comments** rule 10) all fire. Confirm the hit is prose before you edit it. A `TEST` hit prints the test to apply before you decide. Answer it in writing whenever you decide to leave the text as it is: quote the printed test and answer it in one line. Reasoning that never states the test drifts back to the wording the check flagged.

The voice checks run on everything, since a rule about his voice holds wherever the text sits. Each hit names its check and prints a `see` line to the rule behind it, so the inventory lives in the output and in `references/scan.md`.

The extension picks the rest. A source file gets the code-comments stems, and prose gets the sentence-length and specialist-term checks. `references/scan.md` has the routing in full, the checks that fire on correct prose and why, and the reasoning behind `contrastive-voice` and `comma-join`. Read it when a hit does not make sense.

Markdown drafting files get `--skip-html-comments`. Scanning storyline and provenance notes alongside the prose buries the real hits.

Two checks need a read instead:

- Inconsistent capitalization or spelling of recurring technical terms.
- Whether each citation key and named attribution was checked against a source, including ones you wrote yourself. A recalled one counts as unchecked. `--only citation` finds the keys but not where they came from. It stays opt-in because eighty citations in a paper would drown every other check.

Report every `FIX` and `REWRITE` hit, false positives included. Reporting them matters most during iterative editing, where corrections in one round reintroduce patterns cleaned up in the previous one. `TEST` hits are the other case: several of those checks fire routinely on correct prose, so read `references/scan.md` before reporting a batch of them as findings.

---

## The decoding-step sweep

The companion to the scan. The scan catches inflated words. This catches precise words in the wrong slot, which no regex reaches. The test is the one in layer 3, and a section, a diff, or a blog post needs nothing more.

A whole manuscript needs the procedure in `references/decoding-sweep.md`: what to triage before dispatching, the guards that keep an agent from returning a rewrite pass, and the verification step between its report and Christian.

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
- **Consider.** Minor improvements, alternative phrasings, optional polish. A scan hit you judged a false positive goes here, with the answer to its test.

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
- Don't flag style preferences as errors. If a sentence is clear and accurate but you'd have written it differently, leave it alone. A scan hit is not a style preference, and layer 5 says what to do with one.

---

## Applying changes

Two phases. First, present the full review. Stop and wait. Do not start making changes until Christian asks to proceed.

**Two ways to work through the findings.** Phase 2 below walks one finding at a time and waits on each, which is right when every finding needs its own call. A sweep that finds one pattern repeated across a manuscript needs the other shape: present the instances as a table, let him strike what he does not want, and apply the survivors in one pass. One restatement sweep ran to 91 instances. Asking about each would have cost more attention than reading the manuscript. The decoding-step sweep above uses the table form for that reason.

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

The baseline is the commit the pass started from, which stops being HEAD once the pass itself is committed. On a pass already committed, HEAD returns nothing, and the check reports clean on exactly the edits it exists to catch.

### Check what a pass left inconsistent

Before marking any change done, list what the pass could have left wrong: passages that were only correct because of the fact you changed, and the sentences the pass added. Grep finds the old wording. It does not find a passage that reads fine on its own and is now wrong in context, which is the failure that survives review. Find the kinds below by reading in full, and look beyond the file you edited:

- **Restatements.** Another passage states the same fact. Adding detail in one place makes the other a duplicate. Removing detail makes it the only copy. A duplicate that predates the edit is a layer 2 finding.
- **Derivations.** Another passage ranks, counts, or orders by the fact. A priority list built from a table, a total that has to sum, a count repeated in a second document.
- **Negations.** Another passage says what the fact is not, departs from it, or reconciles it with something else. Delete the fact and the negation is left denying nothing.
- **Descriptions of the passage.** A comment, storyline note, or rule that says what the passage does or how it is built. Reword the passage and the description still describes the old one. It sits inches from the text it describes and reads as background, so it survives the read that catches the others.

**Text you added is a dependent passage too.** Every kind above starts from a change you made, so a stale passage is one that disagrees with the new text. A sentence you wrote has no prior version to disagree with, and nothing about it looks stale. Read it against the constraints already governing the passage, including the ones this pass is not editing: the rules stated where it sits, the definitions of the terms it uses, and the claims on either side of it. In a source file those rules sit in the comment block around it. In a manuscript they sit in a storyline note or in the surrounding section. The rule being correct is why a sentence contradicting it stays invisible while you write.

**Fix a stale reference by removing what can go stale.** A count that drifted ("three kinds" against a four-item list) is not fixed by correcting the number, because the same trap stays set for the next edit. Write "the kinds below" or "every kind above". The count was only ever signaling that a list follows. The list does that itself. Apply it to every count in the passage, including the ones that still read correctly. A count the reader checks against is the exception, such as the guards an agent has to receive in full. Then check whether dropping a count orphaned an antecedent: "Three kinds. Find them" loses its referent when the three goes.

Renames are the case a scan catches, because the old term is still sitting somewhere as a string, however hard it is to spot from inside the edit. Additions, deletions, and changed numbers are the case it misses. They leave no stale string to search for, whether the broken passage is elsewhere in the document or the sentence the pass just added.

### Responding to refinements

When Christian asks for a different approach, don't treat it as a literal instruction. Use judgment.

- His suggestion may be exactly right.
- Or it may introduce a new problem (awkward sentence, factual softening that goes too far, structural change that breaks a transition later in the document).
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
- **A new kind of writing not covered?** (Conference talk abstract, a different audience.) Suggest expanding existing skills or creating a new one.
- **A preference revealed by Christian's refinements?** (Shorter sentences, more examples, different transition style.) Suggest codifying it in christian-writing-style.

Brief observations only. Don't manufacture meta-feedback for its own sake.
