# The mechanical scan

Design notes for `scripts/scan.py`. **text-review** layer 5 has what a review needs. This file has the routing, the checks that fire on correct prose, and the reasoning behind the two `REWRITE` checks.

Read it when a hit does not make sense, when you are deciding whether a check misfired, or when you are changing the script.

## What gets read

The extension decides. The rules that apply are the same either way.

A source file is reduced to its comment lines first, because `guard` and `canonical` are ordinary identifiers and a file-wide search buries the hits. Anything else is read as prose, with hard-wrapped lines joined so a phrase split across a line break still matches.

The em-dash check reads every line of a source file, because nothing in code needs one and the comment pass cannot see an error string or a log message. British spelling is not read that way, since it would match every word inside this script's own pattern list.

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
| `unquantified` | "a few paragraphs" as a bold lead-in labels a case. |
| `possession-verb` | A reader left holding evidence is the idiom. |
| `feeling-word` | One per piece is fine when the reaction is itself information, and the script cannot count across a document. |

## The two REWRITE checks

`contrastive-voice` and `comma-join` are `REWRITE`, so no test applies.

`contrastive-voice` replaced a `TEST` that asked whether a contrast was informative, which is the wrong property. On a manuscript arguing by elimination every instance passed that test and 91 still had to be restated. The judgment half of the old check lives on in `side-commentary`, whose stems reach the tails this pattern misses.

`comma-join` holds to about 85% precision on a full manuscript, 22 of 26. Its false positives are a two-item list after a colon, a coordinated pair of `that` clauses, a coordinated noun phrase, and a gapped coordination. It reads `and` alone, since every other coordinator states a relationship a period would drop.

## Markdown drafting files

`--skip-html-comments` reads the published prose and skips `<!-- -->` notes. Half of one dissertation manuscript is storyline and provenance comments, and scanning them alongside the prose buried the real hits three to two.
