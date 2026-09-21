#!/usr/bin/env python3
"""Fixtures for the rules the skill can only state as prose.

Two halves. The message checks run in process, because they are pure text
rules. The commit checks drive a real repository through a real hook, because
the behavior under test is what git does when a hook rewrites a staged file,
and a mock of git would only assert that the mock was written to match the
implementation.

    scripts/test_commit_group.py
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import commit_group

SCRIPT = Path(__file__).resolve().parent / "commit_group.py"
TRAILER = "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"

# scan.py ships with the text-review skill, which can be installed without
# this one, so the file may not be there.
needs_scanner = unittest.skipUnless(
    commit_group.SCAN.is_file(), f"no prose scanner at {commit_group.SCAN}")

# A stand-in for scan.py, so the tests below can drive a known hit. The
# real check table keeps growing. Tests written against it break whenever
# text-review adds a check.
STUB_SCANNER = '''
from collections import namedtuple

Check = namedtuple("Check", "name pattern action note rule")
Hit = namedtuple("Hit", "check path line match context")

CHECKS = [Check("blocks", None, "FIX", "the blocking note.", None),
          Check("warns", None, "REWRITE", "the warning note.", None)]


def checks_for(path, wanted=None):
    return CHECKS


def scan(path, checks, skip_html_comments=False):
    text = path.read_text()
    return [Hit(check, path, 1, f"<{check.name}>", text)
            for check in checks if check.name in text]
'''


def message(subject, body=None, trailer=TRAILER):
    parts = [subject]
    if body:
        parts.append(body)
    if trailer:
        parts.append(trailer)
    return "\n\n".join(parts) + "\n"


# 35 words, the ceiling itself.
AT_CEILING = ("The tokenizer rejects a batch over 8192 tokens, so the loader splits\n"
              "at 8000 and leaves a margin for the prompt prefix that the caller\n"
              "prepends before every request it sends to the language model.")
PAST_CEILING = AT_CEILING.replace("every request", "every single request")


class Checked(unittest.TestCase):
    def errors(self, text):
        return [p for p in commit_group.check_message(text) if p.level == "error"]

    def rules(self, text):
        return sorted(p.rule for p in self.errors(text))


class Subject(Checked):
    def test_the_hard_limit_itself_passes(self):
        self.assertEqual(self.errors(message("s" * 72)), [])

    def test_one_character_over_the_hard_limit_fails(self):
        self.assertEqual(self.rules(message("s" * 73)), ["subject-length"])

    def test_the_aim_is_a_warning_and_not_an_error(self):
        # 50 is the target, 72 is the limit. Between them the message commits.
        problems = commit_group.check_message(message("s" * 60))
        self.assertEqual([p.level for p in problems], ["warning"])

    def test_an_empty_message_fails(self):
        self.assertEqual(self.rules(""), ["subject-empty"])

    def test_a_conventional_commit_prefix_fails(self):
        for subject in ("feat: add retry", "fix(api): handle nulls",
                        "chore!: drop the flag", "docs: update the readme",
                        "Refactor: split the module"):
            with self.subTest(subject=subject):
                self.assertIn("subject-prefix", self.rules(message(subject)))

    def test_a_colon_that_names_no_type_passes(self):
        # Only the conventional type list is banned.
        for subject in ("Note: the retry path stays",
                        "Commit skill: fold in the message checks"):
            with self.subTest(subject=subject):
                self.assertEqual(self.errors(message(subject)), [])


class Body(Checked):
    def test_a_body_needs_a_blank_line_after_the_subject(self):
        text = f"Subject line\nBody text\n\n{TRAILER}\n"
        self.assertEqual(self.rules(text), ["body-blank-line"])

    def test_the_wrap_limit_itself_passes(self):
        line = " ".join(["alpha"] * 12)
        self.assertEqual(len(line), 71)
        self.assertEqual(self.errors(message("Subject", line)), [])

    def test_a_body_line_over_the_wrap_limit_fails(self):
        line = " ".join(["alpha"] * 13)
        self.assertGreater(len(line), 72)
        self.assertEqual(self.rules(message("Subject", line)), ["body-wrap"])

    def test_a_token_too_long_to_wrap_passes(self):
        # A URL has no break point, so reporting it would name no fix.
        url = "https://claude.ai/code/" + "x" * 80
        self.assertEqual(self.errors(message("Subject", url)), [])

    def test_a_long_body_line_that_opens_like_a_trailer_fails(self):
        # The exemption belongs to the trailer block alone.
        line = "Result: " + " ".join(["alpha"] * 16)
        self.assertGreater(len(line), 72)
        self.assertEqual(self.rules(message("Subject", line)), ["body-wrap"])


def body_of(text):
    """Split a message the way check_message does, then return its body."""
    rest = text.rstrip("\n").split("\n")[1:]
    return commit_group.body_text(rest, commit_group.trailers(text))


class BodyProse(Checked):
    """The body checks this script runs itself, with the scanner's hits dropped.

    text-review keeps adding checks, so a test body written for the inventory
    rules would eventually trip one of them.
    """

    def owned(self, body):
        """The problems this script raises itself, in the order it reports them.

        Everything the scanner produced is dropped, so these tests keep
        passing when text-review adds a check.
        """
        return [p for p in commit_group.check_message(message("Subject line", body))
                if not p.rule.startswith("prose")]

    def warned(self, body):
        problems = self.owned(body)
        self.assertEqual([p for p in problems if p.level == "error"], [])
        return sorted({p.rule for p in problems if p.level == "warning"})

    def test_an_inventory_phrase_split_by_the_wrap_is_found(self):
        # A body is wrapped at 72, so a phrase across a line break is the
        # normal case.
        self.assertIn("body-inventory", self.warned(
            "The paragraph and the diagram moved, all from this review\n"
            "round."))

    def test_a_reported_phrase_stays_on_one_line(self):
        # The skill has the reader sort the output by its level prefix. A
        # phrase with the line break still in it puts half a problem on a
        # line of its own.
        problems = self.owned(
            "The caption cited the July run through the draft. Three\n"
            "edits put the August numbers back.")
        self.assertEqual([p.rule for p in problems], ["body-inventory"])
        self.assertIn('"Three edits"', problems[0].text)

    def test_every_inventory_phrase_is_reported(self):
        problems = self.owned(
            "The paragraph and the diagram moved in one commit, all from\n"
            "this review round.")
        self.assertEqual([p.rule for p in problems],
                         ["body-inventory", "body-inventory"])

    def test_a_body_that_counts_the_changes_warns(self):
        self.assertIn("body-inventory", self.warned("Three edits to the loader."))

    def test_a_count_opening_a_later_sentence_warns(self):
        self.assertIn("body-inventory", self.warned(
            "The tokenizer rejects a batch over 8192 tokens. Three fixes\n"
            "got the batch size under it."))

    def test_a_count_that_only_opens_a_wrapped_line_is_clean(self):
        # 72-char wrapping puts a count at the start of a line. This one sits
        # mid-sentence, where it describes the tokenizer.
        self.assertEqual(self.warned(
            "The tokenizer rejects a batch over 8192 tokens, which took\n"
            "three fixes to get under."), [])

    def test_a_body_naming_the_round_the_work_came_from_warns(self):
        self.assertIn("body-inventory",
                      self.warned("The wrap limit moved, from this review round."))

    def test_a_body_naming_the_commit_itself_warns(self):
        self.assertIn("body-inventory",
                      self.warned("The loader and the index moved in one commit."))

    def test_a_body_stating_a_fact_the_diff_does_not_show_is_clean(self):
        self.assertEqual(self.warned(
            "git wraps a subject over 72 chars in git log --oneline."), [])

    def test_a_body_at_the_ceiling_is_clean(self):
        self.assertEqual(self.warned(AT_CEILING), [])

    def test_a_body_one_word_past_the_ceiling_warns(self):
        self.assertIn("body-length", self.warned(PAST_CEILING))

    def test_the_length_warning_gives_the_count_and_the_ceiling(self):
        # A reader one word over and a reader forty over need different
        # things, and "too long" serves neither.
        problems = commit_group.check_message(message("Subject", PAST_CEILING))
        text = " ".join(p.text for p in problems if p.rule == "body-length")
        self.assertIn("36 words", text)
        self.assertIn("past 35", text)

    def test_a_bulleted_body_is_counted(self):
        # A bulleted inventory reads as organized and pads like anything
        # else, so its length is what reports it.
        self.assertIn("body-length", self.warned(
            "- the loader splits every batch at 8000 tokens before the call\n"
            "- the tokenizer rejects anything over 8192 in a single request\n"
            "- the margin covers the prompt prefix the caller prepends\n"
            "- the retry reports a stale index entry and not a missing file"))

    def test_a_list_marker_is_not_a_word(self):
        self.assertEqual(commit_group.word_count("- one\n- two\n* three"), 3)

    def test_a_missing_prose_scanner_warns_and_the_rest_still_runs(self):
        self.addCleanup(setattr, commit_group, "SCAN", commit_group.SCAN)
        commit_group.SCAN = Path("/nonexistent/scan.py")
        problems = commit_group.check_message(message("Subject", PAST_CEILING))
        self.assertEqual({p.level for p in problems}, {"warning"})
        self.assertEqual(sorted({p.rule for p in problems}),
                         ["body-length", "prose-scan"])

    def test_the_trailers_are_not_part_of_the_body(self):
        # They are the harness's text, so a warning on them names nothing the
        # author can fix.
        self.assertEqual(body_of(message("Subject line", "Body text")), "Body text")

    def test_a_message_with_no_body_has_an_empty_body(self):
        self.assertEqual(body_of(message("Subject line")), "")

    def test_an_empty_body_never_reaches_the_scanner(self):
        self.addCleanup(setattr, commit_group, "SCAN", commit_group.SCAN)
        commit_group.SCAN = Path("/nonexistent/scan.py")
        self.assertEqual(commit_group.check_message(message("Subject line")), [])

    def test_a_scanner_that_will_not_load_is_not_reported_as_missing(self):
        # The file is at the path the message names, so "no prose scanner
        # there" sends the reader looking for a file that is sitting there.
        # One path serves both loads, so the wording is what tells them apart.
        self.addCleanup(setattr, commit_group, "SCAN", commit_group.SCAN)
        with tempfile.TemporaryDirectory() as folder:
            commit_group.SCAN = Path(folder) / "scan.py"
            commit_group.SCAN.write_text("import a_module_that_is_not_installed\n")
            module, broke = commit_group.load_scan()
            commit_group.SCAN.unlink()
            absent_module, absent = commit_group.load_scan()
        self.assertIsNone(module)
        self.assertIsNone(absent_module)
        self.assertIn("did not load", broke)
        self.assertNotEqual(broke, absent)


    def test_a_scanner_that_breaks_its_interface_warns(self):
        # scan.py belongs to another skill, so it can rename the function
        # this one calls. Without the try around that call the script exits
        # on a traceback.
        self.addCleanup(setattr, commit_group, "SCAN", commit_group.SCAN)
        with tempfile.TemporaryDirectory() as folder:
            commit_group.SCAN = Path(folder) / "scan.py"
            commit_group.SCAN.write_text("def checks_for(path, wanted=None):\n"
                                         "    return []\n")
            problems = commit_group.check_message(message("Subject line", "A body."))
        self.assertEqual([p.level for p in problems], ["warning"])
        self.assertEqual([p.rule for p in problems], ["prose-scan"])


class ScannerTranslation(unittest.TestCase):
    """How a scanner hit becomes an error or a warning.

    The stub has one check of each kind. Which words the real scan.py
    objects to belongs to text-review's own tests.
    """

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.addCleanup(setattr, commit_group, "SCAN", commit_group.SCAN)
        stub = Path(folder.name) / "scan.py"
        stub.write_text(STUB_SCANNER)
        commit_group.SCAN = stub

    def problems(self, body):
        return commit_group.check_message(message("Subject line", body))

    def test_a_blocking_hit_becomes_an_error(self):
        self.assertEqual([(p.level, p.rule) for p in self.problems("this one blocks")],
                         [("error", "prose/blocks")])

    def test_any_other_hit_becomes_a_warning(self):
        self.assertEqual([(p.level, p.rule) for p in self.problems("this one warns")],
                         [("warning", "prose/warns")])

    def test_the_problem_quotes_the_match_and_the_note(self):
        self.assertEqual(self.problems("this one blocks")[0].text,
                         '"<blocks>". the blocking note.')

    def test_a_body_that_trips_nothing_reports_nothing(self):
        self.assertEqual(self.problems("the body is quiet"), [])


class ScannerContract(unittest.TestCase):
    """Whether the installed scan.py still works the way this script expects.

    A renamed function shows up as an AttributeError the first time anyone
    commits. A retired blocking action shows up as nothing at all: every
    body passes and no commit is ever stopped.
    """

    @needs_scanner
    def test_the_installed_scanner_can_still_block_a_body(self):
        # Two violations in one body, so dropping either check leaves this
        # test working. Nothing here names which check fired.
        problems = commit_group.check_message(message(
            "Subject line", "The colour of the output is unchanged; it is quiet."))
        self.assertTrue([p for p in problems if p.level == "error"
                         and p.rule.startswith("prose/")], problems)


class Trailers(Checked):
    def test_the_harness_trailer_passes(self):
        self.assertEqual(self.errors(f"Subject line\n\n{TRAILER}\n"), [])

    def test_a_trailer_longer_than_the_wrap_limit_passes(self):
        # Every word here is short enough to move, so the line is wrappable and
        # only the trailer exemption keeps it from reporting.
        pair = "Co-Authored-By: Someone With A Rather Long Name <a.long.name@example.com>"
        text = f"Subject line\n\n{TRAILER}\n{pair}\n"
        self.assertGreater(len(pair), 72)
        self.assertTrue(commit_group.wrappable(pair))
        self.assertEqual(self.errors(text), [])

    def test_a_missing_co_authored_by_fails(self):
        self.assertEqual(self.rules("Subject line\n"), ["trailer-missing"])

    def test_a_session_trailer_fails(self):
        # git history is the pressure behind this one. Every commit in this repo
        # before c5fd39c has the trailer, so the line reads as correct in
        # review and only the check catches it.
        text = (f"Subject line\n\n{TRAILER}\n"
                "Claude-Session: https://claude.ai/code/session_01C4BXdgYEoEWTb\n")
        self.assertEqual(self.rules(text), ["trailer-session"])

    def test_a_session_link_under_another_key_fails(self):
        text = f"Subject line\n\n{TRAILER}\nRefs: https://claude.ai/code/abc\n"
        self.assertEqual(self.rules(text), ["trailer-session"])

    def test_an_unrelated_trailer_passes(self):
        # Only the session rule is enforced. A DCO repo needs Signed-off-by, and
        # an invented trailer has no camouflage in review the way a session link
        # copied from git log does.
        text = f"Subject line\n\n{TRAILER}\nSigned-off-by: C G <cg@example.com>\n"
        self.assertEqual(self.errors(text), [])

    def test_a_trailer_glued_to_the_body_fails(self):
        # git reads trailers from the last paragraph only, so a trailer with no
        # blank line above it is body text and never registers.
        text = f"Subject line\n\nBody text\n{TRAILER}\n"
        self.assertEqual(self.rules(text), ["trailer-missing"])

    def test_a_co_authored_by_without_an_address_fails(self):
        self.assertEqual(self.rules("Subject line\n\nCo-Authored-By: Claude\n"),
                         ["trailer-malformed"])

    def test_the_author_name_is_not_pinned(self):
        # The harness sets the name and it moves with the model, so the check
        # asks only that a well-formed trailer exists.
        text = "Subject line\n\nCo-Authored-By: Some Future Model <noreply@anthropic.com>\n"
        self.assertEqual(self.errors(text), [])


class Repo(unittest.TestCase):
    """A repository with one commit, one tracked file, and no hook."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write("seed.txt", "seed\n")
        self.git("add", "seed.txt")
        self.git("commit", "-m", "Seed")

    def git(self, *args):
        done = subprocess.run(["git", *args], cwd=self.root,
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def write(self, name, text):
        path = self.root / name
        path.write_text(text)
        return path

    def hook(self, script):
        path = self.root / ".git" / "hooks" / "pre-commit"
        path.write_text(script)
        path.chmod(0o755)

    def attempt(self, *args):
        self.write("MSG", message("Subject line"))
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root,
                              capture_output=True, text=True)

    def commits(self):
        return int(self.git("rev-list", "--count", "HEAD").strip())

    def hook_runs(self):
        log = self.root / "hook-runs.log"
        return len(log.read_text().splitlines()) if log.exists() else 0


class Staging(Repo):
    def test_it_commits_the_named_file(self):
        self.write("a.txt", "a\n")
        done = self.attempt("MSG", "a.txt")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD").split(),
                         ["a.txt"])

    def test_it_leaves_the_files_it_was_not_given(self):
        self.write("a.txt", "a\n")
        self.write("b.txt", "b\n")
        self.attempt("MSG", "a.txt")
        self.assertIn("b.txt", self.git("status", "--porcelain"))

    def test_it_refuses_an_argument_that_stages_more_than_the_group(self):
        # git status prints an untracked directory as "?? src/", which makes
        # a directory an easy thing to pass. git add turns it into every file
        # underneath. A colon argument gets past the on-disk check, because
        # ls-files matches a pattern against any tracked file.
        self.write("a.txt", "a\n")
        (self.root / "src").mkdir()
        self.write("src/b.txt", "b\n")
        for arg in (".", "..", "./", ":/", "*", "src", "src/", ":(glob)*.txt"):
            with self.subTest(arg=arg):
                done = self.attempt("MSG", arg)
                self.assertEqual(done.returncode, 2, done.stdout)
                self.assertEqual(self.commits(), 1)

    def test_it_refuses_a_path_that_is_neither_on_disk_nor_tracked(self):
        done = self.attempt("MSG", "ghost.txt")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.commits(), 1)

    def test_it_stages_a_deletion(self):
        # A removed file is not on disk, so an existence check alone rejects it.
        (self.root / "seed.txt").unlink()
        done = self.attempt("MSG", "seed.txt")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.git("show", "--name-status", "--format=", "HEAD").split(),
                         ["D", "seed.txt"])

    def test_it_commits_a_deletion_that_is_already_staged(self):
        # git rm takes the path out of the index and the working tree has it
        # gone too, so neither an existence check nor ls-files finds it.
        self.git("rm", "-q", "seed.txt")
        done = self.attempt("MSG", "seed.txt")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.git("show", "--name-status", "--format=", "HEAD").split(),
                         ["D", "seed.txt"])

    def test_it_commits_a_staged_deletion_below_the_root(self):
        # ls-tree lists one level unless it is given the path to resolve.
        nested = self.root / "src"
        nested.mkdir()
        self.write("src/loader.py", "x = 1\n")
        self.git("add", "src/loader.py")
        self.git("commit", "-m", "Add the loader")
        self.git("rm", "-q", "src/loader.py")
        done = self.attempt("MSG", "src/loader.py")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.git("show", "--name-status", "--format=", "HEAD").split(),
                         ["D", "src/loader.py"])

    def test_it_stops_when_the_index_holds_a_path_it_was_not_given(self):
        # Committing here would fold another group's file into this commit.
        self.write("a.txt", "a\n")
        self.write("b.txt", "b\n")
        self.git("add", "b.txt")
        done = self.attempt("MSG", "a.txt")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.commits(), 1)

    def test_a_symlink_does_not_drag_in_its_target(self):
        # git stores a symlink itself, so following one to its target commits
        # the wrong file. The target's own edits belong to whichever group
        # named the target.
        self.write("target.txt", "t\n")
        self.git("add", "target.txt")
        self.git("commit", "-m", "Add the target")
        (self.root / "link.txt").symlink_to("target.txt")
        self.write("target.txt", "edited\n")
        done = self.attempt("MSG", "link.txt")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD").split(),
                         ["link.txt"])
        self.assertIn("target.txt", self.git("status", "--porcelain"))

    def test_a_symlinked_directory_in_the_path_still_resolves(self):
        # The parent still resolves, which is what a repo reached through a
        # symlinked path needs. Every test here runs under one, since
        # tempfile hands back /var on macOS and git prints /private/var.
        (self.root / "real").mkdir()
        self.write("real/deep.txt", "d\n")
        (self.root / "alias").symlink_to("real")
        done = self.attempt("MSG", "alias/deep.txt")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD").split(),
                         ["real/deep.txt"])


    def test_it_commits_a_symlink_to_a_directory(self):
        # git commits this link as one file, so naming it is fine. is_dir()
        # follows the link, so the widening check has to let symlinks past.
        (self.root / "real").mkdir()
        self.write("real/deep.txt", "d\n")
        self.git("add", "real")
        self.git("commit", "-m", "Add the directory")
        (self.root / "alias").symlink_to("real")
        done = self.attempt("MSG", "alias")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD").split(),
                         ["alias"])

    def test_it_stops_when_the_group_has_no_changes(self):
        # Naming a file with no edits stages nothing, so git refuses the
        # commit. Without this check the script blames a pre-commit hook.
        done = self.attempt("MSG", "seed.txt")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.commits(), 1)
        self.assertIn("nothing was staged", done.stdout + done.stderr)


class HookRecovery(Repo):
    REWRITES = """#!/bin/sh
echo run >> hook-runs.log
if [ -f .formatted ]; then exit 0; fi
touch .formatted
echo formatted >> a.txt
echo "files were modified by this hook" >&2
exit 1
"""

    REJECTS = """#!/bin/sh
echo run >> hook-runs.log
echo "E501 line too long" >&2
exit 1
"""

    def test_it_restages_and_retries_when_the_hook_rewrites_a_file(self):
        self.write("a.txt", "a\n")
        self.hook(self.REWRITES)
        done = self.attempt("MSG", "a.txt")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.hook_runs(), 2)

    def test_the_retry_commits_what_the_hook_wrote(self):
        self.write("a.txt", "a\n")
        self.hook(self.REWRITES)
        self.attempt("MSG", "a.txt")
        self.assertEqual(self.git("show", "HEAD:a.txt"), "a\nformatted\n")

    def test_the_retry_adds_exactly_one_commit(self):
        # An amend here would rewrite the commit the group before this one made.
        self.write("a.txt", "a\n")
        self.hook(self.REWRITES)
        before = self.commits()
        self.attempt("MSG", "a.txt")
        self.assertEqual(self.commits(), before + 1)

    def test_it_does_not_retry_a_hook_that_rewrote_nothing(self):
        # A lint error is not fixed by running it again.
        self.write("a.txt", "a\n")
        self.hook(self.REJECTS)
        done = self.attempt("MSG", "a.txt")
        self.assertEqual(done.returncode, 1)
        self.assertEqual(self.hook_runs(), 1)
        self.assertEqual(self.commits(), 1)

    def test_it_reports_what_the_hook_said(self):
        self.write("a.txt", "a\n")
        self.hook(self.REJECTS)
        done = self.attempt("MSG", "a.txt")
        self.assertIn("E501", done.stdout + done.stderr)


class AwkwardNames(Repo):
    """Paths git does not print as plain whitespace-free text."""

    SPACED = "2026-08-17 Mon.md"
    ACCENTED = "café.txt"

    REWRITES = """#!/bin/sh
echo run >> hook-runs.log
if [ -f .formatted ]; then exit 0; fi
touch .formatted
echo formatted >> "2026-08-17 Mon.md"
echo "files were modified by this hook" >&2
exit 1
"""

    def test_it_commits_a_path_with_a_space(self):
        self.write(self.SPACED, "note\n")
        done = self.attempt("MSG", self.SPACED)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_the_index_check_reads_a_spaced_path_whole(self):
        # Splitting git's listing on whitespace made this one path into two,
        # and neither half matched the group, so a correct commit was refused.
        self.write(self.SPACED, "note\n")
        self.git("add", self.SPACED)
        done = self.attempt("MSG", self.SPACED)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_the_index_check_reads_a_quoted_path_whole(self):
        # git prints a non-ASCII name as "caf\303\251.txt" unless told not to.
        self.write(self.ACCENTED, "note\n")
        self.git("add", self.ACCENTED)
        done = self.attempt("MSG", self.ACCENTED)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_a_spaced_path_outside_the_group_still_stops_the_commit(self):
        # Reading the whole path must not turn the check itself off.
        self.write("a.txt", "a\n")
        self.write(self.SPACED, "note\n")
        self.git("add", self.SPACED)
        done = self.attempt("MSG", "a.txt")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn(self.SPACED, done.stdout + done.stderr)

    def test_the_retry_names_a_rewritten_spaced_path_whole(self):
        self.write(self.SPACED, "note\n")
        self.hook(self.REWRITES)
        done = self.attempt("MSG", self.SPACED)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        # Not the whole of stdout: git's own commit output names the file too.
        announced = [line for line in done.stdout.splitlines()
                     if line.startswith("a hook rewrote")]
        self.assertTrue(announced and self.SPACED in announced[0], done.stdout)


class Gate(Repo):
    def test_a_message_with_an_error_commits_nothing(self):
        self.write("a.txt", "a\n")
        self.write("BAD", "feat: add the retry\n")
        done = subprocess.run([sys.executable, str(SCRIPT), "BAD", "a.txt"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.commits(), 1)
        self.assertIn("a.txt", self.git("status", "--porcelain"))

    def test_check_reports_without_committing(self):
        self.write("a.txt", "a\n")
        self.write("MSG", message("Subject line"))
        done = subprocess.run([sys.executable, str(SCRIPT), "--check", "MSG"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.commits(), 1)

    def test_a_message_without_files_is_a_usage_error(self):
        self.write("MSG", message("Subject line"))
        done = subprocess.run([sys.executable, str(SCRIPT), "MSG"], cwd=self.root,
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)

    def test_check_with_files_is_a_usage_error(self):
        # Silently ignoring them would read as a commit that never happened.
        self.write("a.txt", "a\n")
        self.write("MSG", message("Subject line"))
        done = subprocess.run([sys.executable, str(SCRIPT), "--check", "MSG", "a.txt"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)
        self.assertEqual(self.commits(), 1)

    def test_an_unreadable_message_file_is_a_usage_error(self):
        self.write("a.txt", "a\n")
        done = subprocess.run([sys.executable, str(SCRIPT), "ghost-msg", "a.txt"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)
        self.assertEqual(self.commits(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
