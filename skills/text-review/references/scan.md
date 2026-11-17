# The mechanical scan

Design notes for `scripts/scan.py`. **text-review**'s mechanical scan section has what a review needs. This file has the routing, the checks that fire on correct prose, and the reasoning behind the two `REWRITE` checks.

Read it when a hit does not make sense, when you are deciding whether a check misfired, or when you are changing the script.

## What gets read

The extension decides. The rules that apply are the same either way.

A source file is reduced to its comment lines first, because `guard` and `canonical` are ordinary identifiers and a file-wide search buries the hits. Anything else is read as prose, with hard-wrapped lines joined so a phrase split across a line break still matches.

The em-dash check reads every line of a source file, because nothing in code needs one and the comment pass cannot see an error string or a log message. British spelling is not read that way, since it would match every word inside this script's own pattern list.

The scan is for files you wrote. A generated file such as a Pandoc `body.tex` fires on every `2007;297:831--41` in its bibliography.

## Which checks run where

The voice checks run on everything, since a rule about his voice holds wherever the text sits.

Source files add the three code-comments stems: `jargon`, `dead-code-ref`, and `plan-label`. They stay out of prose, where "Step 1" is a heading and no kind of plan label.

Prose adds two of its own.

- `specialist-term` asks the curse-of-knowledge question about the same words the `jargon` stem bans outright in a comment.
- `long-sentence` counts the words between two sentence boundaries. It stays out of source files, where the comment pass reads one physical line at a time and a wrapped sentence never reaches the limit in one unit.

## Which checks fire on correct prose

These are tagged `TEST` because reporting them raw would bury the real findings.

| Check | Why it fires on correct prose |
| --- | --- |
| `side-commentary`, `concrete-thing`, `nominalization-lead`, `soft-verb`, `specialist-term` | "axis" and "stack" are ordinary words in a paper about models, "Precision improved to 0.8" is not a zombie noun, and "API surface" is a noun. |
| `dead-code-ref` | "the target no longer exists" usually describes a missing file. |
| `long-sentence` | A sentence that runs long because it enumerates is doing its job. |
| `unquantified` | "a few paragraphs" labels a case instead of measuring one. |
| `possession-verb` | A reader left holding evidence is the idiom. |
| `pointer` | "those that read the discharge summary" points at a group the same sentence names, and "the former CEO" means previous. |
| `feeling-word` | One per piece is fine when the reaction is itself information, and the script cannot count across a document. |
| `comma-so` | "A retriever can only pick records, so no retriever can deliver more" keeps its comma, since a reader would doubt "no retriever can deliver more" without the first clause. |

## Why contrastive-voice and comma-join are REWRITE

Both are `REWRITE`, so no test applies.

`contrastive-voice` has no test because the rule governs the phrasing. An informative contrast is still restated. On a manuscript arguing by elimination, 91 of them had to be. The judgment about a contrastive tail belongs to `side-commentary`, whose stems reach the tails this pattern misses.

A repo can mandate a contrastive comment in SQL (**code-comments** rule 10). `contrastive-voice` flags it anyway. Whether the repo mandates one is in its AGENTS.md, which no pattern reads.

`comma-join` holds to about 85% precision on a full manuscript, 22 of 26. Its false positives are a two-item list after a colon, a coordinated pair of `that` clauses, a coordinated noun phrase, and a gapped coordination. It reads `and` alone.

## What comma-so asks first

`comma-so` fires on `, so that` and on a bare `, so` that states a purpose. Both take `so that` with no comma. The purpose test comes first because a purpose clause reads like a design choice and gets kept. The purpose test reads the verb. An action done for an end ("gives", "stores", "stratified") is purpose. A state ("has no score", "stays out") is a result.

## What the pointer check reads

Two demonstratives used as pronouns, "those" and "these" with no head noun after them, plus "that same", "this same", "the former" and "the latter".

"That" and "this" are left out. "That" opens every relative clause, so "the row that is empty" would fire. A sentence opening on "This is" usually points at the situation the paragraph just described, which is the sense that stays.

"That same" is in and "the same" is out. "The same X" fired 9 times on one chapter for 1 real hit, against "the same papers", "the same target" and "the same clinicians".

The check misses a pointer followed by a lexical verb, such as "Those cover the case" and "These show the gap". The comment on `POINTER_TAIL` gives the reason. `comma_join`'s `FINITE` pattern hits the same limit.

The pro-forms left out are the ones no stem separates from ordinary use. "One" and "ones" are determiners as often as pro-forms ("the one entry", "the ones without"). "The two" and "the three" fired 46 times on one manuscript for one real hit. "It", "its", "they" and "them" are past counting. The pointer test in layer 3 is what reaches them.

What survives that narrowing still earns its place. On one chapter most of its hits were real defects, but it found only about a third of the pointers a hand pass rewrote. Layer 3 owns the rest.

## What the semicolon check skips

The rule is a semicolon joining two independent clauses. The check masks the markup that needs one of its own: an inline code span, a Pandoc multi-citation `[@a; @b]`, an HTML entity such as `&nbsp;`, and a LaTeX escape such as `\;`. A fenced block never reaches the check at all, so a shell command keeps its separators.

## Markdown drafting files

`--skip-html-comments` reads the published prose and skips `<!-- -->` notes. On a drafting file the storyline and provenance comments can outnumber the prose. Their hits bury the real ones.
