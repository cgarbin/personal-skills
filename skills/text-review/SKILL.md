---
name: text-review
description: >-
  Review Christian's writing for accuracy, organization, and clarity: prose, the writing inside code (comments, docstrings, commit messages, PR descriptions), and sets of edits rather than whole documents (a diff, an edit pass, another round after changes). Use whenever he asks to review, critique, proofread, or give feedback on anything already written, down to a single comment or a single edit, including casual asks like "check this" or "does this read well". Always use with the christian-writing-style skill.
---

# Text Review

How to review Christian's writing: what to examine, in what order, and how to present feedback. For voice, tone, sentence patterns, and formatting conventions, consult **christian-writing-style**.

Always load **christian-writing-style** alongside this skill, plus the reference file for the register under review: `references/blog.md` or `references/academic.md`. Short snippets need neither. Several checks below cite rules that live only in those files.

---

## Before you start

Determine the register (blog, academic, or short snippets) and the draft stage. Both shape what feedback is useful.

- **Register.** Blog post, journal paper, email, commit message? christian-writing-style routes these at the top of its SKILL.md.
- **Draft stage.** Ask if unclear. Early drafts: feedback on structure, argument, missing pieces. Late drafts: sentence-level editing and polish. Reviewing an early draft for comma placement wastes time. Reviewing a final draft without checking the argument is worse.

**Reviewing an edit pass is not reviewing a draft.** When the subject is a set of changes rather than a document, read each changed passage together with the passages that depend on it, in full and in order, whether or not they changed. "Check consumers, not just usages" under Applying changes names the three kinds of dependent passage to look for. A diff shows the side that changed and hides the side that depended on it, so coupling breakage is invisible from the diff by construction.

---

## Review layers

Work through these in order. Each builds on the previous.

### 1. Accuracy and technical correctness

The most important layer. Elegant prose built on wrong claims is worse than clunky prose built on right ones.

- **Factual claims.** Verify statements about specific numbers, dates, algorithms, papers, results. Flag anything that looks wrong or that you can't verify.
- **Technical terminology.** Used correctly and consistently? Watch for terms that are close but not quite right, or that shift meaning between paragraphs.
- **Citations and attributions.** Do cited sources actually say what the text claims? Are ideas attributed correctly? Claims that need a citation but lack one? Three failure modes to watch:
  - Crediting a popularizer instead of the originator.
  - Naming a real source that argues something adjacent, not the claim being made.
  - Verbs that overstate how settled the evidence is ("X established that" when X argued it, or when it stays contested).
- **Logic and reasoning.** Argument holds together? Watch for unstated assumptions, logical jumps, conclusions that don't follow from evidence, correlation-causation conflation, overgeneralization.
- **Numbers and data.** Add up? Percentages consistent with raw counts? Fair comparisons (same baseline, same conditions)?

**Memory-sourced citations are unverified by default.** A citation written from recall is not a checked citation, even when it looks precise and turns out to be right. Author lists, years, journal names, page numbers, book titles, and "X coined this" claims feel certain and are often wrong by one name or one year. Flag every one as Must fix, including citations *you* wrote. If checking isn't possible now, suggest marking it unverified in the text rather than leaving it looking settled.

Two related checks:

- **"Needs a source" versus "has a source nobody checked."** Different problems, different fixes, and the second one hides better.
- **Primary versus secondary sourcing.** If claims about a work come from summaries, reviews, or interviews rather than the work, suggest the piece say so. A short "sources and confidence" note at the end tells a future reader which claims are safe to cite onward.

### 2. Argument and organization

- **Clear purpose.** Can you state the takeaway in one sentence? If not, the piece may be doing too many things.
- **Structure serves the argument.** Sections in logical sequence, each building on what came before. If you have to re-read a section because it depends on something introduced later, the order is wrong.
- **Gaps.** Places where the reader would ask "but what about...?" or "why?" and the text doesn't answer.
- **Unnecessary material.** Sections, paragraphs, sentences that don't contribute. Tangents. Background the audience already knows.
- **Transitions.** Each section connects to the next. Reader can follow opening to conclusion without getting lost.
- **Tables, figures, lists.** Look for places where prose does work that structure would do better: comparisons across multiple items, step-by-step processes, chronological progressions, dense numerical results. Christian's tables are a signature strength. If a paragraph is "X does A, Y does B, Z does C," suggest a table. If a process would be clearer as a diagram, say so. Parallel alternatives (options explored, candidate approaches, variants, rejected designs) often read better as a bulleted list than as prose.
- **Overloaded existing tables.** If a table tries to capture too many dimensions, suggest splitting into focused tables that each make one clear point.
- **Academic papers:** structure matches conventions for the paper type (empirical, systematic review, tutorial). christian-writing-style `references/academic.md` documents these.

### 3. Clarity and readability

- **Ambiguous sentences.** Two readings possible. Pronouns with unclear antecedents. Modifiers that could attach to different parts.
- **Jargon and assumed knowledge.** Terms used without explanation that the target audience might not know. Blog audience is broader than academic.
- **Sentence complexity.** Sentences that try to do too much. christian-writing-style covers heavy left-branching, subject-verb separation, nominalizations.
- **Paragraph focus.** One main idea per paragraph. Split if it covers two or three. Merge if consecutive paragraphs make the same point.
- **Conciseness.** Filler ("it is worth noting that"), redundancy ("each and every"), throat-clearing ("as mentioned previously").
- **Paragraph-tail test.** Read the last sentence of each paragraph on its own and ask what it adds beyond the paragraph. Editorial close-outs are almost always final sentences, and they are invisible while reading forward because they feel like the landing. Run this as a separate pass, not while following the argument. Restatements go, conclusions stay (christian-writing-style, side commentary).
- **Paragraph-opening test.** Read the first clause of each paragraph on its own. Flag runs of consecutive paragraphs that open on a reaction to the material rather than on the material. One such opening is voice and belongs in the blog register. Three in a row means every paragraph tells the reader how to feel before saying what the thing is, and the fact arrives late each time. Run it in the same pass as the tail test (christian-writing-style, `references/blog.md`).
- **Code-comment test.** Read each comment against the code it sits on and ask what a reader who skipped it would get wrong. Flag the ones where the answer is nothing. A one-line comment restates the code as easily as a four-line one (christian-writing-style, Short snippets). When the review covers comments or docstrings, read **code-comments** and run its scan first.

### 4. Style alignment

Consult christian-writing-style for the full specification. Common issues:

- **Wrong register.** Blog informality in an academic paper, academic stiffness in a blog post.
- **Voice drift.** Sections that shift more formal, more casual, more aggressive, or more hedged than Christian's norm.
- **Missing "why does this matter?"** Christian's writing connects technical content to real-world significance. Flag sections that present results without that connection.
- **Overclaiming or underclaiming.** Christian is measured. Watch both directions.
- **Limitations absent or thin.** Christian treats limitations as a contribution. Flag if a piece (especially academic) skips or rushes through them.

### 5. Mechanical scan

Backstop for patterns judgment alone misses. Cheap to search for.

- Em-dashes in prose (Christian doesn't use them in his own writing).
- Semicolons in prose (pseudo-code or table semicolons excepted).
- British spelling (*analyse*, *colour*, *behaviour*, *modelling*, *-ise*, *centre*, *defence*). Flag every occurrence.
- Nominalization markers at sentence start (-tion, -ment, -ance when the sentence could start with a verb).
- Filler openers and single-word paragraph leads ("Interpretation.", "Interestingly,", "Note that", "It is worth noting").
- Side commentary. Grep word stems, not full phrases. This family reappears in new wording each time, so a literal phrase catches one instance and never fires again. `deliberat`, `intentional`, `on purpose`, `by design`, `we do not claim`, `does not (claim|argue)`, `(attributes|makes|takes) no`, `rather than the reverse`, `the other way around`, `not just`, `which is worth`, `That is the`. Unlike the rest of this list, judge these before reporting: delete the clause and reread. If no fact, number, constraint, or claim is lost, the deletion stands. See christian-writing-style on side commentary.
- Empty contrastive tails. Grep `,\snot\s` and `\srather\sthan\s`, then keep only the short-tail form where the contrast is the whole clause and sits at the end of a sentence ("One gate, not two"). The stems above catch fixed phrasings. This catches the bare construction, which reappears in new words each time. Expect a high false-positive rate, since most hits will be mid-sentence contrasts that have real content. Bold lead-in labels ("Restatements go, conclusions stay") are a house pattern, not hits. Judge before reporting: keep the contrast only when the alternative was actually tried, a reader would plausibly assume it, or the argument depends on ruling it out.
- Feeling-words spent on a fact: `uncomfortable`, `surprising`, `surprised`, `striking`, `remarkable`. One per piece is fine when the reaction is itself information. Flag the second.
- Layout announcements: "the rest of this section", "the sections below", "what the table cannot hold", "each item gets". A table followed by per-item sections needs no sentence describing it.
- Vocabulary that stands in for the concrete thing: `land`/`lands`/`landed` as a verb for where things end up, `carr(y|ies|ied)` for what text or code conveys, `stack`, `arm`, `frontier`, `axes`, `lever`, `downstream`.
- Vague quantifiers where a number exists: "elevated", "tighten", "various factors", "had issues", "up" without a value.
- Inconsistent capitalization or spelling of recurring technical terms.
- Every citation key (`[@`) and every named attribution. Confirm each was checked against a source rather than recalled, including ones you wrote yourself.

Flag every hit, even false positives, except for side commentary and empty contrastive tails. Those two fire often enough on legitimate prose that reporting them raw buries the real findings, so judge them first. Flagging the rest matters most during iterative editing, where corrections in one round can reintroduce patterns cleaned up in the previous round. Save the scan as a script and re-run it each round rather than repeating it by hand (see Iterated reviews).

---

## Presenting the review

Organize by severity, not by layer. Within each severity level, give feedback in document order.

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

When Christian is ready, work through findings as a task list. Order them logically, not by severity. Structural reorganization comes before polishing prose that will move. Factual fixes come before refining the sentences they appear in. If applying one change makes another irrelevant or requires re-doing it, put the upstream change first.

**The unit of a change is the argument, not the sentence.** While ordering, merge findings that are two symptoms of one argument spread across passages. They are one change: rewrite those passages together and read them back before moving on. Applied separately, each fix satisfies its own finding and breaks the pair, and the breakage surfaces as a new must-fix in the next round.

For each change:

1. **Show the current text.** Quote the passage.
2. **Show the proposed change.** Revised version with a brief explanation of what changed and why.
3. **Wait for Christian's decision.** Accept, ask for a different approach, or skip.
4. **Do not move to the next finding** until Christian says he is done with the current one.

No batching. One change at a time, at his pace. If he stops partway through, the remaining items aren't going anywhere.

### Check consumers, not just usages

Before marking any change done, list what was only correct because of the fact you just changed. Grep finds the old wording. It does not find a passage that reads fine on its own and is now wrong in context, which is the failure that survives review. Three kinds. Find them by reading in full rather than grepping, and look beyond the file you edited:

- **Restatements.** Another passage states the same fact. Adding detail in one place makes the other a duplicate. Removing detail makes it the only copy.
- **Derivations.** Another passage ranks, counts, or orders by the fact. A priority list built from a table, a total that has to sum, a count repeated in a second document.
- **Negations.** Another passage says what the fact is not, departs from it, or reconciles it with something else. Delete the fact and the negation is left denying nothing.

Renames are the easy case, and the one a scan catches: updating a heading and leaving the old term in the body is hard to see from inside the edit. Additions, deletions, and changed numbers break consumers without leaving a stale string anywhere.

### Responding to refinements

When Christian asks for a different approach, don't treat it as a literal instruction. Use judgment.

- His suggestion may be exactly right.
- Or it may introduce a new problem (awkward sentence, factual softening that goes too far, structural change that breaks a downstream transition).
- If a better alternative exists, present both and explain the tradeoff.
- If his suggestion creates a new issue, say so directly and propose what you'd do instead.

Goal: collaborative back-and-forth between peers, not order-taking.

---

## Iterated reviews

A review that follows an earlier round of edits needs a stopping rule, because the loop can sustain itself indefinitely on its own output.

**Read what a round's findings are about, not how many there are.** If they are confined to text introduced in the previous round, the review is chasing its own churn rather than the work. Consolidate in one pass, verify mechanically, and stop. Say so plainly rather than running another round: a fourth pass that finds one defect you created in the third is not evidence the work is unsound.

**Prefer a script to another read for anything countable.** Cross-document totals, references that have to resolve, a table that recomputes from its source, a term that should have exactly one phrasing. Write the check, keep it, and re-run it instead of re-reading. It costs nothing per run and does not depend on judgment, which is what fails on the fifth pass over the same paragraph.

Recompute derived numbers from the current file every time. Never adjust them by arithmetic on what you believe changed, and never reconcile two scripts by hand. Two counting methods produce two answers, and the difference between them looks exactly like a real change.

---

## Retrospective

Once the editing session is done, briefly check whether the session points to a broader change. Skip if nothing surfaced.

- **Same issue type, multiple times?** May signal a gap in christian-writing-style. Suggest adding guidance.
- **Friction in the review process itself?** Suggest an update to text-review.
- **A new kind of writing not covered?** (Grant proposal, conference talk abstract, different audience.) Suggest expanding existing skills or creating a new one.
- **A preference revealed by Christian's refinements?** (Shorter sentences, more examples, different transition style.) Suggest codifying it in christian-writing-style.

Brief observations only. Don't manufacture meta-feedback for its own sake.
