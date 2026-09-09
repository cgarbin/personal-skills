---
name: christian-writing-style
description: >-
  Apply Christian Garbin's writing style to prose under his name: papers, abstracts, systematic reviews, dissertation chapters, blog posts, tutorials, READMEs, ADRs, docs, emails, commit messages, PR descriptions, code comments, docstrings. Use it whenever he asks to write, draft, edit, fill in, or clean up any of those, including an empty README or a doc that has grown messy, even when he says nothing about style. Not for mechanical edits to a markdown file that need no prose judgment, such as aligning table pipes or inserting a table of contents.
---

# Christian Garbin's Writing Style

Three registers share one voice and differ in formality. Route first, read the common foundation, then read the reference file for the register you picked. Loading the wrong reference wastes context and pulls in conventions that do not apply.

Write about the subject. The example sentences and layout descriptions in these files are there to be applied. Copying them is the failure mode.

## Choose the register first

**Short snippets.** Single-line comments, one-line docstrings, commit subject lines and bodies, PR titles, log messages, error strings, short field or type descriptions. Anything with room for at most two or three sentences. The common foundation plus the Short snippets section below is the entire skill. No reference file.

**Blog and informal.** Blog post, tutorial, explanation, README, ADR, project documentation, email, social media. Audience is practitioners, developers, or the general public. Prompts like "write a post about..." or "explain...". Read `references/blog.md`.

**Academic and formal.** Paper, review, abstract, dissertation chapter, submission. Mentions a journal, conference, or peer review. Audience is academic researchers or reviewers. Format needs a methods section, literature review, or PRISMA diagram. Prompts like "write a paper about..." or "draft a review of...". Read `references/academic.md`.

**Blended.** Some venues sit in between. IEEE Potentials articles are journal-published but written for students, more accessible than a Springer paper and more structured than a blog post. Use academic structure with proper citations, lean toward blog tone with more accessible language and less hedging. Read both reference files.

**When in doubt:** ask.

---

## Common foundation

### Intellectual character

- **Be measured and precise.** Avoid hype. Undersell with accurate hedging. Blog: "under these specific circumstances, for this specific application, AI has performed well." Papers: "the results suggest."
- **Be honest about limitations.** Say what the work does not cover. In papers, treat the limitations section as a contribution.
- **Ground claims in evidence.** Cite academic papers in blog posts. Give comprehensive literature reviews in papers. Do not assert without evidence.
- **Stay practical.** Connect theoretical work back to real-world implications. End systematic reviews with practitioner guidance. Include runnable code in blog experiments.
- **Organize for scanning.** Descriptive section headers, comparison tables, progressive disclosure from simple to complex.

### Craft principles (Pinker, *The Sense of Style*)

These shape *how* sentences are built, in every register.

**Classic style.** Direct the reader's gaze to something in the world. Prose is a window onto the subject. Avoid metaconcepts. Don't write "This section discusses X" when you can state X. Don't write "It is important to note that X" when you can write X.

**Fight the curse of knowledge.** Anchor abstract concepts in something concrete before going abstract. When evaluating a specialist term, ask: is it used once without definition? Does a plain-language equivalent of similar length exist? If yes to either, prefer plain. The specialist term stays only when it is standard for the audience or rewording would lose accuracy. A term inside an example is a separate case. If the lesson is the sentence's shape, any vocabulary works, which is why a model name can sit in an example about modifier placement. If the reader has to understand the example to see the point, it needs words the audience already has.

**Avoid zombie nouns.** Prefer verbs to nominalizations.

- "The identification of the factors" → "We identified the factors"
- "The utilization of deep learning for the classification of images" → "We used deep learning to classify images"
- "An investigation was conducted" → "We investigated"

Active voice even in academic writing. Passive only when the agent is unknown or irrelevant, or when it improves flow by keeping the topic in subject position.

**Given before new.** Each sentence starts with what the reader knows and ends with the new point.

- Good: "The neural network classified 65 out of 67 pictures correctly. This 97% accuracy is good for a relatively small network."
- Weak: "A relatively good accuracy for a small network, 97%, was achieved when 65 of 67 pictures were classified correctly."

**Keep subject and verb close.** Don't stack long modifiers between them. Heavy qualifying phrases go at the end.

- Heavy in middle: "The model, which was trained on 10,000 images from three hospitals using a ResNet-50 architecture with data augmentation, achieved 94% accuracy."
- Heavy at end: "The model achieved 94% accuracy after training on 10,000 images from three hospitals, using a ResNet-50 architecture with data augmentation."

**One sentence, one job.** Past about forty words, check whether the sentence is two sentences nobody separated, or one chaining a clause it should have handed to the next. Lists and enumerations are the common case at that length and they earn it, because the reader takes one item at a time instead of one growing structure.

- Chained: "The oracle selection cuts a median 62% of the input tokens, and recall moves by less than 0.01 in every stratum, which says the generator already had the content and left it unused, so the ceiling is not a retrieval problem."
- Split: "The oracle selection cuts a median 62% of the input tokens. Recall moves by less than 0.01 in every stratum, so the generator already had the content and left it unused. The ceiling is not a retrieval problem."

**One hedge per claim.** "The results suggest..." not "It would seem to appear that the results might possibly suggest..." Pick the right hedge ("suggest," "may indicate," "one possible explanation") and use it once.

### Name the concrete thing

An abstraction standing in for a specific thing makes the reader do the decoding. Christian illustrates abstract points with misspelled school-zone signs, misclassified ducks, X-rays with pen marks.

- **Framing-deck vocabulary**: "stack," "arm," "frontier," "axes," "lever." "Our retrieval stack" → "our retrieval pipeline" or the actual components. "The temporal axis" → "time of note creation" or whatever the specific variable is.
- **"Downstream"** as shorthand for "later" or "the next stage." "Downstream analysis" → "Phase 2 analysis," "the audit step," "the next step."
- **"Load-bearing"** for the part something depends on. "The comment is load-bearing" → "the comment is the only place the constraint is written down." Say what depends on it and what breaks without it.
- **"Land"** as a verb for where files, data, or values end up ("files land at X," "binaries land in $DIR"). Use "go into," "end up at," "is written to," "sits in," or rephrase. Watch for adjacent overuse: "lands cleanly," "the changes landed in the same window."
- **"Carry"** as a verb for what text, code, or a table conveys ("the comment carries the constraint," "the reason carries the content," "what the table cannot carry"). Use "state," "describe," or name what the text actually does.
- **"Hold"** as a verb for what a file, a table, or a dataset contains ("the cohort holds 116 admissions," "the row holds three statistics"). Use "has," "contains," or name what is in it. "Hold" is right for staying steady ("recall holds to the longest admissions") and for keeping something back ("held back from the prose pass").
- **Vague quantifiers where a number exists.** "Latency was elevated" → give the value. "Various factors" → name them. "The system had issues" → name what went wrong. "Tighten grading" → say which metric moved and by how much. "Recovers a small fraction of those concepts" → give the fraction.
- **Coining a phrase when the document already supplies one.** When a passage reads badly, take the wording from its own tables, captions, bullets, and defined terms before inventing anything. One sentence went through five rewrites, each inventing a new abstraction ("sits in the numerator but not its denominator"), while the table row three lines above already read "Not in the source documents, in the generated summary."

### Show, don't tell

Christian shows. An argument built on experiments is laid out as **hypothesis, what was done to test it, the result in a scannable form, then the conclusion**. The same content written as flowing paragraphs is wrong for him even when it is accurate and well written. His reaction to the prose version: "the text is long and prose heavy, hard to follow."

Three or more parallel items are table-shaped or list-shaped, never a run of paragraphs. Candidate explanations, options considered, eliminations, variants tested. Lead with a summary table as the scan layer. After it, each item gets only what the table could not state, usually the mechanism and the caveat.

Do not announce that arrangement in the text. A table followed by per-item sections is self-evident.

Watch the table count as well. Many tables in one section means many measurement populations, denominators, and data vintages for a reader to hold at once, and that is its own source of error. If two tables would need two different provenance footnotes, consider whether one belongs in an appendix.

### Tables and the prose beside them

**Prose next to a table states what the numbers mean. It never restates the numbers.** Point at the table and spend the sentences on the reading. A figure the table does not contain, such as a derived ratio or a fraction of a total, does earn its place in prose.

`references/academic.md` works through the results-section case.

### No this-not-that

He does not write "X rather than Y" or "X, not Y". Restate as a positive claim about what is true, or cut the clause and let the sentences around it show the contrast.

- "Executing that agreement is procurement work rather than a checkbox" becomes "Executing that agreement takes work on both sides."
- "What disqualifies a path is whose server holds the record, not whose weights run on it" becomes "Where the record goes is what rules a path out."
- "does not answer this, and the reason is legal rather than technical" becomes "does not answer this."

The rule governs the phrasing, so it holds where the contrast is informative. A dissertation whose argument is a chain of eliminations passes the empty-tail test below on nearly every instance, and a sweep of one manuscript still had to restate 91 of them. Fix every instance in the passage. The flagged one is a sample.

A plain negation is a different thing and stays: "Low recall is not a retrieval problem" asserts something, where "X, not Y" only points away from Y.

Two places keep the construction. Quoted material is a record of what was sent or said, so editing it misreports the source. A table cell where the column is a verdict takes the positive half alone ("Metric configuration"), which is the same fix in less space.

### Side commentary

Three forms comment on the text instead of stating the fact. Each spends a sentence without telling the reader anything about the subject, so cut them.

**Editorial close-outs** after factual sentences ("X does not do Y," "this solves it," "that is what the evaluation shows"). If the factual sentence stands on its own, let it stand. Especially tempting at the end of paragraphs. Two variants hide well.

- **The empty contrastive tail** names what the fact is *not*, where no reader would have assumed otherwise ("the appendix gives the actual header forms, where a bare count would have said less").
- **The paragraph-closing restatement** says again what the paragraph just showed ("...so what remains in the score is a difference in content. That is the whole purpose of the labels.").

A tail built on "X rather than Y" or "X, not Y" goes whatever this test says (No this-not-that). For a tail worded some other way, keep the contrast only when the alternative was actually tried, or a reader would plausibly assume it, or the argument depends on ruling it out.

**Announcing a choice as deliberate** ("the choice was deliberate," "we take X deliberately," "on purpose," "by design"). The reason that follows is the content. Delete the announcement, keep the reason. Two exceptions. Keep it when the deliberateness is itself the fact, because a reader would otherwise read oversight or accident ("the same defect, arrived at deliberately"). Rewrite when the announcement heads an enumeration, where deleting it orphans the list: "We use a single-pass design, for three reasons. First..."

**Narrating a disclosure instead of disclosing** ("we do not claim otherwise," "we record that as a limitation," "and the write-up has to say so," "to state in the limitations rather than let a reviewer state it"). The sentence performs the act it describes. State the limitation and stop.

**Restatements go, conclusions stay.** A restatement repeats a fact already on the page. A conclusion asserts an inference the facts support but do not state. It stays: "Low recall is not a retrieval problem," after numbers showing the gap is ten times what retrieval moves. Cutting a conclusion leaves the reader holding evidence with no claim attached. In results and decision documents the verdict is the deliverable, so when the call is close, keep it.

Side commentary is not the same as personal voice, which `references/blog.md` calibrates for the blog register.

### What to avoid

Items ending in a section name are explained above.

- Breathless enthusiasm or marketing language ("revolutionary," "game-changing," "incredible," "novel" without justification).
- Claims without sources.
- Attribution verbs stronger than the evidence ("established," "proved," "showed" for what a source argued or proposed).
- Jargon without explanation, including soft verbs used as jargon ("surface," "leverage," "unlock").
- Overpromising or hyping results.
- Emojis.
- Filler openers ("In today's rapidly evolving world...", "As we all know...").
- Single-word paragraph leads that label the paragraph instead of stating its point ("Interpretation.", "Discussion."). A bold multi-word lead-in that states a claim is a house pattern and stays ("**Restatements go, conclusions stay.**").
- Ignoring or minimizing limitations.
- British spelling. Use US: *analyze*, *color*, *behavior*, *modeling*, *-ize*, *center*, *defense*.
- Em-dashes in his own writing. Use periods or parentheses unless Christian uses one first in the conversation.
- Joining two independent clauses with a semicolon or with a comma and "and". Each clause takes its own sentence, even closely related ones ("The model converged. The loss plateaued at 0.3."). "So", "but" and "for" each state a relationship a period would drop, so they stay. A compound predicate is one clause and stays whole ("The script reads the artifact and writes the scores beside it"). Semicolons in pseudo-code or table structure are fine.
- Nominalizations where a verb would do ("the implementation of" → "we implemented"). (Craft principles)
- Metacommentary that delays content ("It is worth noting that...", "It is important to mention..."). (Craft principles)
- Hedging pileups. One hedge per claim, placed precisely. (Craft principles)
- Passive voice when the agent matters and active voice would be clearer. (Craft principles)
- Long left-branching phrases that separate subject from verb. (Craft principles)
- Sentences past about forty words that are not a list or an enumeration. (Craft principles)
- Vague hand-waving instead of concrete evidence. "Various factors" → name them. (Name the concrete thing)
- Framing-deck vocabulary ("stack," "arm," "frontier," "axes," "lever"), "downstream" for "later," "land" as a verb for where things end up, "carry" for what text conveys. (Name the concrete thing)
- "X rather than Y" and "X, not Y". (No this-not-that)
- Editorial close-outs, announcing a choice as deliberate, narrating a disclosure instead of disclosing. (Side commentary)

---

## Short snippets

Skip to **Editing existing text** if you routed to blog or academic.

Comments and docstrings have a second layer of rules on top of this section. Read **code-comments** before writing or editing one.

The common foundation is the entire skill here. There is no opening hook, no roadmap, no progressive disclosure, no hedging strategy to choose, because there is no room for any of it. What still applies, even in one line:

- No semicolons as clause-joiners. Use a period or rephrase.
- No em-dashes. Use periods or parentheses.
- US spelling (*analyze*, *behavior*, *modeling*).
- No zombie nouns. "Compute the average" beats "perform the computation of the average."
- Concrete and specific. Name the thing. "The value" and "the data" are placeholders.
- No filler ("note that...", "it is worth mentioning that..."). Just state it.
- No marketing words ("simply", "easily", "blazing fast").

**A snippet earns its place by stating a fact its context cannot.** The context is the code for a comment, the diff for a commit message, the stack trace for an error string. That fact is usually the constraint that shaped the work or the hazard it avoids. A commit body is narrower, and **commit** sets its rules. In a comment the rejected alternative goes, whatever the reasoning (**code-comments**, road not taken). The test while drafting: what would a reader who skipped it get wrong? If nothing, delete it. If one clause answers it, that clause is the whole snippet. A constraint that shaped the code and appears nowhere on the page is a missing comment.

When a snippet still runs past two or three sentences after every sentence has earned its place (a multi-paragraph docstring, a long PR description), switch to the blog register. A commit body is the exception. Its reader has the diff, so the body needs only what no comment can state. **commit** has the ceiling and the examples. Its check runs this scan on the body for you.

---

## Editing existing text

The default is minimal intervention.

- Fix what violates this skill. Leave what merely differs from how you would have written it.
- Preserve his structure unless the structure is the problem. Raise a reordering of sections as a finding and leave the document alone.
- Preserve the voice already on the page, including asides and reactions he wrote himself. The rate limit in `references/blog.md` governs what you add. What he already wrote stays.
- After renaming a term or reframing a decision, scan the whole document for the old usage. Anything beyond a rename needs the consumer check in **text-review**, because an addition or a changed number breaks a passage elsewhere without leaving a stale string to find.

A fix confined to a sentence or two goes in directly. Anything larger is a review, so switch to **text-review** and use its gate: present every finding grouped by severity, wait, then work through them one at a time. Do not describe a large rewrite and apply it in the same turn.

---

## Before you finish

Run the mechanical scan on every file you wrote or edited, and fix what it finds. It catches what survives a careful draft: em-dashes, clauses joined by a semicolon or by a comma and "and", British spelling, filler openers, the this-not-that construction, sentences past forty words, and the vocabulary under Name the concrete thing.

```bash
~/.claude/skills/text-review/scripts/scan.py draft.md README.md loader.py
~/.claude/skills/text-review/scripts/scan.py --skip-html-comments draft.md
```

The second form reads the published prose and skips `<!-- -->` notes. Use it on a drafting file, where the notes can outweigh the prose.

Pass every file you touched in one call. The extension decides what gets read: a source file is reduced to its comments and docstrings, anything else is read as prose.

**text-review** owns the script and explains what each pattern is for. On a non-standard install it sits at `text-review/scripts/scan.py` in the skills directory.

Work the groups in order. `FIX` and `REWRITE` hits are always violations. Every group prints a `see` line pointing at the rule behind the check. `TEST` hits also print the test to apply. Whenever you decide to keep your wording, quote that test and answer it in one line. Reasoning that never states the test drifts back to what you already wrote.

A clean scan is not a clean draft.

- **The rules with no stems.** Announcing the arrangement instead of stating it (Show, don't tell) has no mechanical form. Neither does coining a phrase the document already supplies (Name the concrete thing), nor do the paragraph-tail and paragraph-opening tests in **text-review**. The wording is new every time. Read your own draft for them the way you would read someone else's.
- **Text that never becomes a file**, such as an answer in the conversation. Reread it against What to avoid instead.
- **Files that quote the banned vocabulary as examples**, these skill files included. Every example fires, so read those files by eye.
