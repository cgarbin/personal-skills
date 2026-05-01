---
name: christian-writing-style
description: Christian Garbin's writing style for any prose he authors. Use when writing or editing prose under his name in any document or code context, including any markdown (.md) file (READMEs, ADRs, project documentation), docstrings, code comments (single-line and multi-line), commit messages, PR descriptions, and emails. Triggers include "write this in my style", "help me write", "review my draft", editing or creating any .md file, or writing or editing comments and docstrings in code.
---

# Christian Garbin's Writing Style

Two registers for substantive prose, **blog/informal** and **academic/formal**, plus a **short snippets** case where only the common foundation applies. Same voice, different formality. Choose based on context. If unclear, ask.

---

## Common foundation

### Intellectual character

- **Measured and precise.** Avoids hype. Undersells with accurate hedging rather than overclaiming. Blog: "under these specific circumstances, for this specific application, AI has performed well." Papers: "the results suggest" rather than "the results prove."
- **Honest about limitations.** Every blog post acknowledges what it doesn't cover. Every paper has a thorough limitations section, treated as a contribution.
- **Research-grounded.** Blog posts cite academic papers. Papers provide comprehensive literature reviews. Never asserts without evidence.
- **Practical.** Theoretical work connects back to real-world implications. Systematic reviews end with practitioner guidance. Blog experiments include runnable code.
- **Organized.** Clear structure: descriptive section headers, comparison tables, progressive disclosure from simple to complex.

### Craft principles (Pinker, *The Sense of Style*)

These shape *how* sentences are built, in both registers.

**Classic style.** Direct the reader's gaze to something in the world. Prose is a window onto the subject. Avoid metaconcepts. Don't write "This section discusses X" when you can state X. Don't write "It is important to note that X" when you can write X.

**Fight the curse of knowledge.** Anchor abstract concepts in something concrete before going abstract. When evaluating a specialist term, ask: is it used once without definition? Does a plain-language equivalent of similar length exist? If yes to either, prefer plain. The specialist term stays only when it is load-bearing, standard for the audience, or rewording would lose accuracy.

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

**Concrete and specific.** Name the factors instead of saying "various factors." Name what went wrong instead of saying "the system had issues." Christian illustrates abstract points with misspelled school-zone signs, misclassified ducks, X-rays with pen marks.

**One hedge per claim.** "The results suggest..." not "It would seem to appear that the results might possibly suggest..." Pick the right hedge ("suggest," "may indicate," "one possible explanation") and use it once.

### What to avoid (both registers)

- Breathless enthusiasm or marketing language ("revolutionary," "game-changing," "incredible," "novel" without justification).
- Claims without sources.
- Jargon without explanation.
- Overpromising or hyping results.
- Emojis.
- Filler openers ("In today's rapidly evolving world...", "As we all know...").
- Ignoring or minimizing limitations.
- Vague hand-waving instead of concrete evidence.
- Nominalizations where a verb would do ("the implementation of" → "we implemented").
- Metacommentary that delays content ("It is worth noting that...", "It is important to mention...").
- Hedging pileups. One hedge per claim, placed precisely.
- Passive voice when the agent matters and active voice would be clearer.
- Long left-branching phrases that separate subject from verb.
- British spelling. Use US: *analyze*, *color*, *behavior*, *modeling*, *-ize*, *center*, *defense*.
- Em-dashes in his own writing. Use periods or parentheses unless Christian uses one first in the conversation.
- Semicolons as a clause-joining device. Use a period between independent clauses, even closely related ones ("The model converged. The loss plateaued at 0.3."). Semicolons in pseudo-code or table structure are fine.
- Editorial close-outs after factual sentences ("X does not do Y," "this solves it," "that is what the evaluation shows"). If the factual sentence stands on its own, let it stand. Especially tempting at the end of paragraphs in dissertation prose.
- Framing-deck vocabulary ("stack," "arm," "frontier," "axes," "lever"). Name the concrete thing instead. "Our retrieval stack" → "our retrieval pipeline" or the actual components. "The temporal axis" → "time of note creation" or whatever the specific variable is.
- "Downstream" as shorthand for "later" or "the next stage." Name the concrete next step. "Downstream analysis" → "Phase 2 analysis," "the audit step," "the next step."
- "Land" as a verb for where files, data, or values end up ("files land at X," "binaries land in $DIR"). Stuffy. Use "go into," "end up at," "is written to," "sits in," or rephrase. Watch for adjacent overuse: "lands cleanly," "land in the same place."

---

## Short snippets

For short in-code prose where the two registers below do not fit: single-line comments, one-line docstrings, commit subject lines, PR titles, log messages, error strings, short type or field descriptions.

For these, the **common foundation is the entire skill**. There is no opening hook, no roadmap, no progressive disclosure, no hedging strategy to choose, because there is no room for any of it. What still applies, even in one line:

- No semicolons as clause-joiners. Use a period or rephrase.
- No em-dashes. Use periods or parentheses.
- US spelling (*analyze*, *behavior*, *modeling*).
- No zombie nouns. "Compute the average" beats "perform the computation of the average."
- Concrete and specific. Name the thing, not "the value" or "the data."
- No filler ("note that...", "it is worth mentioning that..."). Just state it.
- No marketing words ("simply", "easily", "blazing fast").
- Explain the *why* or the non-obvious *what*, not the *how*. "Cache key includes tenant id to avoid cross-tenant reuse" beats "set the cache key."

When the snippet grows past two or three sentences (a multi-paragraph docstring, a long PR description, a commit body that argues for a decision), switch to the blog/informal register.

---

## Blog and informal

For blog posts, tutorials, explanations, documentation, emails, social media.

### Voice

Senior engineer explaining something to a smart colleague over coffee. Knowledgeable, never condescending.

- **Conversational but substantive.** Uses technical terms then immediately explains them in plain language.
- **Inclusive.** "We" and "let's" frequently. ("Let's explore what 'learning' means for machine learning." / "We will start with a notebook that is not wrong but is not well written.")
- **Intellectually humble.** Openly acknowledges limits. ("well, it takes me some effort - your mileage may vary" / "The honest answer is 'we don't know'.")
- **Gently humorous.** Parenthetical asides for dry wit:
  - "(well, it takes me some effort - your mileage may vary)"
  - "(presumably, the human would chuckle, then - hopefully - slow down)"
  - "(a polite way to say 'the developers failed to account for how the world works')"

### Sentence patterns

Mix of short and medium sentences. Important thoughts get short sentences for emphasis.

- "That's all." (after a technical explanation)
- "Does it mean we need to stop using neural networks until then? No."
- "The neural network may be _learning_, but it is definitely not _understanding_."
- "So far, so good, but..."

Rhetorical questions as transitions: "Should we be concerned that deep 'learning' is not 'understanding'?"

### Structure

1. **Opening hook.** Framing question, relatable scenario, or clear problem statement. Never throat-clearing. ("In the expression _machine learning_, are the machines actually learning anything?")
2. **Roadmap.** Brief, natural overview of what's coming.
3. **Progressive disclosure.** Simple to complex.
4. **"Why does this matter?" moments.** After a technical result, pause to explain real-world significance, often with an explicit header.
5. **Honest endings.** No forced tidy conclusions on messy topics.

### Formatting

- H2/H3 headers, often conversational: "When are squares not squares?" / "If all we have is a hammer..."
- Italics for technical terms on first use and for emphasis.
- Bold sparingly, for key takeaways. Bold+italic for maximum emphasis: ***the neural network does not understand the concept of "square".***
- Blockquotes with attribution for direct citations.
- Inline links to papers, repos, tools, used generously.
- Notice blocks (`{: .notice}`) for key insights or caveats.
- Code blocks with brief explanations.
- Images with alt text and captions explaining what to notice.

### Bullets vs. prose

If content is naturally a list, write it as a list: scannable reference items, parallel options, discrete steps, side-by-side comparisons. If it carries an argument where items connect with "because" or "but," write prose. Those connectives are part of the reasoning, and bullets hide them.

### Transitions

- "In other words..." to rephrase a complex idea.
- "But there is a twist..." to introduce a complication.
- "Coming from an engineering background..." to ground a point.
- Short bridging sentences: "We will fix some of the issues in the next step."

---

## Academic and formal

For journal papers, conference papers, systematic reviews, abstracts, grant proposals.

### Voice

More formal register, same core qualities of clarity, honesty, practical grounding.

- **Formal but clear.** Direct, declarative sentences. Avoid unnecessary complexity.
- **"We" throughout.** Even in single-author work, never "I."
- **Carefully hedged.** "The results suggest," "this may indicate," "one possible explanation is."
- **Evidence-dense.** Nearly every substantive claim has a citation.

### Sentence patterns

Longer than blog but still clear. Break complex ideas across multiple sentences rather than packing them into one.

- Clear topic sentences: "In this section, we review the methods and tools that have been proposed to address these challenges."
- Specific numbers: "Of the 48 papers, 42 (87.5%) used structured data from electronic health records."
- Hedged conclusions: "These results suggest that... however, further research is needed to..."
- Transitions that summarize what was just covered and preview what's next.

### Structure

**Empirical/experimental papers:**
1. Introduction: problem, motivation, contribution.
2. Related work / background.
3. Methods: setup, datasets, models, training, evaluation.
4. Results: numbers, tables, figures.
5. Discussion: interpretation, comparison, implications.
6. Limitations: thorough and honest, not perfunctory.
7. Conclusion and future work.

**Systematic reviews and surveys:**
1. Introduction: gap, research questions.
2. Methods: search strategy, criteria, PRISMA or equivalent.
3. Results: organized thematically or by question, with summary tables.
4. Discussion: synthesis, patterns, contradictions, implications.
5. Limitations: of the reviewed studies AND of the review itself.
6. Conclusion: takeaways and concrete recommendations.

**Tutorial/overview papers:**
1. Introduction: accessible framing.
2. Background: concepts for a broader audience.
3. Core content: progressive, building from foundations.
4. Practical considerations: deployment, cost, tradeoffs.
5. Conclusion: summary and future directions.

### Tables and figures

Christian uses tables extensively, a distinctive pattern.

- **Comparison tables**: multiple studies, methods, or tools side by side with consistent columns.
- **Summary tables**: condense large amounts of information into scannable formats.
- **Chronological tables**: evolution of methods or findings over time.
- Captions describe what the reader should take away.
- Figures for process flows (PRISMA, system architectures) and results visualizations.

### Bullets vs. prose

Same principle as the blog. Bullets appear in his published work for enumerated contributions, methodological steps, inclusion/exclusion criteria, lists of datasets or models, and limitation items. Bullets must not fragment a coherent argument.

### Practical grounding

Even in formal work, connect findings to practice:

- Explicit "implications for practitioners" or "lessons learned" sections.
- Discussion sections that go beyond restating results.
- Identifying gaps between research and practice.
- Concrete recommendations, not just "future work should explore..."

### Citations

- Dense throughout. Nearly every substantive paragraph cites a source.
- Synthesize across sources rather than listing them. Describe what multiple papers agree on, where they diverge, and what the overall picture suggests.
- Cite primary sources, not secondary summaries.
- References formatted per the target journal's style.
- In Obsidian markdown drafts, use Pandoc citation syntax: `[@smith2023temporal]`, `[@smith2023temporal, p. 42]`, `[@smith2023temporal; @jones2022ehr]`, `[-@key]` to suppress the author. Pandoc resolves these at compile time. Never write formatted references inline.

### Limitations sections

A hallmark of his academic writing.

- Limitations of both the work itself and the methods used.
- In systematic reviews, limitations of the reviewed studies separately from limitations of the review process.
- Practical impact of each limitation, not just its existence.
- Direct: "Our study has some limitations that should be acknowledged..."

---

## Choosing the register

**Short snippets:**
- Single-line comments, one-line docstrings.
- Commit subject lines, PR titles.
- Log messages, error strings, short field or type descriptions.
- Anything with room for at most two or three sentences.
- Apply only the common foundation. No register-specific structure.

**Blog/informal:**
- Blog post, tutorial, explanation.
- "Write a post about...", "explain..."
- Audience: practitioners, developers, general public.
- Format: website, email, social media, documentation.

**Academic/formal:**
- Paper, review, abstract, submission.
- Mentions a journal, conference, or peer review.
- Audience: academic researchers or reviewers.
- Format requires methods section, literature review, or PRISMA diagram.
- "Write a paper about...", "draft a review of..."

**When in doubt:** ask.

### Blending the registers

Some contexts call for an in-between style. IEEE Potentials articles are journal-published but written for students, more accessible than a Springer paper but more structured than a blog post. In these cases:

- Use academic structure (clear sections, proper citations).
- Lean toward blog tone (more accessible language, occasional brief asides, less hedging).
- "Blog rigor with academic structure."
