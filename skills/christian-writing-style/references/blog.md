# Blog and informal register

For blog posts, tutorials, explanations, project documentation, READMEs, ADRs, emails, social media.

Read this alongside the common foundation in SKILL.md. Nothing here licenses what the common foundation bans.

## Voice

Senior engineer explaining something to a smart colleague over coffee. Knowledgeable, never condescending.

- **Conversational but substantive.** Use technical terms, then explain them in plain language right away.
- **Inclusive.** "We" and "let's" frequently. ("Let's explore what 'learning' means for machine learning." / "We will start with a notebook that is not wrong but is not well written.")
- **Intellectually humble.** Acknowledge limits openly. ("well, it takes me some effort - your mileage may vary" / "The honest answer is 'we don't know'.")
- **Dry wit, sparingly.** Parenthetical asides appear in his posts: "(presumably, the human would chuckle, then - hopefully - slow down)" and "(a polite way to say 'the developers failed to account for how the world works')". Preserve one that is already in a draft. Do not manufacture one to sound like him.

## Personal voice has a rate limit

Personal reactions belong in this register. Stacking them does not. Two paragraph openings from one five-paragraph draft section:

> The first row is arithmetic, **and it is the one that surprised me least once I looked at it**.
>
> The fourth row is **the uncomfortable one**, because it says part of the 71% is not evidence that my pipeline works.

Both tell the reader how to feel about the row before saying what the row is, so the fact arrives late. Either one alone reads as voice. Two out of five openings, with a third opening on a contrastive framing, read as a tic.

Two habits keep it in range.

**Do not open consecutive paragraphs with a reaction to the material.** Let the fact lead and let the reaction follow it, or move the reaction into a later sentence.

**Feeling-words spent on a fact cost more than they look.** *Uncomfortable*, *surprising*, *striking*, *remarkable*. One in a piece is fine when the reaction is itself information, because "I did not expect this, and here is why" tells the reader something about the world. "The uncomfortable one" as a paragraph opener is decoration on a fact that stands without it.

## Voice is not commentary

The common foundation bans side commentary, meaning text that comments on the text instead of stating a fact. Personal voice is the other thing that sits in that space, and the two are easy to confuse here, which is why this register either suppresses both or produces both several times per section.

- **Voice** gives the reader something they did not have: a reaction, an uncertainty, a judgment you would defend. "The honest answer is 'we don't know'." Keep it, at the rate above.
- **Commentary** repeats what the sentence already said, or names what a fact is *not* where no reader would have assumed otherwise. "That is the whole purpose of the labels." Cut it at any density.

When the call is close, delete the clause and reread. If a fact, a number, a constraint, or a claim you would defend went missing, it was voice. If only the tone changed, it was commentary.

## Sentence patterns

Mix short and medium sentences. Important thoughts get short sentences for emphasis.

- "That's all." (after a technical explanation)
- "Does it mean we need to stop using neural networks until then? No."
- "The neural network may be _learning_, but it is definitely not _understanding_."
- "So far, so good, but..."

Rhetorical questions as transitions: "Should we be concerned that deep 'learning' is not 'understanding'?"

## Structure

1. **Opening hook.** Framing question, relatable scenario, or clear problem statement. Never throat-clearing. ("In the expression _machine learning_, are the machines actually learning anything?")
2. **Roadmap.** Brief, natural overview of what's coming.
3. **Progressive disclosure.** Simple to complex.
4. **"Why does this matter?" moments.** After a technical result, pause to explain real-world significance, often with an explicit header.
5. **Honest endings.** No forced tidy conclusions on messy topics.

## Formatting

- H2/H3 headers, often conversational: "When are squares not squares?" / "If all we have is a hammer..."
- Italics for technical terms on first use and for emphasis.
- Bold sparingly, for key takeaways. Bold+italic for maximum emphasis: ***the neural network does not understand the concept of "square".***
- Blockquotes with attribution for direct citations.
- Inline links to papers, repos, tools, used generously.
- Notice blocks (`{: .notice}`) for key insights or caveats.
- Code blocks with brief explanations.
- Images with alt text and captions explaining what to notice.

## Bullets vs. prose

If content is naturally a list, write it as a list: scannable reference items, parallel options, discrete steps, side-by-side comparisons. If the items connect with "because" or "but," write prose. Those connectives are part of the reasoning, and bullets hide them.

## Transitions

- "In other words..." to rephrase a complex idea.
- "But there is a twist..." to introduce a complication.
- "Coming from an engineering background..." to ground a point.
- Short bridging sentences: "We will fix some of the issues in the next step."
