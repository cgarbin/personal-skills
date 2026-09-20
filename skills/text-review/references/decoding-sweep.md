# The decoding-step sweep on a manuscript

The procedure **text-review** layer 3's decoding-step test points at when the subject is a whole manuscript. On a section, a diff, or a blog post, that test is the whole of it and this file is not needed.

The statistic, artifact, and ordinal patterns are in christian-writing-style (Name the concrete thing).

**The one test.** Name the step the reader currently has to take. Christian's own diagnosis, on "Llama's median is the fastest at every stratum through 64K":

> "Llama's median" forces the reader to stop and think "median of what?". Then comes "fastest", and the reader thinks "perhaps time then?". Don't generate all this extraneous cognitive load. Simpler: "Llama's generation time".

If you cannot name a concrete decoding step, it is not a finding.

**Procedure.** One agent per chapter. The first chapter runs alone. Its accepted fixes go to the rest, dispatched in parallel.

1. Extract the range to a scratchpad file. Scan it with `--skip-html-comments`. Answer the `TEST` groups before dispatching, so the agent does not spend findings on them.
2. Dispatch a read-only agent with the test above, those three patterns, and accepted fixes from a chapter already done. The worked examples are what keep the report at ten usable findings instead of thirty padded ones.
3. Give it four guards, or it returns a rewrite pass. Clear cases only, a word or a clause, never a paragraph restructure. Repetition is not a defect, so a restated figure never becomes a cross-reference. Precision beats brevity: units, intervals, version pins, and thresholds stay. The document's defined terms never get simplified away, so list them.
4. Verify every factual claim in the report against the source table before presenting any of it. Three of one chapter's ten rested on table arithmetic. A review agent in the same session got the arithmetic backwards. The reviewer relayed it to Christian without checking.
5. Present as a table: line, current, the step the reader takes, proposed. He strikes what he does not want.
6. Apply in one pass, using the anchor check in **text-review** under Check what a pass deleted. Then rescan only the changed lines and answer any surviving `TEST` hit in one line.

**What the sweep is not for.** It finds no wrong claims and no missing arguments, because it never asks whether a passage should exist. Run it after the claim-level review.
