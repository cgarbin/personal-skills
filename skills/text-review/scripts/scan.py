#!/usr/bin/env python3
"""Mechanical scan for text-review layer 5 and the code-comments scan.

Prose mode runs on markdown and text. Comment mode extracts comment lines from
source files first, because every code-comments stem is also ordinary code
vocabulary and a file-wide search buries the hits in identifiers and literals.

Hits are candidates, not verdicts. Checks tagged JUDGE fire often enough on
correct prose that reporting them raw buries the real findings.

Exit status: 0 clean, 1 hits found, 2 usage error.

    scripts/scan.py draft.md
    scripts/scan.py --comments src/chunker.py src/loader.go
    scripts/scan.py --only citation,british paper.md
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# (name, pattern, judge_before_reporting)
PROSE_CHECKS = [
    ("em-dash", r"—", False),
    ("semicolon", r";", False),
    # "analysis" is a correct US spelling, so that stem needs the verb endings.
    ("british", r"(?i)\b\w*(?:analys(?=e|ed|es|ing)|colour|behaviour|flavour|honour|"
                r"favour|labour|neighbour|rumour|humour|endeavour|vapour|odour|"
                r"modelling|labell|cancell|travell|signall|centre|defence|licence|"
                r"practis(?=e|ed|es|ing)|whilst|programme|artefact)\w*", False),
    # Endings are required. "specialist", "criticism", "formalist", "emphasis"
    # are correct US spellings.
    ("british-ise", r"(?i)\b(?:organis|recognis|realis|summaris|characteris|generalis|"
                    r"minimis|maximis|optimis|prioritis|standardis|utilis|categoris|"
                    r"normalis|specialis|visualis|criticis|apologis|familiaris|personalis|"
                    r"formalis|initialis|serialis|tokenis|emphasis)"
                    r"(?:e|ed|es|ing|ation|ations)\b", False),
    ("filler-opener", r"(?i)^\W*(?:it is worth noting|note that|interestingly|"
                      r"it is important to|as we all know|in today's)", False),
    ("nominalization-lead", r"^\W*[A-Z]\w+(?:tion|ment|ance|ence)\b", False),
    ("single-word-lead", r"^\*{0,2}[A-Z]\w+\.\*{0,2}\s*$", False),
    ("feeling-word", r"(?i)\b(?:uncomfortable|surprising|surprised|striking|remarkable)\b", True),
    ("layout-announce", r"(?i)the rest of this section|the sections below|"
                        r"what the table cannot|each item gets|as (?:described|shown) below", False),
    ("concrete-thing", r"(?i)\b(?:lands?|landed|carr(?:y|ies|ied)|stack|arm|frontier|"
                       r"axes|lever|downstream)\b", True),
    ("vague-quantifier", r"(?i)\b(?:elevated|tighten)\b|various factors|had issues", False),
    # Opt-in. A paper with 80 citations would otherwise drown every other check.
    ("citation", r"\[@", False),
    # Side commentary reappears in new wording each time, so match stems.
    ("side-commentary", r"(?i)deliberat|intentional|on purpose|by design|we do not claim|"
                        r"does not (?:claim|argue)|(?:attributes|makes|takes) no|"
                        r"rather than the reverse|the other way around|not just|"
                        r"which is worth|that is the", True),
    # Bold lead-in labels ("Restatements go, conclusions stay") are a house
    # pattern, not hits.
    ("contrastive-tail", r",\s+not\s+|\s+rather\s+than\s+", True),
]

OPT_IN = {"citation"}

COMMENT_CHECKS = [
    ("jargon", r"(?i)\b(?:guard|invariant|idempotent|canonical|load-bearing|downstream)\b", False),
    ("dead-code-ref", r"(?i)used to|no longer|after decoupling|the old\b|the deleted\b", False),
    ("plan-label", r"(?i)\bcluster\s*[A-Z]?\d|\bstep\s*\d|this task|^\W*[A-Z]\d\s*:", False),
]

LINE_COMMENT = {
    ".py": "#", ".sh": "#", ".bash": "#", ".zsh": "#", ".rb": "#", ".yaml": "#",
    ".yml": "#", ".toml": "#", ".tf": "#", ".r": "#", ".pl": "#",
    ".go": "//", ".js": "//", ".mjs": "//", ".cjs": "//", ".ts": "//", ".tsx": "//",
    ".jsx": "//", ".java": "//", ".kt": "//", ".c": "//", ".h": "//", ".cpp": "//",
    ".hpp": "//", ".cs": "//", ".rs": "//", ".swift": "//", ".scala": "//",
    ".php": "//", ".css": "//", ".scss": "//",
    ".sql": "--", ".lua": "--",
}

BLOCK_DELIMITERS = (('"""', '"""'), ("'''", "'''"), ("/*", "*/"))

# A new prose unit starts here rather than continuing the one above.
UNIT_START = re.compile(r"^\s*(?:#{1,6}\s|[-*+]\s|\d+\.\s|>\s|\||```|~~~)")


def prose_units(path):
    """Yield (lineno, text) with hard-wrapped lines joined into one unit.

    Phrase patterns like "the rest of this section" straddle a newline in wrapped
    markdown and match nothing when each physical line is tested on its own. The
    line number reported is where the unit starts.
    """
    unit, start, in_fence = [], None, False
    for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        fence = line.lstrip().startswith(("```", "~~~"))
        if not line.strip() or (UNIT_START.match(line) and not in_fence) or fence:
            if unit:
                yield start, " ".join(unit)
                unit, start = [], None
        if fence:
            in_fence = not in_fence
        if line.strip():
            if start is None:
                start = n
            unit.append(line.strip())
        if in_fence or fence:
            # Code blocks stay one line per unit so the reported context is readable.
            if unit:
                yield start, " ".join(unit)
                unit, start = [], None
    if unit:
        yield start, " ".join(unit)


def comment_lines(path):
    """Yield (lineno, text) for comment lines only.

    Block comments and docstrings are matched loosely, so a stray delimiter inside
    a string literal pulls in code lines.
    """
    marker = LINE_COMMENT.get(path.suffix.lower())
    if marker is None:
        print(f"skip {path} (no comment syntax known for {path.suffix or 'this file'})",
              file=sys.stderr)
        return
    in_block = False
    for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        if in_block:
            yield n, line
            if any(closer in line for _, closer in BLOCK_DELIMITERS):
                in_block = False
            continue
        for opener, closer in BLOCK_DELIMITERS:
            if opener in line:
                idx = line.index(opener)
                yield n, line[idx:]
                if closer not in line[idx + len(opener):]:
                    in_block = True
                break
        else:
            if marker in line:
                yield n, line[line.index(marker):]


def scan(path, checks, comments=False):
    source = comment_lines(path) if comments else prose_units(path)
    seen, hits = set(), []
    for n, text in source:
        for name, pattern, judge in checks:
            for m in re.finditer(pattern, text):
                key = (name, n, m.group(0).lower())
                if key in seen:
                    continue
                seen.add(key)
                start, end = max(0, m.start() - 30), min(len(text), m.end() + 30)
                hits.append((name, judge, n, m.group(0), text[start:end].strip()))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--comments", action="store_true",
                    help="scan comment lines of source files with the code-comments rules")
    ap.add_argument("--only", help="comma-separated check names, the only way to run "
                                   f"the opt-in checks ({', '.join(sorted(OPT_IN))})")
    ap.add_argument("--summary", action="store_true", help="counts per check, no hit lines")
    args = ap.parse_args()

    all_checks = COMMENT_CHECKS if args.comments else PROSE_CHECKS
    if args.only:
        wanted = {n.strip() for n in args.only.split(",")}
        checks = [c for c in all_checks if c[0] in wanted]
        if not checks:
            print(f"no checks match {args.only}. available: "
                  + ", ".join(c[0] for c in all_checks), file=sys.stderr)
            return 2
    else:
        checks = [c for c in all_checks if c[0] not in OPT_IN]

    totals = Counter()
    for path in args.paths:
        if not path.is_file():
            print(f"skip {path} (not a file)", file=sys.stderr)
            continue
        for name, judge, n, match, context in scan(path, checks, comments=args.comments):
            totals[name] += 1
            if not args.summary:
                tag = f"{name} JUDGE" if judge else name
                print(f'{path}:{n}: [{tag}] "{match}" ...{context}...')

    if totals:
        sys.stdout.flush()
        print("\n".join(f"{c:>5}  {name}" for name, c in totals.most_common()),
              file=sys.stderr)
    return 1 if totals else 0


if __name__ == "__main__":
    sys.exit(main())
