#!/usr/bin/env python3
"""Mechanical scan for text-review layer 5 and the code-comments scan.

The file extension picks what to read. A source file is reduced to its comment
lines first, because every code-comments stem is also ordinary code vocabulary
and a file-wide search buries the hits in identifiers and literals. Anything
else is read as prose. WHOLE_FILE names the exception, a check that reads every
line of a source file so it can reach an error string.

Rules do not split the same way. The voice checks run on everything, and each
side holds back the checks that only mean something there: COMMENT_CHECKS stay
out of prose, where "Step 1" is a heading rather than a dead plan label, and
PROSE_ONLY_CHECKS stay out of comments, where the same words are already an
absolute violation rather than a judgment call.

Hits are candidates, not verdicts. Each check declares the action it needs, and
the report groups by that action so a find-and-replace does not sit in the same
list as a call that needs judgment:

    FIX      the replacement is determined
    REWRITE  always a violation, but the wording has to change
    TEST     apply the test named on the hit, then decide

Exit status: 0 clean, 1 hits found, 2 usage error.

    scripts/scan.py draft.md
    scripts/scan.py draft.md src/chunker.py src/loader.go
    scripts/scan.py --only citation,british paper.md
"""

import argparse
import re
import sys
from collections import Counter, namedtuple
from pathlib import Path

# note holds what the action needs: the replacement for FIX, the test to apply
# for TEST. rule points at the prose that explains the pattern, because copying
# that prose here would make a third place to keep in sync with the skill files.
Check = namedtuple("Check", "name pattern action note rule")
Hit = namedtuple("Hit", "check path line match context")

AVOID = "christian-writing-style, What to avoid"
CONCRETE = "christian-writing-style, Name the concrete thing"
COMMENTARY = "christian-writing-style, Side commentary"

PROSE_CHECKS = [
    Check("em-dash", r"—", "FIX",
          "use a period or parentheses", AVOID),
    Check("semicolon", r";", "FIX",
          "use a period between independent clauses. In pseudo-code or table "
          "structure it stays", AVOID),
    # "analysis" and its plural "analyses" are correct US spellings, so the stem
    # needs the verb endings and has to stop short of "-es". That gives up the
    # British verb in "he analyses the data", which is rarer in his register than
    # the plural noun in "the analyses show".
    Check("british", r"(?i)\b\w*(?:analys(?=e(?!s)|ing)|colour|behaviour|flavour|honour|"
                     r"favour|labour|neighbour|rumour|humour|endeavour|vapour|odour|"
                     r"modelling|labell|cancell|travell|signall|centre|defence|licence|"
                     r"practis(?=e|ed|es|ing)|whilst|programme|artefact)\w*", "FIX",
          "use the US spelling", AVOID),
    # Endings are required. "specialist", "criticism", "formalist", "emphasis"
    # are correct US spellings.
    Check("british-ise", r"(?i)\b(?:organis|recognis|realis|summaris|characteris|generalis|"
                         r"minimis|maximis|optimis|prioritis|standardis|utilis|categoris|"
                         r"normalis|specialis|visualis|criticis|apologis|familiaris|personalis|"
                         r"formalis|initialis|serialis|tokenis|emphasis)"
                         r"(?:e|ed|es|ing|ation|ations)\b", "FIX",
          "use the US spelling", AVOID),
    Check("filler-opener", r"(?i)^\W*(?:it is worth noting|note that|interestingly|"
                           r"it is important to|as we all know|in today's)", "REWRITE",
          "open with the point", AVOID),
    # "sion" is here for the section-label form ("Discussion.", "Conclusion.").
    # It also fires on concrete nouns that open a sentence ("Precision improved
    # to 0.8"), which is why this check needs the test rather than a rewrite.
    Check("nominalization-lead", r"^\W*[A-Z]\w+(?:tion|sion|ment|ance|ence)\b", "TEST",
          "is the noun a verb in disguise? \"Configuration of the parser\" is a "
          "lead, \"Precision improved to 0.8\" is not",
          "christian-writing-style, Avoid zombie nouns"),
    Check("feeling-word", r"(?i)\b(?:uncomfortable|surprising|surprised|striking|remarkable)\b",
          "TEST",
          "one per piece is fine when the reaction is itself information, so "
          "count the others before flagging this one",
          "christian-writing-style references/blog.md, Personal voice has a rate limit"),
    Check("layout-announce", r"(?i)the rest of this section|the sections below|"
                             r"what the table cannot|each item gets|as (?:described|shown) below",
          "REWRITE",
          "a table followed by per-item sections is self-evident, so cut the sentence",
          "christian-writing-style, Show, don't tell"),
    Check("concrete-thing", r"(?i)\b(?:land(?:s|ed|ings?)?|carr(?:y|ies|ied|ying)|stacks?|"
                            r"arms?|frontiers?|ax[ei]s|levers?|downstream|"
                            r"load[- ]bearing)\b", "TEST",
          "framing vocabulary, or the literal thing? Name the specific thing if "
          "it is framing", CONCRETE),
    Check("vague-quantifier", r"(?i)\b(?:elevated|tighten)\b|various factors|had issues",
          "REWRITE",
          "give the number, or name what went wrong", CONCRETE),
    Check("soft-verb", r"(?i)\b(?:surfac(?:e|es|ed|ing)|leverag(?:e|es|ed|ing)|"
                       r"unlock(?:s|ed|ing)?)\b", "TEST",
          "a verb standing in for a plainer one? \"surfaces those\" is \"shows "
          "those\". A noun (API surface) or a status label is fine", AVOID),
    # Opt-in. A paper with 80 citations would otherwise drown every other check.
    Check("citation", r"\[@", "TEST",
          "was this key checked against a source, or recalled? The script finds "
          "the keys, not where they came from",
          "text-review, layer 1"),
    # Side commentary reappears in new wording each time, so match stems.
    Check("side-commentary", r"(?i)deliberat|intentional|on purpose|by design|we do not claim|"
                             r"does not (?:claim|argue)|(?:attributes|makes|takes) no|"
                             r"rather than the reverse|the other way around|not just|"
                             r"which is worth|that is the", "TEST",
          "delete the clause and reread. If no fact, number, constraint, or "
          "claim is lost, the deletion stands", COMMENTARY),
    # Bold lead-in labels ("Restatements go, conclusions stay") are a house
    # pattern, not hits.
    Check("contrastive-tail", r",\s+not\s+|\s+rather\s+than\s+", "TEST",
          "keep the contrast only when the alternative was tried, a reader "
          "would assume it, or the argument depends on ruling it out", COMMENTARY),
]

OPT_IN = {"citation"}

# Held back from source files, where the same words are covered by the absolute
# form of the rule in COMMENT_CHECKS.
PROSE_ONLY_CHECKS = [
    Check("specialist-term", r"(?i)\b(?:guard|invariant|idempotent|canonical)\b", "TEST",
          "standard for this audience, or does a plain word of the same length "
          "exist? \"canonical order\" is \"fixed order\"",
          "christian-writing-style, Fight the curse of knowledge"),
]

COMMENT_CHECKS = [
    Check("jargon", r"(?i)\b(?:guard|invariant|idempotent|canonical|load[- ]bearing|downstream)\b",
          "REWRITE",
          "name the thing in this code: \"the check above\", \"the file the "
          "script reads\"", "code-comments rule 1"),
    # "no longer" and "the old" describe runtime state as often as dead code
    # ("the target no longer exists"), so this one asks rather than asserts.
    Check("dead-code-ref", r"(?i)used to|no longer|after decoupling|the old\b|the deleted\b",
          "TEST",
          "about code that stopped running, or about runtime state like a "
          "missing file? Only the first is a violation",
          "code-comments rule 8"),
    Check("plan-label", r"(?i)\bcluster\s*[A-Z]?\d|\bstep\s*\d|this task|^\W*[A-Z]\d\s*:",
          "REWRITE",
          "the plan is not in the repo, so the label points nowhere",
          "code-comments rule 9"),
]

# Block delimiters are per language. Applying them everywhere reads the "/*" in
# a shell string like "Read(secrets/**)" as a comment opener and swallows the
# rest of the file.
C_BLOCK = (("/*", "*/"),)
PY_BLOCK = (('"""', '"""'), ("'''", "'''"))
NO_BLOCK = ()

# extension -> (line marker, block delimiter pairs)
COMMENT_SYNTAX = {
    ".py": ("#", PY_BLOCK),
    ".sh": ("#", NO_BLOCK), ".bash": ("#", NO_BLOCK), ".zsh": ("#", NO_BLOCK),
    ".rb": ("#", NO_BLOCK), ".yaml": ("#", NO_BLOCK), ".yml": ("#", NO_BLOCK),
    ".toml": ("#", NO_BLOCK), ".tf": ("#", NO_BLOCK), ".r": ("#", NO_BLOCK),
    ".pl": ("#", NO_BLOCK),
    ".go": ("//", C_BLOCK), ".js": ("//", C_BLOCK), ".mjs": ("//", C_BLOCK),
    ".cjs": ("//", C_BLOCK), ".ts": ("//", C_BLOCK), ".tsx": ("//", C_BLOCK),
    ".jsx": ("//", C_BLOCK), ".java": ("//", C_BLOCK), ".kt": ("//", C_BLOCK),
    ".c": ("//", C_BLOCK), ".h": ("//", C_BLOCK), ".cpp": ("//", C_BLOCK),
    ".hpp": ("//", C_BLOCK), ".cs": ("//", C_BLOCK), ".rs": ("//", C_BLOCK),
    ".swift": ("//", C_BLOCK), ".scala": ("//", C_BLOCK), ".php": ("//", C_BLOCK),
    # CSS has no line comment, so it gets the block form only.
    ".css": (None, C_BLOCK), ".scss": ("//", C_BLOCK),
    ".sql": ("--", C_BLOCK), ".lua": ("--", NO_BLOCK),
}

# A new prose unit starts here rather than continuing the one above.
UNIT_START = re.compile(r"^\s*(?:#{1,6}\s|[-*+]\s|\d+\.\s|>\s|\||```|~~~)")

SENTENCE_END = re.compile(r"(?<=[.!?])\s")

# Checks that read every line of a source file rather than the comments alone,
# so they reach an error string or a log message. Only em-dash qualifies:
# nothing in code needs one, so the sole false positive is a linter declaring
# the character, while British spelling would match every word inside this
# script's own pattern list.
WHOLE_FILE = {"em-dash"}


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

    The line marker has to start the line or follow whitespace, so the "#" in
    "$#" and the "//" in a URL are not read as comment openers. Block comments
    are still matched loosely, so a delimiter inside a string literal pulls in
    the code lines after it until the closer shows up.
    """
    marker, blocks = COMMENT_SYNTAX[path.suffix.lower()]
    line_start = re.compile(r"(?:^|(?<=\s))" + re.escape(marker)) if marker else None
    in_block = False
    for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        if in_block:
            yield n, line
            if any(closer in line for _, closer in blocks):
                in_block = False
            continue
        for opener, closer in blocks:
            if opener in line:
                idx = line.index(opener)
                yield n, line[idx:]
                if closer not in line[idx + len(opener):]:
                    in_block = True
                break
        else:
            m = line_start.search(line) if line_start else None
            if m:
                yield n, line[m.start():]


def sentence_around(text, start, end, cap=320):
    """Return the sentence holding text[start:end].

    A fixed window cuts the clause in half, and the deletion test a TEST hit asks
    for cannot be applied to half a clause. The cap keeps one long unit from
    printing a whole paragraph.
    """
    left = 0
    for m in SENTENCE_END.finditer(text[:start]):
        left = m.end()
    m = SENTENCE_END.search(text, end)
    right = m.start() if m else len(text)
    if right - left <= cap:
        return text[left:right].strip()
    pad = max(0, (cap - (end - start)) // 2)
    return text[max(left, start - pad):min(right, end + pad)].strip()


def all_lines(path):
    for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        yield n, line


def is_source(path):
    return path.suffix.lower() in COMMENT_SYNTAX


def checks_for(path, wanted=None):
    """Return every voice check, plus the ones that only mean something here."""
    checks = PROSE_CHECKS + (COMMENT_CHECKS if is_source(path) else PROSE_ONLY_CHECKS)
    if wanted:
        return [c for c in checks if c.name in wanted]
    return [c for c in checks if c.name not in OPT_IN]


def scan(path, checks):
    if is_source(path):
        passes = [(comment_lines(path), checks),
                  (all_lines(path), [c for c in checks if c.name in WHOLE_FILE])]
    else:
        passes = [(prose_units(path), checks)]
    seen, hits = set(), []
    for source, active in passes:
        if not active:
            continue
        for n, text in source:
            for check in active:
                for m in re.finditer(check.pattern, text):
                    key = (check.name, n, m.group(0).lower())
                    if key in seen:
                        continue
                    seen.add(key)
                    hits.append(Hit(check, path, n,
                                    m.group(0), sentence_around(text, m.start(), m.end())))
    return hits


def report(hits):
    """Group by action, then by check, so the fix and the rule print once."""
    for action in ("FIX", "REWRITE", "TEST"):
        group = [h for h in hits if h.check.action == action]
        if not group:
            continue
        print(f"\n{action}")
        for name in dict.fromkeys(h.check.name for h in group):
            rows = [h for h in group if h.check.name == name]
            check = rows[0].check
            print(f"  {name}: {check.note}")
            print(f"  see {check.rule}")
            for h in rows:
                print(f'    {h.path}:{h.line}: "{h.match}"')
                print(f"      {h.context}")
            print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--only", help="comma-separated check names, the only way to run "
                                   f"the opt-in checks ({', '.join(sorted(OPT_IN))})")
    ap.add_argument("--summary", action="store_true", help="counts per check, no hit lines")
    args = ap.parse_args()

    all_checks = PROSE_CHECKS + PROSE_ONLY_CHECKS + COMMENT_CHECKS
    wanted = None
    if args.only:
        wanted = {n.strip() for n in args.only.split(",")}
        unknown = wanted - {c.name for c in all_checks}
        if unknown:
            print(f"no such check: {', '.join(sorted(unknown))}. available: "
                  + ", ".join(c.name for c in all_checks), file=sys.stderr)
            return 2

    hits, totals = [], Counter()
    for path in args.paths:
        if not path.is_file():
            print(f"skip {path} (not a file)", file=sys.stderr)
            continue
        found = scan(path, checks_for(path, wanted))
        hits.extend(found)
        totals.update(h.check.name for h in found)

    if hits and not args.summary:
        report(hits)

    if totals:
        by_action = {c.name: c.action for c in all_checks}
        sys.stdout.flush()
        print("\n".join(f"{c:>5}  {by_action[name]:<7}  {name}"
                        for name, c in totals.most_common()), file=sys.stderr)
    return 1 if totals else 0


if __name__ == "__main__":
    sys.exit(main())
