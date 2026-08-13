#!/usr/bin/env python3
"""Measure whether an installed skill triggers on a set of queries.

Usage:
    ./scripts/trigger-eval.py <skill-name> <eval-set.json> [runs-per-query]

The eval set is a JSON array of {"query": str, "should_trigger": bool}.

skill-creator ships scripts/run_eval.py for this, but it registers the skill
under test by writing .claude/commands/<name>.md. Claude Code surfaces those
as user-invocable slash commands, which the model only calls when the user
types the name, so every description scores 0.0 there. This runs the query
against the globally installed skill instead. Competing skills are installed
too, so their pull on the same query is part of what gets measured.
"""

import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

WORKERS = 6
TIMEOUT_S = 300


def skills_invoked(query: str, cwd: str) -> set[str]:
    """Names passed to the Skill tool during one run, empty if none."""
    # CLAUDECODE is unset so `claude -p` will nest inside a Claude Code
    # session. The guard exists for interactive terminals, not subprocesses.
    cmd = ["env", "-u", "CLAUDECODE", "claude", "-p", query,
           "--output-format", "stream-json", "--verbose"]
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True,
                             text=True, timeout=TIMEOUT_S).stdout
    except subprocess.TimeoutExpired:
        return set()

    found: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            if node.get("type") == "tool_use" and node.get("name") == "Skill":
                name = (node.get("input") or {}).get("skill")
                if name:
                    found.add(name)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for line in out.splitlines():
        try:
            walk(json.loads(line))
        except json.JSONDecodeError:
            continue
    return found


def main() -> None:
    if len(sys.argv) < 3:
        print("usage: trigger-eval.py <skill-name> <eval-set.json> "
              "[runs-per-query]", file=sys.stderr)
        sys.exit(1)

    skill = sys.argv[1]
    items = json.loads(Path(sys.argv[2]).read_text())
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    # Run in an empty directory so no project context biases the model
    # toward or away from the skill.
    with tempfile.TemporaryDirectory() as cwd:
        jobs = [item for item in items for _ in range(runs)]
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            invoked = list(pool.map(lambda j: skills_invoked(j["query"], cwd), jobs))

    by_query: dict[str, list[set[str]]] = {}
    for item, names in zip(jobs, invoked):
        by_query.setdefault(item["query"], []).append(names)

    results = []
    for item in items:
        seen = by_query[item["query"]]
        hits = sum(1 for names in seen if skill in names)
        others: dict[str, int] = {}
        for names in seen:
            for other in names - {skill}:
                others[other] = others.get(other, 0) + 1
        rate = hits / len(seen)
        results.append({
            "query": item["query"],
            "should_trigger": item["should_trigger"],
            "trigger_rate": rate,
            "runs": len(seen),
            "other_skills": others,
            "pass": (rate >= 0.5) == item["should_trigger"],
        })

    passed = sum(1 for r in results if r["pass"])
    print(json.dumps({
        "skill_name": skill,
        "runs_per_query": runs,
        "summary": {"total": len(results), "passed": passed,
                    "failed": len(results) - passed},
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
