#!/usr/bin/env python3
"""Mechanical scan for the text-review and code-comments skills.

The file extension picks what to read. A source file is reduced to its comment
lines first, because every code-comments stem is also ordinary code vocabulary
and a file-wide search buries the hits in identifiers and literals. Anything
else is read as prose. WHOLE_FILE names the exception, a check that reads every
line of a source file so it can reach an error string.

Rules do not split the same way. The voice checks run on everything, and each
side holds back the checks that only mean something there: COMMENT_CHECKS stay
out of prose, where "Step 1" is a heading and no kind of plan label, and
PROSE_ONLY_CHECKS stay out of comments, for the two reasons given where that
list is defined.

Hits are candidates to judge. Each check declares the action it needs, and
the report groups by that action so a find-and-replace does not sit in the same
list as a call that needs judgment:

    FIX      the replacement is determined
    REWRITE  always a violation, but the wording has to change
    TEST     apply the test named on the hit, then decide

Exit status: 0 clean, 1 hits found, 2 usage error.

    scripts/scan.py draft.md
    scripts/scan.py draft.md src/chunker.py src/loader.go
    scripts/scan.py --only citation,british paper.md
    scripts/scan.py --skip-html-comments paper.md
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
POINT_AT_NOUN = "christian-writing-style, Point at a noun"

SENTENCE_LIMIT = 40

SENTENCE_SPLIT = re.compile(r"[.!?]+[\"')\]]*\s+")

# Periods that do not end a sentence. A decimal needs no entry here, since the
# digit after the point is not whitespace and never starts a candidate split.
ABBREVIATIONS = {"al", "approx", "cf", "ch", "dr", "e.g", "eq", "fig", "figs",
                 "i.e", "inc", "mr", "ms", "no", "p", "pp", "prof", "ref",
                 "refs", "sec", "st", "tab", "vs"}

# The period, percent, and colon keep "0.405", "62%", and "[@sec:coverage]" to
# one word each. Splitting them inflates the count on the results paragraphs,
# which are the ones a reader can least judge by eye.
WORD = re.compile(r"[A-Za-z0-9][\w'.%:-]*")

# Units that hold no sentence. A table row and a shell command inside an HTML
# comment both pass the word limit without being prose. The length check reads
# this. A quantity written out in a table cell is still vague, so the quantity
# check does not.
NOT_PROSE = re.compile(r"^\s*(?:\||```|~~~|\$\$?|#{1,6}\s|!\[|<!--)")

UNQUANTIFIED = re.compile(r"(?i)\ba (?:few|handful|small fraction|little)\b")

DIGIT = re.compile(r"\d")


class Span:
    """One hit from a check that counts instead of matching a pattern.

    Holds the same three attributes as a regex match, so the reporting path
    reads both the same way.
    """

    def __init__(self, label, start, end):
        self.label, self.begin, self.finish = label, start, end

    def group(self, index=0):
        if index:
            raise IndexError("no such group")
        return self.label

    def start(self):
        return self.begin

    def end(self):
        return self.finish


def sentences(text):
    """Yield (start, end, sentence) over one prose unit.

    A boundary needs a capital, a digit, or an opening bracket after the period.
    A lowercase word after one keeps the sentence whole, which covers the
    abbreviations the list above misses.
    """
    left = 0
    for m in SENTENCE_SPLIT.finditer(text):
        head = text[left:m.start()]
        last = re.split(r"[\s(\[]", head)[-1].lower().rstrip(".") if head else ""
        if last in ABBREVIATIONS or (len(last) == 1 and last.isalpha()):
            continue
        after = text[m.end():m.end() + 1]
        if after and not (after.isupper() or after.isdigit() or after in "[\"'($*`-"):
            continue
        yield left, m.start(), text[left:m.start()]
        left = m.end()
    if left < len(text):
        yield left, len(text), text[left:]


def long_sentences(text):
    """Find sentences past SENTENCE_LIMIT words, skipping units that hold none.

    The match states the count and the opening words. The count alone would
    collide in the dedup key when one unit holds two long sentences.
    """
    if NOT_PROSE.match(text):
        return
    for start, end, sentence in sentences(text):
        count = len(WORD.findall(sentence))
        if count > SENTENCE_LIMIT:
            yield Span(f"{count} words: {' '.join(sentence.split()[:6])}", start, end)


def unquantified(text):
    """Find a vague quantity in a sentence that states no number.

    The rule is "vague where a number exists" and no script can tell whether one
    exists. A digit in the same sentence is the closest available stand-in, and
    it is what keeps "a few hundredths, from 0.020 to 0.030" quiet.
    """
    for start, _, sentence in sentences(text):
        if DIGIT.search(sentence):
            continue
        for m in UNQUANTIFIED.finditer(sentence):
            yield Span(m.group(0), start + m.start(), start + m.end())


# A quoted line is a record of what was sent or said. The voice rules govern
# what he writes, so editing quoted material would misreport the source.
QUOTED = re.compile(r"^\s*>")

CONTRAST = re.compile(r",\s+not\s+|\s+rather\s+than\s+")


def label(match, text, after, words=3):
    """Tag a hit with what follows it, so two in one unit survive the dedup key.

    The key is (check, line, match), so a constant label collapses every
    repeat inside one paragraph and undercounts the summary.
    """
    tail = " ".join(text[after:].split()[:words])
    joiner = "" if tail[:1] in ",.;:)" else " "
    return f"{match}{joiner}{tail}".strip()


def contrastive_voice(text):
    """Find "X rather than Y" and "X, not Y" outside quoted material.

    Headings and table cells fire. Two section titles in one dissertation
    used the construction, so skipping them would have missed both.
    """
    if QUOTED.match(text):
        return
    for m in CONTRAST.finditer(text):
        yield Span(label(m.group(0).strip(), text, m.end()), m.start(), m.end())


# Markup that needs a semicolon of its own: an inline code span, a Pandoc
# multi-citation, an HTML entity, and a LaTeX escape. The rule is about two
# clauses, and 39 of the 39 hits on one manuscript were markup.
MARKUP = re.compile(r"`[^`]*`|\[@[^\]]*\]|&#?\w+;|\\.")


def semicolon(text):
    """Find a semicolon outside the markup that holds one.

    Masking keeps the offsets, so the reported sentence is the real one. A
    fenced block never reaches here, since scan() holds a counting check back
    from one, which is what takes a shell command out of the results.
    """
    masked = MARKUP.sub(lambda m: " " * len(m.group(0)), text)
    for m in re.finditer(";", masked):
        yield Span(label(";", text, m.end()), m.start(), m.end())


# "That" and "this" are left out on their own, where the stems below reach them
# only in "that same" and "this same". "That" opens every relative clause ("the
# row that is empty"). A sentence opening on "This is" points at the situation
# the paragraph just described, which is the sense that stays.
POINTER_TAIL = (r"[.,;:)]|\s+(?:is|are|was|were|has|have|had|and|or|but|so|that|which|"
                r"of|in|to|from|with|for|than|against|into|on|at|by)\b")

POINTER = re.compile(rf"(?i)(?<![\w-])(?:(?:those|these)(?={POINTER_TAIL})"
                     rf"|(?:that|this) same\b"
                     rf"|the (?:former|latter)\b)")


def pointer(text):
    """Find a pointer word whose noun the reader has to supply.

    Quoted material is skipped for the reason contrastive_voice gives. Table
    cells are read: one row said "combine those into daily summaries" through
    every review the table had.
    """
    if QUOTED.match(text):
        return
    for m in POINTER.finditer(text):
        yield Span(label(m.group(0), text, m.end()), m.start(), m.end())


# A clause after the conjunction needs a subject of its own. Bare nouns stay
# out: in "notes, laboratory results, and medication orders" the list item
# "orders" reads as a verb and every serial list would fire. The capitalized
# alternative is the reason this pattern is not compiled with IGNORECASE, which
# would let it match any word at all.
SUBJECT = (r"(?i:it|they|we|this|that|there|these|those|he|she|one|its|their|our|his|her|"
           r"the|an?|no|every|each|both|most|some|all|another|either|neither|two|three|"
           r"four|five)\b|\[@[^\]]+\]|`[^`]+`|[A-Z][\w-]*")

# -ss, -ous, -ness and -less end nouns and adjectives, which is what the
# lookbehind excludes. The -s and -ed endings reach most finite verbs. The
# irregular pasts are listed because "the loss held" and "the ceiling rose" are
# ordinary in his results prose and match neither ending. Several of them
# double as nouns, at a cost of three false positives across 477 files.
FINITE = (r"(?i:is|are|was|were|has|have|had|does|do|did|will|would|can|could|may|might|"
          r"must|should|shall|holds?|reads?|gives?|makes?|takes?|needs?|stays?|runs?|"
          r"held|grew|fell|rose|wrote|took|gave|went|came|kept|meant|sent|told|saw|"
          r"found|brought|drew|built|made)\b"
          r"|(?i:\w*(?<![su])s)\b|(?i:\w+ed)\b")

COMMA_JOIN = re.compile(rf",\s+and\s+(?:{SUBJECT})"
                        rf"(?:\s+[\w'@:.%\[\]`$-]+){{0,3}}\s+(?:{FINITE})")


def comma_join(text):
    """Find two independent clauses joined by a comma and "and".

    A subject followed by a finite verb separates a second clause from a
    compound predicate ("reads the artifact, and writes the scores") or a
    trailing participle ("every interval spanning zero"). Neither survives a
    period. A heading and a table row are skipped for the same reason.
    """
    if QUOTED.match(text) or NOT_PROSE.match(text):
        return
    for start, _, sentence in sentences(text):
        for m in COMMA_JOIN.finditer(sentence):
            # A serial list ends "..., and the process that produced them are
            # in Appendix", which is a subject and a verb by every test this
            # check can apply. An earlier comma in the same sentence is the one
            # signal that separates the two, at the cost of the genuine joins
            # that share a sentence with a list.
            if ", " in sentence[:m.start()]:
                continue
            end = m.start() + m.group(0).index("and") + 3
            yield Span(label(", and", sentence, end), start + m.start(), start + end)


PROSE_CHECKS = [
    Check("em-dash", r"—", "FIX",
          "use a period or parentheses", AVOID),
    Check("semicolon", semicolon, "FIX",
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
    # to 0.8"), which is why this check asks for a test.
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
    Check("pointer", pointer, "TEST",
          "name the noun it points at. If the nearest noun before it is "
          "something else, or no noun was written at all, write the noun. A "
          "demonstrative standing for the situation just described stays",
          POINT_AT_NOUN),
    # "held" is left out. His sweep of one manuscript rewrote 44 instances of
    # the word and changed no "held", where the participle reads as the steady
    # sense. The particles after the verb mark that sense too.
    Check("possession-verb", r"(?i)\b(?:hold|holds|holding)\b"
                        r"(?!\s+(?:to|together|up|back|at|where|wherever|"
                        r"whenever|on|off|out|for|in|true|steady)\b)", "TEST",
          "possession, or staying steady? \"the cohort holds 116\" is \"has\". "
          "\"the rule holds where the contrast is informative\" stays", CONCRETE),
    # "load-bearing" is the one figurative sense with its own entry in
    # concrete-thing. Reaching it here too would print that sentence under two
    # groups, so the reader answers one call twice.
    Check("relation-verb", r"(?i)(?<!load-)(?<!load )\b(?:bears?|bearing|borne)\b",
          "REWRITE",
          "name the relation: \"the evaluation bears on leakage\" is \"could have "
          "caught leakage\". \"Bears out\" is \"confirms\", and \"bear in mind\" "
          "is filler", CONCRETE),
    Check("vague-quantifier", r"(?i)\b(?:elevated|tighten)\b|various factors|had issues",
          "REWRITE",
          "give the number, or name what went wrong", CONCRETE),
    # Separate from vague-quantifier because these words are right often enough
    # that a REWRITE, which prints false positives and all, would be wrong.
    Check("unquantified", unquantified, "TEST",
          "give the fraction, or say why it is not available. A label rather "
          "than a measurement is fine", CONCRETE),
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
    # The judgment half of the old contrastive-tail check lives on in
    # side-commentary above, whose stems reach the tails this pattern misses
    # ("not just", "the other way around").
    Check("contrastive-voice", contrastive_voice, "REWRITE",
          "restate as a positive claim about what is true, or cut the clause "
          "and let the next sentence show it",
          "christian-writing-style, No this-not-that"),
    Check("comma-join", comma_join, "REWRITE",
          "two clauses, so use a period. It reads \", and\" alone. \", but\", \", so\" "
          "and \", for\" mark a relationship a period would drop, so they stay",
          "christian-writing-style, What to avoid"),
]

OPT_IN = {"citation"}

# Held back from source files, for two different reasons. specialist-term
# because the same words are covered by the absolute form of the rule in
# COMMENT_CHECKS. long-sentence because comment_lines yields one physical line
# at a time, so a wrapped sentence never reaches the limit in a single unit.
PROSE_ONLY_CHECKS = [
    Check("specialist-term", r"(?i)\b(?:guard|invariant|idempotent|canonical)\b", "TEST",
          "standard for this audience, or does a plain word of the same length "
          "exist? \"canonical order\" is \"fixed order\". A term in an example "
          "that only shows sentence shape is fine",
          "christian-writing-style, Fight the curse of knowledge"),
    Check("long-sentence", long_sentences, "TEST",
          "lists and enumerations are legitimately long. Split only when the "
          "sentence chains modifiers or hides its subject",
          "christian-writing-style, One sentence, one job"),
]

COMMENT_CHECKS = [
    Check("jargon", r"(?i)\b(?:guard|invariant|idempotent|canonical|load[- ]bearing|downstream)\b",
          "REWRITE",
          "name the thing in this code: \"the check above\", \"the file the "
          "script reads\"", "code-comments rule 1"),
    # "no longer" and "the old" describe runtime state as often as dead code
    # ("the target no longer exists"), so this one asks.
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

# A new prose unit starts at any marker below, and does not continue the unit above.
UNIT_START = re.compile(r"^\s*(?:#{1,6}\s|[-*+]\s|\d+\.\s|>\s|\||```|~~~)")

SENTENCE_END = re.compile(r"(?<=[.!?])\s")

# Checks that read every line of a source file, past the comments,
# so they reach an error string or a log message. Only em-dash qualifies:
# nothing in code needs one, so the sole false positive is a linter declaring
# the character, while British spelling would match every word inside this
# script's own pattern list.
WHOLE_FILE = {"em-dash"}


def strip_html_comments(lines):
    """Blank the `<!-- -->` spans and keep the rest of each line.

    Keeping the rest of the line lets a note sit tight against its paragraph
    without taking the paragraph with it.
    A fence is tracked, because "<!--" inside a code block opens nothing.
    """
    inside, in_fence, out = False, False, []
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        kept, rest = [], line
        while rest:
            if inside:
                end = rest.find("-->")
                if end < 0:
                    rest = ""
                    break
                rest, inside = rest[end + 3:], False
                continue
            start = rest.find("<!--")
            if start < 0:
                kept.append(rest)
                break
            kept.append(rest[:start])
            rest, inside = rest[start + 4:], True
        out.append("".join(kept))
    return out


def prose_units(path, drop_comments=False):
    """Yield (lineno, text, fenced) with hard-wrapped lines joined into one unit.

    Phrase patterns like "the rest of this section" straddle a newline in wrapped
    markdown and match nothing when each physical line is tested on its own. The
    line number reported is where the unit starts. fenced says the unit came
    from a code block, which the checks that measure a sentence cannot read.
    """
    lines = path.read_text(errors="replace").splitlines()
    if drop_comments:
        lines = strip_html_comments(lines)
    unit, start, in_fence = [], None, False
    for n, line in enumerate(lines, 1):
        fence = line.lstrip().startswith(("```", "~~~"))
        if not line.strip() or (UNIT_START.match(line) and not in_fence) or fence:
            if unit:
                yield start, " ".join(unit), False
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
                yield start, " ".join(unit), True
                unit, start = [], None
    if unit:
        yield start, " ".join(unit), False


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


def matches(pattern, text):
    """Run one check over one unit. A check that counts is a function."""
    if isinstance(pattern, str):
        return re.finditer(pattern, text)
    return pattern(text)


def checks_for(path, wanted=None):
    """Return every voice check, plus the ones that only mean something here."""
    checks = PROSE_CHECKS + (COMMENT_CHECKS if is_source(path) else PROSE_ONLY_CHECKS)
    if wanted:
        return [c for c in checks if c.name in wanted]
    return [c for c in checks if c.name not in OPT_IN]


def unfenced(source):
    """Add the third element prose_units yields. A comment pass reads no fences."""
    for n, text in source:
        yield n, text, False


def scan(path, checks, skip_html_comments=False):
    if is_source(path):
        passes = [(unfenced(comment_lines(path)), checks),
                  (unfenced(all_lines(path)),
                   [c for c in checks if c.name in WHOLE_FILE])]
    else:
        passes = [(prose_units(path, skip_html_comments), checks)]
    seen, hits = set(), []
    for source, active in passes:
        if not active:
            continue
        for n, text, fenced in source:
            for check in active:
                # The pattern checks still read a code block, where a semicolon
                # in a shell command is a judgment call. The counting checks
                # cannot, because a code line is not a sentence.
                if fenced and not isinstance(check.pattern, str):
                    continue
                for m in matches(check.pattern, text):
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
    ap.add_argument("--skip-html-comments", action="store_true",
                    help="markdown only: read the published prose and skip <!-- --> notes")
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
        found = scan(path, checks_for(path, wanted), args.skip_html_comments)
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
