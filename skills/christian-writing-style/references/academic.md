# Academic and formal register

For journal papers, conference papers, systematic reviews, dissertation chapters, abstracts, grant proposals.

Read this alongside the common foundation in SKILL.md. Nothing here licenses what the common foundation bans.

## Voice

More formal register, same core qualities of clarity, honesty, practical grounding.

- **Formal but clear.** Direct, declarative sentences. Avoid unnecessary complexity.
- **"We" throughout.** Even in single-author work, never "I."
- **Carefully hedged.** "The results suggest," "this may indicate," "one possible explanation is."
- **Evidence-dense.** Nearly every substantive claim has a citation.

## Sentence patterns

Longer than blog but still clear. Break complex ideas across multiple sentences.

- Clear topic sentences: "In this section, we review the methods and tools that have been proposed to address these challenges."
- Specific numbers: "Of the 48 papers, 42 (87.5%) used structured data from electronic health records."
- Hedged conclusions: "These results suggest that... however, further research is needed to..."
- Transitions that summarize what was just covered and preview what's next.

## Structure

**Empirical/experimental papers:**

1. Introduction: problem, motivation, contribution.
2. Related work / background.
3. Methods: setup, datasets, models, training, evaluation.
4. Results: numbers, tables, figures.
5. Discussion: interpretation, comparison, implications.
6. Limitations: thorough and honest.
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

## Writing the prose beside a results table

The common foundation states the rule: prose next to a table says what the numbers mean and never restates them. Two habits travel with it in results sections.

**Name the mechanism with the precise term.** "This number is confounded with the task" beats "it holds two different problems," which needs two more sentences to decode. When a defined technical term exists, a vague framing is not humility, it is work pushed onto the reader.

**One signpost clause.** "This section separates the two and characterizes the second" is enough. Adding "and then tests whether it is real" pads it. A third clause is usually where an inaccuracy creeps in, because it describes something the section does not quite do.

### Before and after

The same opening paragraph for a results section. Christian's version is second.

> Concept recall pools to 0.159, and read on its own that number says these models fail at the task. It holds two different problems. Most of the concepts it counts as missed were never in the model's input, which is a property of the task. Of the concepts that were there, the models produce about a third, which is a property of the models. This section separates the two, characterizes the second, and then tests whether it is real.
>
> The level is low on all three models while the trend matches the other metrics in Section 5.1, rising with admission size on Gemma and Qwen and moving without a clear direction on Llama.

> Concept recall is low in all three models, as shown in Table [ref]. However, this number cannot be interpreted as "the models have failed" because it is confounded with the task. Most of the concepts that the models miss were never in their input, which is a property of the task. Of the concepts that were there, the models produce about a third, which is a property of the models. This section separates the two and characterizes the second.

Five differences, and **the transferable content is these five. The wording is disposable.** A results paragraph with no two-way confound to separate should look nothing like this one.

1. **Points at the table instead of quoting a number from it.** The table holds the per-model figures. A pooled figure in the prose makes the reader reconcile two presentations of one fact. It reads as a discrepancy.
2. **Names the confound.** One clause with a defined term replaces three sentences of framing.
3. **Quotes the wrong reading and rejects it** ("cannot be interpreted as 'the models have failed'") instead of half-asserting it and then retracting.
4. **Keeps the plural.** The first version opens on "all three models" and slips to "the model's input."
5. **Stops one clause earlier.** The dropped clause was also inaccurate: the section tests alternative explanations for the gap.

The second paragraph is gone entirely. Per-model trend qualifiers belong in the table caption or in the section that owns the trend. Under the opening claim they bury it.

## Tables and figures

Christian uses tables extensively, a distinctive pattern.

- **Comparison tables**: multiple studies, methods, or tools side by side with consistent columns.
- **Summary tables**: condense large amounts of information into scannable formats.
- **Chronological tables**: evolution of methods or findings over time.
- Captions describe what the reader should take away.
- Figures for process flows (PRISMA, system architectures) and results visualizations.

## Bullets vs. prose

Same principle as the blog. Bullets appear in his published work for enumerated contributions, methodological steps, inclusion/exclusion criteria, lists of datasets or models, and limitation items. Bullets must not fragment a coherent argument.

## Practical grounding

Even in formal work, connect findings to practice:

- Explicit "implications for practitioners" or "lessons learned" sections.
- Discussion sections that go beyond restating results.
- Identifying gaps between research and practice.
- Concrete recommendations. "Future work should explore..." names none.

## Citations

- Dense throughout. Nearly every substantive paragraph cites a source.
- Synthesize across sources. Describe what multiple papers agree on, where they diverge, and what the overall picture suggests.
- Cite primary sources.
- References formatted per the target journal's style.
- In Obsidian markdown drafts, use Pandoc citation syntax: `[@smith2023temporal]`, `[@smith2023temporal, p. 42]`, `[@smith2023temporal; @jones2022ehr]`, `[-@key]` to suppress the author. Pandoc resolves these at compile time. Never write formatted references inline.

## Limitations sections

A hallmark of his academic writing.

- Limitations of both the work itself and the methods used.
- In systematic reviews, limitations of the reviewed studies separately from limitations of the review process.
- Practical impact of each limitation.
- Direct: "Our study has some limitations that should be acknowledged..."
