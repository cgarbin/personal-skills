# The mechanical scan

Design notes for `scripts/scan.py`. **text-review**'s mechanical scan section has what a review needs. This file has the routing, the checks that fire on correct prose, and the reasoning behind the two `REWRITE` checks.

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
| `unquantified` | "a few paragraphs" labels a case instead of measuring one. |
| `possession-verb` | A reader left holding evidence is the idiom. |
| `pointer` | "those that read the discharge summary" points at a group the same sentence names, and "the former CEO" means previous. |
| `feeling-word` | One per piece is fine when the reaction is itself information, and the script cannot count across a document. |

## Why contrastive-voice and comma-join are REWRITE

Both are `REWRITE`, so no test applies.

`contrastive-voice` replaced a `TEST` that asked whether a contrast was informative, which is the wrong property. On a manuscript arguing by elimination every instance passed that test and 91 still had to be restated. The judgment half of the old check lives on in `side-commentary`, whose stems reach the tails this pattern misses.

`comma-join` holds to about 85% precision on a full manuscript, 22 of 26. Its false positives are a two-item list after a colon, a coordinated pair of `that` clauses, a coordinated noun phrase, and a gapped coordination. It reads `and` alone, since every other coordinator states a relationship a period would drop.

## What the pointer check reads

Two demonstratives used as pronouns, "those" and "these" with no head noun after them, plus "that same", "this same", "the former" and "the latter".

"That" and "this" are left out. "That" opens every relative clause, so "the row that is empty" would fire. A sentence opening on "This is" usually points at the situation the paragraph just described, which is the sense that stays.

"That same" is in and "the same" is out. "The same X" fired 9 times on `BHC generation techniques in prior work` for 1 real hit, against "the same papers", "the same target" and "the same clinicians".

The words read after a demonstrative are auxiliaries and prepositions, so "Those cover the case" and "These show the gap" are missed. A plural noun is what blocks the wider list. After a demonstrative, "those runs" and "those counts" read as verbs by any stem. `comma_join`'s `FINITE` pattern hits the same limit.

The pro-forms left out are the ones no stem separates from ordinary use. "One" and "ones" are determiners as often as pro-forms ("the one entry", "the ones without"). "The two" and "the three" fired 46 times on one manuscript for one real hit. "It", "its", "they" and "them" are past counting. The pointer test in layer 3 is what reaches them.

What survives that narrowing still earns its place. On `BHC generation techniques in prior work` as it stood before the hand pass, it reported 5 hits, 4 of them defects that pass had found. It fires on 4 of the 13 pointers that pass rewrote, which is why layer 3 owns the rest. It prints 12 hits on a 5,036-line manuscript.

## What the semicolon check skips

The rule is a semicolon joining two independent clauses. The check masks the markup that needs one
of its own: an inline code span, a Pandoc multi-citation `[@a; @b]`, an HTML entity such as
`&nbsp;`, and a LaTeX escape such as `\;`. A fenced block never reaches the check at all, so a
shell command keeps its separators.

One chapter of a Pandoc manuscript fired 39 times before this and every one was markup. It fires
none now.

One markup case is left that no pattern reaches. A repo can mandate a contrastive comment in SQL
(**code-comments** rule 10), which `contrastive-voice` flags, and whether the repo mandates it sits
in its AGENTS.md.

Generated files are a separate matter. A Pandoc `body.tex` fires on every `2007;297:831--41` in its
bibliography. The scan is for files you wrote.

## Markdown drafting files

`--skip-html-comments` reads the published prose and skips `<!-- -->` notes. Half of one dissertation manuscript is storyline and provenance comments, and scanning them alongside the prose buried the real hits three to two.
