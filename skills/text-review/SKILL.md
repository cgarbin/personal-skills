---
name: text-review
description: "Review and critique written text for accuracy, technical correctness, organization, and clarity. Use this skill whenever Christian asks you to review, critique, proofread, edit, or give feedback on something he's written, whether it's a paragraph, a blog post draft, or a full academic paper. Also trigger when he says 'check this', 'does this read well', 'review my draft', 'what do you think of this text', or anything that involves evaluating existing prose rather than writing new prose from scratch. Always use this skill together with the christian-writing-style skill."
---

# Text Review

This skill defines how to review Christian's writing. It covers the review *process*: what to examine, in what order, and how to present feedback. For questions about Christian's voice, tone, sentence patterns, and formatting conventions, consult the **christian-writing-style** skill. That skill is the authority on what Christian's writing should sound like. This skill is the authority on how to evaluate whether a piece of writing is working.

Always load the **christian-writing-style** skill alongside this one. The review depends on it for style judgments.

---

## Before you start

Determine the register (blog or academic) and the stage of the draft. Both affect what kind of feedback is most useful.

**Register.** Is this a blog post, a journal paper, an email? The christian-writing-style skill defines the two registers and when each applies. The register determines which structural and tonal expectations to evaluate against.

**Draft stage.** Ask if it's not clear. Early drafts benefit from feedback on structure, argument, and missing pieces. Late drafts benefit from sentence-level editing and polish. Reviewing an early draft for comma placement wastes everyone's time. Reviewing a final draft without checking the argument is worse.

---

## Review layers

Work through these layers in order. Each layer builds on the previous one. If the argument has a logical gap, fixing the prose around it is premature.

### 1. Accuracy and technical correctness

This is the most important layer. Elegant prose built on wrong claims is worse than clunky prose built on right ones.

What to check:

- **Factual claims.** Are statements of fact correct? If a claim is about a specific number, date, algorithm, paper, or result, verify it if possible. Flag anything that looks wrong or that you can't verify.
- **Technical terminology.** Are terms used correctly and consistently? Watch for subtle misuses: terms that are close but not quite right, or that shift meaning between paragraphs.
- **Citations and attributions.** Do cited sources actually say what the text claims they say? Are ideas attributed to the right people? Are there claims that need a citation but don't have one?
- **Logic and reasoning.** Does the argument hold together? Are there unstated assumptions, logical jumps, or conclusions that don't follow from the evidence presented? Watch for correlation-causation conflation and overgeneralization from limited evidence.
- **Numbers and data.** Do the numbers add up? Are percentages consistent with the raw counts? Are comparisons fair (same baseline, same conditions)?

How to flag issues: Be specific. Don't say "this might be wrong." Say what the issue is, why you think it's an issue, and what the correct version might be (or that you're uncertain and it needs checking).

### 2. Argument and organization

Once the facts are solid, look at how they're arranged.

What to check:

- **Does it have a clear purpose?** Can you state in one sentence what the reader should take away? If not, the piece may be trying to do too many things.
- **Does the structure serve the argument?** Sections should follow a logical sequence, each one building on what came before. If you have to re-read a section because it depends on something introduced later, the order is wrong.
- **Are there gaps?** Places where the reader would ask "but what about...?" or "why?" and the text doesn't answer. Missing context, skipped steps, or objections that aren't addressed.
- **Is there unnecessary material?** Sections, paragraphs, or sentences that don't contribute to the main point. Tangents that go too far. Background that the audience already knows.
- **Do transitions work?** Does each section connect to the next? Can you follow the thread from opening to conclusion without getting lost?
- **Opportunities for tables, figures, or lists.** Look for places where prose is doing work that structure would do better: comparisons across multiple items, step-by-step processes, chronological progressions, or dense numerical results. Christian uses tables heavily (especially comparison and summary tables) and they are a signature strength of his writing. If a paragraph is essentially a list of "X does A, Y does B, Z does C," suggest a table. If a process is described in prose but would be clearer as a diagram, say so. The same principle applies to bulleted lists: when a paragraph describes several parallel alternatives (options explored, candidate approaches, variants, rejected designs), a bulleted list often reads better than prose. Prose hides the parallel structure. A list makes it scannable.
- **Overloaded existing tables.** Review tables already in the draft. If one has too many columns or tries to capture too many dimensions at once, suggest splitting it into focused tables that each make one clear point.
- **For academic papers specifically:** Does the structure match the conventions for the paper type (empirical, systematic review, tutorial)? The christian-writing-style skill documents these structures. Check the draft against the appropriate template.

### 3. Clarity and readability

Now look at how individual ideas are expressed.

What to check:

- **Ambiguous sentences.** Sentences where two readings are possible. Pronouns with unclear antecedents. Modifiers that could attach to different parts of the sentence.
- **Jargon and assumed knowledge.** Terms or concepts used without explanation that the target audience might not know. Remember: the target audience for blog posts is broader than for academic papers.
- **Sentence complexity.** Sentences that try to do too much. The christian-writing-style skill's craft principles (from Pinker) cover this in detail: heavy left-branching, subject-verb separation, and nominalizations are the usual culprits.
- **Paragraph focus.** Each paragraph should have one main idea. If a paragraph covers two or three ideas, suggest splitting it. If consecutive paragraphs make the same point, suggest merging them.
- **Conciseness.** Words and phrases that don't earn their place. Filler ("it is worth noting that"), redundancy ("each and every"), and throat-clearing ("as mentioned previously").

### 4. Style alignment

Finally, check that the writing sounds like Christian. Consult the christian-writing-style skill for the full specification. The most common issues to watch for:

- **Wrong register.** Blog-style informality in an academic paper, or academic stiffness in a blog post.
- **Voice drift.** Sections that shift into a different voice: more formal, more casual, more aggressive, or more hedged than Christian's norm.
- **Missing "why does this matter?"** Christian's writing almost always connects technical content to real-world significance. If a section presents results or findings without this connection, flag it.
- **Overclaiming or underclaiming.** Christian is measured. He doesn't hype and he doesn't hedge excessively. Watch for both directions.
- **Limitations absent or thin.** Christian treats limitations as a genuine contribution. If a piece (especially an academic one) skips or rushes through limitations, flag it.

### 5. Mechanical scan

Before finalizing the review, run a mechanical pass for patterns that judgment alone misses. These are cheap to search for and easy to forget:

- Em-dashes in prose (Christian does not use them in his own writing).
- Semicolons in prose (pseudo-code or table-structure semicolons excepted).
- Nominalization markers at sentence start (-tion, -ment, -ance when the sentence could start with a verb).
- Filler openers and single-word paragraph leads ("Interpretation.", "Interestingly,", "Note that", "It is worth noting").
- Inconsistent capitalization or spelling of recurring technical terms.

Flag every hit, even if some turn out to be false positives. A mechanical scan is the backstop for layers 1 through 4. It is especially important during iterative editing, where corrections made in one round can reintroduce the patterns that were cleaned up in the last one.

---

## Presenting the review

Structure the review so Christian can act on it efficiently.

### Organize by severity, not by layer

Don't present four separate layer-by-layer sections. Instead, group the feedback by how urgently it needs attention:

1. **Must fix.** Factual errors, logical flaws, missing critical content, technical mistakes. Things that would undermine the piece if left in.
2. **Should fix.** Structural issues, unclear passages, gaps in the argument, significant style misalignments. Things that weaken the piece.
3. **Consider.** Minor improvements, alternative phrasings, optional restructuring suggestions, polish. Things that would make a good piece better.

Within each severity level, give feedback in document order so it's easy to walk through the text alongside the review.

### Be specific and actionable

For every issue, provide:

- **Where.** Quote or closely identify the passage so there's no ambiguity about what you're referring to.
- **What.** State the problem clearly.
- **Why.** Explain why it's a problem (for the reader, for accuracy, for the argument).
- **How.** Suggest a fix or an alternative. If there are multiple options, mention them briefly.

Avoid vague feedback like "this section could be improved" or "consider reworking this." Say what specifically should change and why.

### Calibrate depth to draft length

- **A few paragraphs:** Inline feedback is fine. Walk through nearly every sentence if needed.
- **A blog post:** Focus on the highest-impact issues. Call out specific passages but don't do a line-by-line edit unless asked.
- **A full paper:** Start with a brief overall assessment (2–3 sentences on the paper's main strengths and weaknesses). Then give section-by-section feedback at the paragraph level. Save sentence-level edits for passages that are actively confusing or wrong.

### What not to do

- Don't rewrite large sections unprompted. Point out the problem and suggest a direction. Christian will rewrite it himself.
- Don't pad the review with praise for things that are fine. If a section works well and there's nothing to say about it, skip it. Reserve positive comments for things that are genuinely strong and worth preserving (especially if they might otherwise get cut in a revision).
- Don't flag style preferences as errors. If a sentence is clear and accurate but you'd have written it differently, leave it alone.

---

## After the review: applying changes

The review has two distinct phases. First, present the full summary of findings. Then stop and wait. Do not start making changes until Christian asks to proceed.

### Phase 1: Summarize all findings

Present the complete review using the severity structure above (must fix / should fix / consider). This gives Christian the full picture so he can prioritize, push back, or skip items before any edits begin.

### Phase 2: Walk through changes one at a time

When Christian is ready to apply changes, work through the findings as a task list. Before starting, order the items logically, not necessarily by severity. Some changes depend on others: a structural reorganization should come before polishing the prose that will move, and fixing a factual error should come before refining the sentence it appears in. If applying one change would make another one irrelevant or would require re-doing it, put the upstream change first. Christian prefers to stay in control of the process:

1. **Show the current text.** Quote the passage as it stands now.
2. **Show the proposed change.** Present the revised version alongside a brief explanation of what changed and why.
3. **Wait for Christian's decision.** He will either accept the change, ask for a different approach, or skip it entirely.
4. **Do not move to the next finding** until Christian says he is done with the current one.

This means no batching, no "here are the next three changes." One finding at a time, at Christian's pace. If he wants to stop partway through the list, that's fine. The remaining items aren't going anywhere.

When a change renames a term, reframes a decision, or deprecates a concept, scan the full document for residual usages before marking the change done. A change that updates a heading but leaves the old term in the body creates confusion that is hard to see from inside the edit. Deprecations often cascade. Ruling out a whole approach may require removing references across several sections, not just the one Christian flagged.

### Responding to Christian's refinements

When Christian asks for a different approach or suggests a revision, don't treat it as a literal instruction to execute. Use your judgment. His suggestion might be exactly right, but it might also introduce a new problem: an awkward sentence, a factual softening that goes too far, a structural change that breaks a transition downstream. Think through the implications before applying it. If his suggestion would work but a better alternative exists, present both and explain the tradeoff. If his suggestion would create a new issue, say so directly and propose what you'd do instead. The goal is a collaborative back-and-forth between peers, not order-taking.

---

## After the editing session: retrospective

Once the review and editing work is done, take a step back and consider whether anything that came up during the session points to a broader change. This is a brief, lightweight check, not a full audit.

Ask yourself:

- **Did the same type of issue come up multiple times?** If the review flagged the same problem in several places (e.g., repeated nominalizations, consistently missing "why does this matter?" sections, a pattern of overclaiming), that might signal a gap in the christian-writing-style skill. Suggest adding guidance to prevent the pattern at the source.
- **Did the review process itself have friction?** If something about the review layers, the severity categories, or the change workflow felt wrong or missing during this session, suggest an update to this skill (text-review).
- **Did a new kind of writing come up that the skills don't cover?** For example, a grant proposal, a conference talk abstract, or a different audience than the skills anticipate. If so, suggest whether the existing skills should expand or whether a new skill is warranted.
- **Did Christian's refinements reveal a preference not yet captured?** If he consistently pushed back in a particular direction (preferring shorter sentences, wanting more examples, favoring a different transition style), suggest codifying that preference in the christian-writing-style skill.

Present these observations briefly at the end of the session. If there's nothing worth flagging, say so and move on. Don't manufacture meta-feedback for its own sake.
