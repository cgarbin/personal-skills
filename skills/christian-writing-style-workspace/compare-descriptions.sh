#!/usr/bin/env bash
# Compare candidate descriptions for christian-writing-style against the same
# trigger set, to find the shortest one that still loads reliably. A
# description is always in context, so length is a standing cost.
#
# Each variant is written into the skill for the length of its run, because
# `claude -p` reads the skill from disk. Runs are sequential: two at once
# would fight over that file, and concurrent claude processes distort each
# other's timing.
#
# Results are written to this directory as trigger-<variant>.json, which
# .gitignore excludes. Compare the summary blocks, then the per-query rates
# for the queries that disagree.

set -euo pipefail

W="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$W/../.." && pwd)"
EVAL_SET="$W/trigger-eval.json"
RUNS="${1:-5}"

# Three runs per query lets one run flipping look like a real regression.
# Five is the floor for telling noise from a change.
if [[ "$RUNS" -lt 5 ]]; then
    echo "Warning: $RUNS runs per query is below the noise floor." >&2
fi

MID="Apply Christian Garbin's writing style to any prose under his name: papers, dissertation chapters, blog posts, READMEs, ADRs, docs, emails, commit messages, PR descriptions, code comments. Use it whenever he asks to write, draft, or edit prose, and whenever you create or edit a hand-written .md file, even when he says nothing about style."

SHORT="Apply Christian Garbin's writing style whenever writing or editing prose under his name: papers, blog posts, docs, READMEs, commit messages, PR descriptions, code comments, emails."

run() {
    local name="$1"
    shift
    echo "### $name ###"
    python3 "$REPO/scripts/trigger-eval.py" christian-writing-style "$EVAL_SET" \
        "$RUNS" "$@" > "$W/trigger-$name.json"
    python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['summary'])" \
        "$W/trigger-$name.json"
}

# No --description, so this measures whatever is in the skill right now.
run installed
run mid --description "$MID"
run short --description "$SHORT"

echo "ALL DONE"
