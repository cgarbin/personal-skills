#!/usr/bin/env python3
"""Check a commit message, then stage the listed files and commit them.

The message checks: subject under 72 characters, no Conventional Commit
prefix, a blank line before the body, body lines wrapped at 72, and a
Co-Authored-By trailer in the last paragraph, where git will read it. --check
reports on a draft without committing. Committing runs the same checks and
stops on an error, so a message that skipped --check is still checked.

Staging takes the paths given as arguments and nothing else, so one group's
commit cannot pick up another group's file.

A format hook such as ruff-format can rewrite a file and then abort the
commit. Nothing is committed, and the file on disk no longer matches what was
staged. Staging it again and re-running the same commit is the whole fix. It
is the same steps on the same files every time, with nothing to decide, so the
script does it once itself instead of reporting the failure.

A hook that aborted without rewriting anything hit something a second run will
not fix, a lint error for example. The script reports that and stops.

Exit status: 0 committed or checked clean, 1 nothing committed, 2 usage error.

    scripts/commit_group.py --check MESSAGE_FILE
    scripts/commit_group.py MESSAGE_FILE src/loader.py README.md
"""

import argparse
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

# level decides whether the commit proceeds. rule names the check in a form
# that survives rewording the text.
Problem = namedtuple("Problem", "level rule text")

SUBJECT_AIM = 50
SUBJECT_LIMIT = 72
BODY_LIMIT = 72

# The type list from the Conventional Commits spec, not every word before a
# colon. "Note: ..." is a sentence and stays. "docs: ..." is the convention
# the skill rejects.
CONVENTIONAL = re.compile(
    r"^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)"
    r"(\([^)]*\))?!?:\s", re.IGNORECASE)

ADDRESS = re.compile(r"<[^@<>\s]+@[^@<>\s]+>")

# Pathspecs that would stage more than the group. argparse rejects an unknown
# option on its own, so no flag reaches this.
WIDENING = {".", "..", "./", ":/", "*"}


def trailers(text):
    """Return the trailers git will register, not every line that looks like one.

    git reads them from the last paragraph only, so a trailer with no blank
    line above it is body text.
    """
    done = subprocess.run(["git", "interpret-trailers", "--parse"],
                          input=text, capture_output=True, text=True)
    if done.returncode != 0:
        return []
    return [line.split(":", 1) for line in done.stdout.splitlines()
            if ":" in line]


def last_paragraph(lines, first):
    """Return the numbers of the lines in the final paragraph, counting from first."""
    end = len(lines)
    while end > 0 and not lines[end - 1].strip():
        end -= 1
    start = end
    while start > 0 and lines[start - 1].strip():
        start -= 1
    return set(range(start + first, end + first))


def wrappable(line):
    """Whether wrapping this line could get it under the limit.

    A URL is one token with no break point, so reporting it would name no fix.
    """
    return all(len(word) <= BODY_LIMIT for word in line.split())


def check_message(text):
    lines = text.rstrip("\n").split("\n")
    subject = lines[0].strip()
    if not subject:
        return [Problem("error", "subject-empty", "the message has no subject line")]

    problems = []
    if len(subject) > SUBJECT_LIMIT:
        problems.append(Problem(
            "error", "subject-length",
            f"subject is {len(subject)} chars, over the {SUBJECT_LIMIT} limit"))
    elif len(subject) > SUBJECT_AIM:
        problems.append(Problem(
            "warning", "subject-length",
            f"subject is {len(subject)} chars, over the {SUBJECT_AIM} aim"))

    if CONVENTIONAL.match(subject):
        problems.append(Problem(
            "error", "subject-prefix",
            f"drop the Conventional Commit prefix: {subject.split(':')[0]}:"))

    rest = lines[1:]
    if rest and rest[0].strip():
        problems.append(Problem(
            "error", "body-blank-line",
            "put a blank line between the subject and the body"))

    parsed = trailers(text)
    # The trailer block is not prose, and a session link passes the limit on
    # its own, so the wrap rule stops where the trailers start.
    exempt = last_paragraph(rest, 2) if parsed else set()
    for number, line in enumerate(rest, start=2):
        if number not in exempt and len(line) > BODY_LIMIT and wrappable(line):
            problems.append(Problem(
                "error", "body-wrap",
                f"line {number} is {len(line)} chars, wrap the body at {BODY_LIMIT}"))

    authors = [value for key, value in parsed
               if key.strip().lower() == "co-authored-by"]
    if not authors:
        problems.append(Problem(
            "error", "trailer-missing",
            "no Co-Authored-By trailer git will read, so add one in its own "
            "paragraph at the end"))
    elif not any(ADDRESS.search(value) for value in authors):
        problems.append(Problem(
            "error", "trailer-malformed",
            "the Co-Authored-By trailer needs a Name <address> value"))

    return problems


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def listed_paths(done):
    """Split a -z listing into paths, holding a name with a space in one piece.

    The plain listing separates on newlines and quotes anything unusual, so a
    name with a space or an accent comes back in a form that matches nothing.
    """
    return [path for path in done.stdout.split("\0") if path]


def relay(done):
    for stream, out in ((done.stdout, sys.stdout), (done.stderr, sys.stderr)):
        if stream.strip():
            print(stream.rstrip(), file=out)


def resolve(given, root):
    """Return repo-relative forms of the arguments, so they compare with git's output."""
    resolved = []
    for path in given:
        try:
            resolved.append(str(Path(path).resolve().relative_to(root)))
        except ValueError:
            raise ValueError(f"{path} is outside {root}") from None
    return resolved


def tracked(root, path):
    return git(root, "ls-files", "--error-unmatch", "--", path).returncode == 0


def commit(root, message, files):
    """Stage the named files and commit, retrying once past a rewriting hook."""
    staged = listed_paths(git(root, "diff", "--cached", "--name-only", "-z"))
    extra = [path for path in staged if path not in files]
    if extra:
        print("error: the index already holds paths this group does not name: "
              + ", ".join(extra), file=sys.stderr)
        print("unstage them or add them to the group before committing.",
              file=sys.stderr)
        return 1

    add = git(root, "add", "--", *files)
    if add.returncode != 0:
        relay(add)
        return 1

    first = git(root, "commit", "-F", str(message))
    if first.returncode == 0:
        relay(first)
        return 0

    rewritten = listed_paths(git(root, "diff", "--name-only", "-z", "--", *files))
    if not rewritten:
        relay(first)
        print("error: the commit failed and no file in the group changed, so a "
              "retry would fail the same way.", file=sys.stderr)
        return 1

    print("a hook rewrote " + ", ".join(rewritten) + ", re-staging and retrying")
    git(root, "add", "--", *files)
    second = git(root, "commit", "-F", str(message))
    relay(second)
    if second.returncode != 0:
        print("error: the commit failed again after the retry.", file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check a commit message, then commit one group of files.")
    parser.add_argument("--check", action="store_true",
                        help="report on the message and commit nothing")
    parser.add_argument("message", help="file holding the commit message")
    parser.add_argument("files", nargs="*", help="paths to stage, named one by one")
    args = parser.parse_args(argv)

    if args.check and args.files:
        parser.error("--check takes no files")
    if not args.check and not args.files:
        parser.error("name the files to stage, or pass --check")

    widening = [path for path in args.files if path in WIDENING]
    if widening:
        parser.error("name each file, not " + ", ".join(widening))

    message = Path(args.message).resolve()
    try:
        text = message.read_text()
    except OSError as failure:
        parser.error(f"cannot read {args.message}: {failure.strerror}")

    problems = check_message(text)
    for problem in problems:
        print(f"{problem.level}: {problem.rule}: {problem.text}")
    if any(problem.level == "error" for problem in problems):
        print("nothing committed.")
        return 1
    if args.check:
        return 0

    top = git(Path.cwd(), "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        relay(top)
        return 2
    root = Path(top.stdout.strip()).resolve()

    try:
        files = resolve(args.files, root)
    except ValueError as outside:
        print(f"error: {outside}", file=sys.stderr)
        return 1

    missing = [path for path in files
               if not (root / path).exists() and not tracked(root, path)]
    if missing:
        print("error: not on disk and not tracked: " + ", ".join(missing),
              file=sys.stderr)
        return 1

    return commit(root, message, files)


if __name__ == "__main__":
    sys.exit(main())
