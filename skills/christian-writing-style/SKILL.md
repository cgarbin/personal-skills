---
name: christian-writing-style
description: >-
  Apply Christian Garbin's writing style to prose under his name: papers, abstracts, systematic reviews, dissertation chapters, blog posts, tutorials, READMEs, ADRs, docs, emails, commit messages, PR descriptions, code comments, docstrings. Use it whenever he asks to write, draft, edit, fill in, or clean up any of those, including an empty README or a doc that has grown messy, even when he says nothing about style. Not for mechanical edits to a markdown file that need no prose judgment, such as aligning table pipes or inserting a table of contents.
---

# Christian Garbin's Writing Style

The registers below share one voice and differ in formality. Route first, read the common foundation, then read what the third column names. Loading the wrong reference wastes context and pulls in conventions that do not apply. Apply the example sentences and layout descriptions in these files to your own subject. Copying them is the failure mode.

## Choose the register first

| Register | Covers | Read |
| --- | --- | --- |
| Short snippets | Single-line comments, one-line docstrings, commit subject lines and bodies, PR titles, log messages, error strings, short field or type descriptions. Anything with room for at most two or three sentences | The common foundation and Short snippets below, and no reference file. **code-comments** for a comment or a docstring, **commit** for a commit body |
| Blog and informal | Blog post, tutorial, explanation, README, ADR, project documentation, email, social media. Audience is practitioners, developers, or the general public. Prompts like "write a post about..." or "explain..." | `references/blog.md` |
| Academic and formal | Paper, review, abstract, dissertation chapter, submission. Mentions a journal, conference, or peer review. Audience is academic researchers or reviewers. Format needs a methods section, literature review, or PRISMA diagram. Prompts like "write a paper about..." or "draft a review of..." | `references/academic.md` |
| Blended | A venue between the two. IEEE Potentials articles are journal-published and written for students, more accessible than a Springer paper and more structured than a blog post | Both reference files |

In the blended register, take structure and citations from academic and tone from blog.

**When in doubt:** ask.

---

## Common foundation

### Intellectual character

- **Be measured and precise.** Avoid hype. State the claim at the strength the evidence supports, and hedge where the evidence is thin. Blog: "under these specific circumstances, for this specific application, AI has performed well."
- **Be honest about limitations.** Say what the work does not cover. In papers, treat the limitations section as a contribution.
- **Ground claims in evidence.** Cite academic papers in blog posts. Give comprehensive literature reviews in papers. Do not assert without evidence.
- **Stay practical.** Connect theoretical work back to real-world implications. End systematic reviews with practitioner guidance. Include runnable code in blog experiments.
- **Organize for scanning.** Descriptive section headers, comparison tables, progressive disclosure from simple to complex.

### Craft principles (Pinker, *The Sense of Style*)

These shape *how* sentences are built, in every register.

**Classic style.** Direct the reader's gaze to something in the world. Prose is a window onto the subject. Avoid metaconcepts. Don't write "This section discusses X" when you can state X. Don't write "It is important to note that X" when you can write X.

**Fight the curse of knowledge.** Anchor abstract concepts in something concrete before going abstract. Prefer the plain word unless the term is standard for this audience or rewording loses accuracy. A term used once and never defined is the common failure, because the reader pays for it and gets nothing back. A term inside an example is a separate case when the lesson is the sentence's shape. If the reader has to understand the example to see the point, it needs words the audience already has.

**Avoid zombie nouns.** Prefer verbs to nominalizations.

- "The identification of the factors" → "We identified the factors"
- "An investigation was conducted" → "We investigated"

Active voice even in academic writing. Passive only when the agent is unknown or irrelevant, or when it improves flow by keeping the topic in subject position.

**Given before new.** Each sentence starts with what the reader knows and ends with the new point.

- Good: "The neural network classified 65 out of 67 pictures correctly. This 97% accuracy is good for a relatively small network."
- Weak: "A relatively good accuracy for a small network, 97%, was achieved when 65 of 67 pictures were classified correctly."

**Keep subject and verb close.** Don't stack long modifiers between them. Heavy qualifying phrases go at the end.

- Heavy in middle: "The model, which was trained on 10,000 images from three hospitals using a ResNet-50 architecture with data augmentation, achieved 94% accuracy."
- Heavy at end: "The model achieved 94% accuracy after training on 10,000 images from three hospitals, using a ResNet-50 architecture with data augmentation."

**One sentence, one job.** Past about forty words, check whether the sentence is two sentences nobody separated, or one chaining a clause it should have handed to the next. Lists and enumerations are the common case at that length and they earn it.

- Chained: "The oracle selection cuts a median 62% of the input tokens, and recall moves by less than 0.01 in every stratum, which says the generator already had the content and left it unused, so the ceiling is not a retrieval problem."
- Split: "The oracle selection cuts a median 62% of the input tokens. Recall moves by less than 0.01 in every stratum, so the generator already had the content and left it unused. The ceiling is not a retrieval problem."

**One hedge per claim, and none on a claim the evidence settles.** "The results suggest..." not "It would seem to appear that the results might possibly suggest..." Pick the right hedge ("suggest," "may indicate," "one possible explanation") and use it once.

### Name the concrete thing

An abstraction standing in for a specific thing makes the reader do the decoding. Christian illustrates abstract points with misspelled school-zone signs, misclassified ducks, X-rays with pen marks.

- **Framing vocabulary standing in for the specific thing**: "stack," "arm," "frontier," "axes," "lever," "downstream," "load-bearing," "land," "carry." "Our retrieval stack" → "our retrieval pipeline". "The temporal axis" → "time of note creation". "Downstream analysis" → "Phase 2 analysis" or "the audit step". "The comment is load-bearing" → "the comment is the only place the constraint is written down", naming what breaks without it. "Files land at X" → "files are written to X". "The comment carries the constraint" → "states the constraint".
- **"Hold"** for what a file or a dataset contains ("the cohort holds 116 admissions"). Use "has" or "contains". "Hold" is right for staying steady ("recall holds to the longest admissions") and for keeping something back.
- **"Bear"** for how one fact relates to another ("their evaluation bears on leakage"). Name the relation: "could have caught leakage." "Bears out" is "confirms." "Bear in mind" opens a sentence that states the fact without it.
- **A statistic standing in for the quantity it measures.** "Llama's median is the fastest at every stratum" makes the reader ask "median of what?", then guess from "fastest" that it might be time. Write "Llama's generation time". The statistic is not the wrong word. It is in the slot the quantity belongs in.
- **An artifact standing in for what it shows.** A table, row, column, line, curve, or cell cannot do what a quantity does. The test is whether the artifact can literally take the verb. A table can list the strata. A row cannot move recall. An artifact that passes the test still names what it plots: "so the lines cross" → "so the memory curves cross". One that fails is replaced: "This table is the limit of the model" → "Input utilization is the limit of the model".
- **A bare ordinal or position.** "the least memory below the first crossing and the most above the second" sends the reader back to map two ordinals onto two numbers in the previous sentence. Write "the least memory up to about 14,000 tokens and the most above about 38,000". When no name exists, supply the noun the ordinal counts: "The third survives" → "The third failure mode survives".
- **Vague quantifiers where a number exists.** "Latency was elevated" → give the value. "Various factors" → name them. "The system had issues" → name what went wrong. "Tighten grading" → say which metric moved and by how much. "Recovers a small fraction of those concepts" → give the fraction. Beside a table that prints the value, the label is the right form and the number stays in the table (Tables and the prose beside them).
- **Coining a phrase when the document already supplies one.** When a passage reads badly, take the wording from its own tables, captions, bullets, and defined terms before inventing anything. Rewriting one sentence more than twice means the wording is already somewhere in the document.

### Point at a noun

This, that, those, it, its, they, one, the two, the former: each of these sends the reader back for a noun. The reader takes the nearest noun that fits. Write the noun whenever the nearest noun is something else, and whenever no noun was written anywhere. The writer is the last reader to see the defect, because the writer knows the referent.

- **The nearest noun wins.** "The methods table answers what raises coverage. This one answers what has been tried" hands the second sentence to the methods table. Write "This document answers what has been tried".
- **A pointer with nothing behind it.** "Neither total is restated in prose" follows a paragraph that names no total. The reader has to build both totals out of it. Write "Neither the row count nor the study count".
- **Add the head noun, or replace the pointer with it.** "Those are ceilings and baselines" becomes "Those runs are ceilings and baselines". "calls content selection the unmeasured one" becomes "the unmeasured technique". "Koras reached 0.363 from that same base model" becomes "from Llama-3-8B-Instruct". One repeated noun costs less than a lookup. A name costs no more to read. The bare ordinal above is the same failure.
- **A name standing in for one side of a comparison.** "Koras is its published peer. What separates the two is the width of the channel from the reference to the prompt" sets a research group against this work's format instruction. Name both sides: "Koras's authoring guidelines are the format instruction's published peer. The format instruction and the authoring guidelines differ in how much of the reference reaches the prompt."
- **A pro-verb.** "Does" and "did" send the reader back for a verb. "the cheapest place in the table to intervene and the only place it does" makes the reader rebuild the verb. Name the subject and what it does: "the only place this work touches".

A demonstrative that stands for the situation just described stays: "This is a limit of the task", after a paragraph that establishes the limit. An expletive stays too. "It takes two passes" points at nothing by design, and naming a subject there produces the zombie noun the craft principles ban.

### Show, don't tell

Christian shows. An argument built on experiments is laid out as **hypothesis, what was done to test it, the result in a scannable form, then the conclusion**. The same content written as flowing paragraphs is wrong for him even when it is accurate and well written.

Three or more parallel items are table-shaped or list-shaped, never a run of paragraphs. Candidate explanations, options considered, eliminations, variants tested. Items that connect with "because" or "but" stay prose, where the connective is part of the reasoning (`references/blog.md`, Bullets vs. prose). Lead with a summary table as the scan layer. After it, each item gets only what the table could not state, usually the mechanism and the caveat.

Do not announce that arrangement in the text. A table followed by per-item sections is self-evident.

### Tables and the prose beside them

**Prose next to a table states what the numbers mean. It never restates the numbers.** Point at the table and spend the sentences on the reading. A figure the table does not contain, such as a derived ratio, earns its place.

`references/academic.md` works through the results-section case.

### No this-not-that

He does not write "X rather than Y" or "X, not Y". Restate as a positive claim about what is true, or cut the clause and let the sentences around it show the contrast.

- "Executing that agreement is procurement work rather than a checkbox" becomes "Executing that agreement takes work on both sides."
- "What disqualifies a path is whose server holds the record, not whose weights run on it" becomes "Where the record goes is what rules a path out."
- "does not answer this, and the reason is legal rather than technical" becomes "does not answer this."

The rule governs the phrasing, so an informative contrast is still restated. One sweep of a dissertation arguing by elimination restated 91 of them. Fix every instance in the passage. A flagged one is a sample.

A plain negation is a different thing and stays: "Low recall is not a retrieval problem" asserts something, where "X, not Y" only points away from Y.

Quoted material keeps the construction, since editing it misreports the source. A verdict column in a table takes the positive half alone, so the cell reads "Metric configuration" where the prose would have said "metric configuration, not model choice".

### Side commentary

Three forms comment on the text instead of stating the fact. Each spends a sentence without telling the reader anything about the subject, so cut them.

**Editorial close-outs** after factual sentences ("X does not do Y," "this solves it," "that is what the evaluation shows"). If the factual sentence stands on its own, let it stand. Especially tempting at the end of paragraphs. Two variants hide well.

- **The empty contrastive tail** names what the fact is *not*, where no reader would have assumed otherwise ("the appendix gives the actual header forms, where a bare count would have said less").
- **The paragraph-closing restatement** says again what the paragraph just showed ("...so what remains in the score is a difference in content. That is the whole purpose of the labels.").

A tail built on "X rather than Y" or "X, not Y" goes whatever this test says (No this-not-that). For a tail worded some other way, apply the empty-tail test: keep the contrast only when the alternative was actually tried, or a reader would plausibly assume it, or the argument depends on ruling it out.

**Announcing a choice as deliberate** ("the choice was deliberate," "we take X deliberately," "on purpose," "by design"). The reason that follows is the content. Delete the announcement, keep the reason. Keep it when the deliberateness is itself the fact ("the same defect, arrived at deliberately"). Rewrite when the announcement heads an enumeration, where deleting it orphans the list: "We use a single-pass design, for three reasons. First..."

**Narrating a disclosure instead of disclosing** ("we do not claim otherwise," "we record that as a limitation," "and the write-up has to say so," "to state in the limitations rather than let a reviewer state it"). The sentence performs the act it describes. State the limitation and stop.

**Restatements go, conclusions stay.** A restatement repeats a fact already on the page. A conclusion asserts an inference the facts support but do not state. It stays: "Low recall is not a retrieval problem," after numbers showing the gap is ten times what retrieval moves. In results and decision documents the verdict is the deliverable, so when the call is close, keep it.

Side commentary is not the same as personal voice, which `references/blog.md` calibrates for the blog register.

### What to avoid

- Breathless enthusiasm or marketing language ("revolutionary," "game-changing," "incredible," "novel" without justification).
- Attribution verbs stronger than the evidence ("established," "proved," "showed" for what a source argued or proposed).
- Jargon without explanation, including soft verbs used as jargon ("surface," "leverage," "unlock").
- Emojis.
- Filler openers ("In today's rapidly evolving world...", "As we all know...").
- Single-word paragraph leads that label the paragraph instead of stating its point ("Interpretation.", "Discussion.").
- British spelling. Use US: *analyze*, *color*, *behavior*, *modeling*, *-ize*, *center*, *defense*.
- Em-dashes in his own writing. Use periods or parentheses unless Christian uses one first in the conversation.
- Joining two independent clauses with a semicolon or with a comma and "and". Each clause takes its own sentence ("The model converged. The loss plateaued at 0.3."). "So", "but" and "for" state a relationship a period would drop, so they stay. A compound predicate is one clause and stays whole ("The script reads the artifact and writes the scores beside it").

This list is not the whole of it. Every rule in the common foundation belongs on it too. A second copy here would be a second wording to drift from.

---

## Short snippets

Comments and docstrings have a second layer of rules on top of this section. Read **code-comments** before writing or editing one.

The common foundation is the entire skill here. No hook, no roadmap, no progressive disclosure. What still applies, even in one line:

- No zombie nouns. "Compute the average" beats "perform the computation of the average."
- Concrete and specific. Name the thing. "The value" and "the data" are placeholders.
- No filler ("note that...", "it is worth mentioning that..."). Just state it.
- No marketing words ("simply", "easily", "blazing fast").

**A snippet earns its place by stating a fact its context cannot.** The context is the code for a comment, the diff for a commit message, the stack trace for an error string. That fact is usually the constraint that shaped the work or the hazard it avoids. In a comment the rejected alternative goes, whatever the reasoning (**code-comments**, road not taken). The test while drafting: what would a reader who skipped it get wrong? If nothing, delete it. If one clause answers it, that clause is the whole snippet. A constraint that shaped the code and appears nowhere on the page is a missing comment.

When a snippet still runs past two or three sentences after every sentence has earned its place (a module docstring, a long PR description), switch to the blog register for sentence construction. Its Structure and Formatting sections describe a post. A commit body is the exception. Its reader has the diff, so the body needs only what no comment can state. **commit** has the ceiling and the examples. Its check runs this scan on the body for you.

---

## Editing existing text

The default is minimal intervention.

- Fix what violates this skill. Leave what merely differs from how you would have written it.
- Preserve his structure unless the structure is the problem. Raise a reordering of sections as a finding and leave the document alone.
- Preserve the voice already on the page, including asides and reactions he wrote himself. The rate limit in `references/blog.md` governs what you add. What he already wrote stays.
- After renaming a term or reframing a decision, scan the whole document for the old usage. Anything beyond a rename needs "Check what a pass left inconsistent" in **text-review**.

A fix confined to a sentence or two goes in directly. Anything larger is a review, so switch to **text-review** and use its gate. Do not describe a large rewrite and apply it in the same turn.

---

## Before you finish

Run the mechanical scan on every file you wrote or edited, and fix what it finds. It catches what survives a careful draft, naming each check it fires and the rule behind it.

```bash
~/.claude/skills/text-review/scripts/scan.py draft.md README.md loader.py
~/.claude/skills/text-review/scripts/scan.py --skip-html-comments draft.md
```

Use the second form on a drafting file, where the `<!-- -->` notes can outweigh the prose.

Pass every file you touched in one call. A source file whose extension the script knows is reduced to its comments and docstrings. Everything else is read as prose. That includes a source file in a language the script does not know, whose statement separators then fire the semicolon check (`COMMENT_SYNTAX` in `scan.py`).

Work the groups in order. **text-review**'s mechanical scan section explains how to read the output, including what to do with a hit you decide to keep. On a non-standard install the script sits at `text-review/scripts/scan.py` in the skills directory.

A clean scan is not a clean draft.

- **The rules no stem reaches.** The statistic, artifact, and ordinal patterns, and coining a phrase the document already supplies (Name the concrete thing). The paragraph-tail, paragraph-opening, and pointer tests, and announcing the arrangement, are reached in part only, so a clean run on those leaves the rest to you. What no stem reaches is worded new every time, so read your own draft for it the way you would read someone else's.
- **Text that never becomes a file**, such as an answer in the conversation. Reread it against What to avoid instead.
- **Files that quote the banned vocabulary as examples**, these skill files included. Every example fires, so read those files by eye.
