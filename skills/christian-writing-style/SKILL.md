---
name: christian-writing-style
description: "Christian Garbin's personal writing style guide for both blog posts and academic papers. Use this skill whenever Christian asks you to write anything — blog posts, articles, explanations, tutorials, documentation, academic papers, literature reviews, systematic reviews, conference papers, journal submissions, abstracts, or any prose content. Also use it when he says 'write this in my style', 'draft a post', 'draft a paper', 'help me write', or asks for any written content that should sound like him. If Christian is asking you to produce written text of any kind, consult this skill first."
---

# Christian Garbin's Writing Style

This skill captures Christian's voice and writing patterns, distilled from his blog (cgarbin.github.io) and his published academic papers in journals including Radiology: Artificial Intelligence, Springer Multimedia Tools and Applications, Computer Methods and Programs in Biomedicine, and IEEE Potentials. When writing for Christian, internalize these patterns so the output reads as if he wrote it himself.

Christian writes in two registers — **blog/informal** and **academic/formal** — but the underlying voice is the same person. The register should be chosen based on what he's asking for. If it's unclear, ask.

---

## Part 1: The Common Foundation

These qualities are present in everything Christian writes, regardless of register.

### Intellectual Character

Christian is a senior software engineer with a PhD-level research background. His writing reflects someone who genuinely enjoys understanding how things work and cares about getting the details right. He is:

- **Measured and precise.** He avoids hype and overstatement. He'd rather undersell a finding with accurate hedging than overclaim. In his blog: "under these specific circumstances, for this specific application, AI has performed well." In his papers: "the results suggest" rather than "the results prove."
- **Honest about limitations.** Every blog post acknowledges what it doesn't cover. Every paper has a thorough limitations section. He treats limitations not as a checkbox obligation but as a genuine contribution — helping readers understand the boundaries of what was found.
- **Research-grounded.** In blog posts, he cites academic papers. In academic papers, he provides comprehensive literature reviews. He never asserts without evidence.
- **Practical.** Even his most theoretical work connects back to real-world implications. His systematic reviews end with guidance for practitioners. His blog experiments include runnable code.
- **Organized.** He uses clear structure — sections with descriptive headers, tables for comparison, progressive disclosure from simple to complex. He thinks about the reader's cognitive load.

### Craft Principles (from Steven Pinker's *The Sense of Style*)

Christian follows the principles in Pinker's *The Sense of Style*. These apply across both registers and should guide all prose decisions. They are craft principles that shape *how* sentences are built — they don't change *what* Christian sounds like.

**Write in classic style.** The writer sees something in the world and directs the reader's gaze to it. The prose is a window onto the subject, not a display of the writer's sophistication. This means: orient the reader toward the thing being discussed, not toward the act of discussing it. Avoid metaconcepts — don't write "This section discusses the approach we took" when you can write "We approached the problem by..." Don't write "It is important to note that X" when you can just state X. Show the reader the thing itself.

**Fight the curse of knowledge.** The writer knows things the reader doesn't, and the biggest threat to clear writing is forgetting that. This manifests as unexplained jargon, skipped logical steps, and abstractions where examples are needed. The antidote: when introducing a concept, briefly anchor it in something concrete before going abstract. Christian already does this naturally — he explains "units" vs. "neurons," he walks through Shapley values with an employee profit-sharing analogy. Keep doing this.

**Keep prose vigorous — avoid zombie nouns.** Prefer verbs over nominalizations. Nominalizations turn actions into abstract things and drain the life from sentences:
- "The identification of the factors" → "We identified the factors"
- "The utilization of deep learning for the classification of images" → "We used deep learning to classify images"
- "An investigation was conducted" → "We investigated"

This matters even in academic writing. Formal doesn't mean lifeless. Christian's papers use active voice ("We trained a network..." "We reviewed 48 studies...") far more than the passive-heavy norm in academic ML writing. Preserve this. Use passive voice only when the agent is genuinely unknown or irrelevant, or when it improves flow by keeping the topic in subject position.

**Put given information before new information.** Each sentence should start with what the reader already knows (the topic, or something just mentioned) and end with the new point. This creates a natural flow where the reader is never stranded. Pinker calls this the given-new contract:
- Good: "The neural network classified 65 out of 67 pictures correctly. This 97% accuracy is good for a relatively small network." (starts with the familiar network, ends with the new evaluation)
- Weak: "A relatively good accuracy for a small network, 97%, was achieved when 65 of 67 pictures were classified correctly." (buries the familiar topic)

**Manage the reader's cognitive load with syntax.** Keep the main subject and verb close together. Don't stack up long modifying phrases before the verb — the reader has to hold all of that in memory before they learn what the sentence is doing. When a sentence has a heavy qualifying phrase, put it at the end rather than wedging it between subject and verb:
- Heavy in the middle (hard to parse): "The model, which was trained on 10,000 images from three hospitals using a ResNet-50 architecture with data augmentation, achieved 94% accuracy."
- Heavy at the end (easier): "The model achieved 94% accuracy after training on 10,000 images from three hospitals, using a ResNet-50 architecture with data augmentation."

**Be concrete and specific.** Prefer concrete nouns and specific examples over abstract generalizations. Instead of "various factors can affect model performance," name the factors. Instead of "the system had issues," say what went wrong. This is one of Christian's strengths — he illustrates abstract points with misspelled school-zone signs, misclassified ducks, and X-rays with pen marks.

**Avoid hedging pileups.** Academic writing requires hedging, but don't stack hedges. One hedge per claim is enough:
- Good: "The results suggest that larger training sets improve generalization."
- Pileup: "It would seem to appear that the results might possibly suggest that larger training sets could potentially improve generalization."

Christian hedges precisely — he picks the right hedge ("suggest," "may indicate," "one possible explanation") and uses it once.

### What to Avoid (Both Registers)

These patterns are never Christian's style, in any context:

- Breathless enthusiasm or marketing language ("revolutionary," "game-changing," "incredible," "novel" without justification)
- Making claims without citing sources
- Hiding behind jargon without explanation
- Overpromising or hyping results
- Using emojis
- Starting with filler ("In today's rapidly evolving world..." / "As we all know...")
- Ignoring or minimizing limitations
- Vague hand-waving instead of concrete evidence
- Nominalizations where a verb would do ("the implementation of" → "we implemented")
- Metacommentary that delays the actual content ("It is worth noting that..." / "It is important to mention...")
- Hedging pileups — one hedge per claim, placed precisely
- Passive voice when the agent matters and active voice would be clearer
- Long left-branching phrases that separate subject from verb

---

## Part 2: Blog and Informal Writing

Use this register for blog posts, tutorials, explanations, documentation, emails, social media posts, and any non-academic writing.

### Voice and Tone

Christian writes his blog like a senior engineer explaining something to a smart colleague over coffee. He's knowledgeable but never condescending. He genuinely enjoys learning and wants the reader to share that experience.

- **Conversational but substantive.** He doesn't dumb things down, but he also doesn't hide behind jargon. He'll use a technical term and then immediately explain it in plain language.
- **Inclusive.** He uses "we" and "let's" frequently, bringing the reader along as a partner in exploration. ("Let's explore what 'learning' means for machine learning." / "We will start with a notebook that is not wrong but is not well written.")
- **Intellectually humble.** He openly acknowledges when his own understanding has limits. ("well, it takes me some effort — your mileage may vary" / "The honest answer is 'we don't know'.")
- **Gently humorous.** He uses parenthetical asides for dry wit:
  - "(well, it takes me some effort - your mileage may vary)"
  - "(presumably, the human would chuckle, then - hopefully - slow down)"
  - "(a polite way to say 'the developers failed to account for how the world works')"

### Sentence Patterns

A mix of short and medium-length sentences. When a thought is important, he gives it a short sentence for emphasis.

- "That's all." (after a technical explanation)
- "Does it mean we need to stop using neural networks until then? No."
- "The neural network may be _learning_, but it is definitely not _understanding_."
- "So far, so good, but..."

He uses rhetorical questions as transitions: "Should we be concerned that deep 'learning' is not 'understanding'?"

### Structure

1. **Opening hook.** A framing question, a relatable scenario, or a clear problem statement. Never throat-clearing. ("In the expression _machine learning_, are the machines actually learning anything?")
2. **Roadmap.** A brief, natural overview of what's coming.
3. **Progressive disclosure.** Simple to complex. He starts where the reader is and builds.
4. **"Why does this matter?" moments.** After a technical result, he pauses to explain real-world significance. Often with an explicit header: "Why does this experiment matter?"
5. **Honest endings.** He doesn't force tidy conclusions on messy topics. ("I know ending a post without a conclusion is anti-climatic. But in this case, it's an acknowledgment of the complexity...")

### Formatting (Blog)

- Section headers at H2/H3, often conversational: "When are squares not squares?" / "In the dark, all squares are triangles" / "If all we have is a hammer..."
- Italics for technical terms on first use and for emphasis
- Bold sparingly, for key takeaways. Sometimes bold+italic for maximum emphasis: ***the neural network does not understand the concept of "square".***
- Blockquotes with proper attribution for direct citations
- Inline links, generously — to papers, repos, tools, concepts
- Notice blocks (`{: .notice}`) for key insights or caveats
- Code blocks with brief explanations
- Images with alt text and captions explaining what to notice

### Bullets vs. prose (Blog)

If content is naturally a list, write it as a list: scannable reference items, parallel options, discrete steps, side-by-side comparisons. If it carries an argument or explanation where items connect with "because" or "but", write prose. Those connectives are part of the reasoning, and bullets hide them.

### Transitions (Blog)

- "In other words..." to rephrase a complex idea
- "But there is a twist..." to introduce a complication
- "Coming from an engineering background..." to ground a point in experience
- Short bridging sentences: "We will fix some of the issues in the next step."

---

## Part 3: Academic and Formal Writing

Use this register for journal papers, conference papers, systematic reviews, literature reviews, abstracts, grant proposals, and any peer-reviewed or formally published work.

### Voice and Tone

In academic writing, Christian shifts to a more formal register while retaining his core qualities of clarity, honesty, and practical grounding. The humor and parenthetical asides disappear, but the commitment to making complex topics accessible remains.

- **Formal but clear.** He writes precisely without becoming opaque. He favors direct, declarative sentences even in formal contexts. He avoids unnecessarily complex sentence structures or passive voice where active voice is clearer.
- **"We" throughout.** He uses "we" consistently (even in single-author work), never "I." This is the formal academic "we" — less warm than the blog "let's explore together" but still collaborative in tone.
- **Carefully hedged.** He uses precise hedging: "the results suggest," "this may indicate," "one possible explanation is." He distinguishes clearly between what the data shows, what it suggests, and what remains uncertain.
- **Evidence-dense.** Citation density is much higher than the blog. Nearly every substantive claim is backed by a reference. In systematic reviews, he cites dozens to hundreds of sources.

### Sentence Patterns (Academic)

Sentences are somewhat longer and more structured than in blog writing, but Christian still avoids the kind of dense, multi-clause academic sentences that obscure meaning. He breaks complex ideas across multiple shorter sentences rather than packing them into one.

Characteristic patterns:
- Clear topic sentences that state what a paragraph will do: "In this section, we review the methods and tools that have been proposed to address these challenges."
- Results stated with specific numbers: "Of the 48 papers, 42 (87.5%) used structured data from electronic health records."
- Hedged conclusions: "These results suggest that... however, further research is needed to..."
- Transition sentences between sections that both summarize what was just covered and preview what's next.

### Structure (Academic)

Christian follows standard academic structure but organizes within it carefully:

**For empirical/experimental papers** (e.g., Dropout vs. Batch Normalization, Patient Localization):
1. Introduction — problem statement, motivation, contribution summary
2. Related Work / Background — structured review of prior work
3. Methods — experimental setup, datasets, models, training details, evaluation metrics
4. Results — presented with specific numbers, tables, and figures
5. Discussion — interpretation, comparison with prior work, practical implications
6. Limitations — thorough and honest, not perfunctory
7. Conclusion and Future Work — what was found, what comes next

**For systematic reviews and surveys** (e.g., Opioid Use Disorder review, RSNA Radiology AI paper):
1. Introduction — the gap this review fills, clear research questions
2. Methods — search strategy, inclusion/exclusion criteria, PRISMA or equivalent methodology
3. Results — organized thematically or by research question, with summary tables
4. Discussion — synthesis across studies, patterns, contradictions, implications for practice
5. Limitations — of the reviewed studies AND of the review itself
6. Conclusion — key takeaways and concrete recommendations

**For tutorial/overview papers** (e.g., IEEE Potentials edge computing):
1. Introduction — accessible framing of the problem
2. Background — concepts explained for a broader audience
3. Core content — progressive, building from foundations
4. Practical considerations — real-world deployment, cost, tradeoffs
5. Conclusion — summary of key points and future directions

### Tables and Figures (Academic)

Christian uses tables extensively in his papers to organize and compare information. This is a distinctive pattern:

- **Comparison tables** that organize multiple studies, methods, or tools side by side with consistent columns (e.g., Table 1 in the RSNA paper comparing reporting guidelines, or the systematic review tables organizing 48 studies by data type, ML method, and performance)
- **Summary tables** that condense large amounts of information into scannable formats
- **Chronological tables** showing evolution of methods or findings over time
- Tables always have descriptive captions that explain what the reader should take away
- Figures are used for process flows (PRISMA diagrams, system architectures) and results visualizations

### Bullets vs. prose (Academic)

The same principle applies as in the blog: if content is naturally a list, write it as a list. Bullets appear throughout Christian's published work for enumerated contributions, methodological steps, inclusion and exclusion criteria, lists of datasets or models, and limitation items. What bullets should not do is fragment a coherent argument.

### Practical Grounding (Academic)

Even in his most formal work, Christian connects findings to practice. This shows up as:

- Explicit "implications for practitioners" or "lessons learned" sections
- Discussion sections that go beyond restating results to discuss what they mean for real-world deployment
- Identifying gaps between research and practice (e.g., the gap between published ML models and production-ready systems)
- Concrete recommendations, not just "future work should explore..."

### Citations and References (Academic)

- Dense citation throughout — nearly every substantive paragraph cites at least one source
- He synthesizes across sources rather than just listing them. He'll describe what multiple papers agree on, where they diverge, and what the overall picture suggests.
- He cites primary sources (the original papers) rather than secondary summaries
- References are formatted according to the target journal's style
- When drafting in Obsidian markdown, use Pandoc citation syntax: `[@smith2023temporal]` for standard citations, `[@smith2023temporal, p. 42]` for page references, `[@smith2023temporal; @jones2022ehr]` for multiple sources, `[-@key]` to suppress the author name. These are resolved at compile time by Pandoc — never write out formatted references inline.

### Limitations Sections

This deserves special attention because it's a hallmark of Christian's academic writing. His limitations sections are unusually thorough and honest:

- He identifies limitations of both the work itself and the methods used
- In systematic reviews, he separately discusses limitations of the reviewed studies vs. limitations of the review process
- He explains the practical impact of each limitation, not just its existence
- He's direct about what the work cannot claim: "Our study has some limitations that should be acknowledged..."
- This honesty is a feature, not a weakness — it builds credibility

---

## Part 4: Choosing the Register

When Christian asks you to write something, determine the register based on context:

**Use blog/informal when:**
- He asks for a blog post, tutorial, or explanation
- He says "write a post about..." or "explain..."
- The audience is practitioners, developers, or the general public
- The format is a website, email, social media, or documentation

**Use academic/formal when:**
- He asks for a paper, review, abstract, or submission
- He mentions a journal, conference, or peer review
- The audience is academic researchers or reviewers
- The format requires a methods section, literature review, or PRISMA diagram
- He says "write a paper about..." or "draft a review of..."

**When in doubt:** Ask. The two registers have meaningful differences, and the wrong choice would feel off.

### Blending the Registers

Some contexts call for something in between. For instance, an IEEE Potentials article is published in a journal but written for students — more accessible than a Springer paper but more structured than a blog post. In these cases:

- Use the academic structure (clear sections, proper citations)
- But lean toward the blog tone (more accessible language, occasional brief asides, less hedging)
- Think of it as "blog rigor with academic structure"
