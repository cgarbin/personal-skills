#!/usr/bin/env python3
"""Measure whether an installed skill loads on a set of queries.

    ./scripts/trigger-eval.py <skill-name> <eval-set.json> [runs-per-query]

The eval set is a JSON array of {"query": str, "should_trigger": bool}.

skill-creator ships scripts/run_eval.py for this, but it registers the skill
under test by writing .claude/commands/<name>.md. Claude Code shows those
as user-invocable slash commands, which the model only calls when the user
types the name, so a bare task prompt never triggers one and every
description scores 0.0. This runs the query against the globally installed
skill instead. Competing skills are installed too, so their pull on the same
query is part of what gets measured.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TIMEOUT_S = 300


def replace_description(skill_md: str, description: str) -> str:
    """Return the SKILL.md text with a new description in its frontmatter."""
    parts = skill_md.split("---", 2)
    if len(parts) < 3 or parts[0].strip():
        raise ValueError("SKILL.md does not open with a --- frontmatter block")
    if re.search(r"^description:\s*[>|]", parts[1], re.MULTILINE):
        raise ValueError("description uses a block scalar, which this cannot rewrite")
    new, n = re.subn(r"^description: .*$", f"description: {description}",
                     parts[1], count=1, flags=re.MULTILINE)
    if n != 1:
        raise ValueError("no single-line description field in the frontmatter")
    return "---".join([parts[0], new, parts[2]])


@contextlib.contextmanager
def swapped_description(skill_md: Path, description: str | None):
    """Write a description into the skill for the duration of the run.

    `claude -p` reads the skill from disk on each call, so the variant has to
    be on disk to be measured. The restore is in a finally because a run that
    dies partway would otherwise leave the skill holding the variant. Only one
    eval can be in flight per skill for the same reason.
    """
    if description is None:
        yield
        return
    original = skill_md.read_text()
    try:
        skill_md.write_text(replace_description(original, description))
        yield
    finally:
        skill_md.write_text(original)


def skills_invoked(query: str, cwd: str) -> set[str]:
    """Names passed to the Skill tool during one run, empty if none."""
    # CLAUDECODE is unset so `claude -p` will nest inside a Claude Code
    # session. That check is there for interactive terminals, not subprocesses.
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


def measure(items: list[dict], skill: str, runs: int, workers: int) -> dict:
    # Run in an empty directory so no project context biases the model
    # toward or away from the skill.
    with tempfile.TemporaryDirectory() as cwd:
        jobs = [item for item in items for _ in range(runs)]
        with ThreadPoolExecutor(max_workers=workers) as pool:
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
    return {
        "skill_name": skill,
        "runs_per_query": runs,
        "summary": {"total": len(results), "passed": passed,
                    "failed": len(results) - passed},
        "results": results,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__ or "",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skill", help="skill name, as it appears in the Skill tool")
    ap.add_argument("eval_set", type=Path, help="JSON array of queries")
    ap.add_argument("runs", nargs="?", type=int, default=3,
                    help="runs per query (default 3, use 5+ to see past noise)")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--description",
                    help="test this description instead of the installed one")
    ap.add_argument("--skill-md", type=Path,
                    help="path to the SKILL.md to rewrite when --description "
                         "is given (default: skills/<skill>/SKILL.md)")
    args = ap.parse_args()

    items = json.loads(args.eval_set.read_text())
    skill_md = args.skill_md or REPO / "skills" / args.skill / "SKILL.md"

    if args.description and not skill_md.is_file():
        sys.exit(f"Error: no SKILL.md at {skill_md}")

    with swapped_description(skill_md, args.description):
        out = measure(items, args.skill, args.runs, args.workers)

    if args.description:
        out["description_tested"] = args.description
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
