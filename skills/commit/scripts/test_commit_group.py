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
import tempfile
import unittest
from pathlib import Path

import commit_group

SCRIPT = Path(__file__).resolve().parent / "commit_group.py"
TRAILER = "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"


def message(subject, body=None, trailer=TRAILER):
    parts = [subject]
    if body:
        parts.append(body)
    if trailer:
        parts.append(trailer)
    return "\n\n".join(parts) + "\n"


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
        # Only the conventional type list is banned, not every colon.
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
        # The exemption belongs to the trailer block, not to every "Word: " line.
        line = "Result: " + " ".join(["alpha"] * 16)
        self.assertGreater(len(line), 72)
        self.assertEqual(self.rules(message("Subject", line)), ["body-wrap"])


class Trailers(Checked):
    def test_the_harness_trailer_passes(self):
        text = (f"Subject line\n\n{TRAILER}\n"
                "Claude-Session: https://claude.ai/code/session_01C4BXdgYEoEWTb\n")
        self.assertEqual(self.errors(text), [])

    def test_a_trailer_longer_than_the_wrap_limit_passes(self):
        session = "Claude-Session: https://claude.ai/code/session_" + "x" * 40
        text = f"Subject line\n\n{TRAILER}\n{session}\n"
        self.assertGreater(len(session), 72)
        self.assertEqual(self.errors(text), [])

    def test_a_missing_co_authored_by_fails(self):
        self.assertEqual(self.rules("Subject line\n"), ["trailer-missing"])

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
        # is that a well-formed trailer exists, not that it matches one string.
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
        return subprocess.run(["python3", str(SCRIPT), *args], cwd=self.root,
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

    def test_it_refuses_an_argument_that_stages_the_tree(self):
        # Only the pathspecs. argparse turns a flag away before this check.
        self.write("a.txt", "a\n")
        for arg in (".", "..", "./", ":/", "*"):
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

    def test_it_stops_when_the_index_holds_a_path_it_was_not_given(self):
        # Committing here would fold another group's file into this commit.
        self.write("a.txt", "a\n")
        self.write("b.txt", "b\n")
        self.git("add", "b.txt")
        done = self.attempt("MSG", "a.txt")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.commits(), 1)


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
        done = subprocess.run(["python3", str(SCRIPT), "BAD", "a.txt"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.commits(), 1)
        self.assertIn("a.txt", self.git("status", "--porcelain"))

    def test_check_reports_without_committing(self):
        self.write("a.txt", "a\n")
        self.write("MSG", message("Subject line"))
        done = subprocess.run(["python3", str(SCRIPT), "--check", "MSG"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.commits(), 1)

    def test_a_message_without_files_is_a_usage_error(self):
        self.write("MSG", message("Subject line"))
        done = subprocess.run(["python3", str(SCRIPT), "MSG"], cwd=self.root,
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)

    def test_check_with_files_is_a_usage_error(self):
        # Silently ignoring them would read as a commit that never happened.
        self.write("a.txt", "a\n")
        self.write("MSG", message("Subject line"))
        done = subprocess.run(["python3", str(SCRIPT), "--check", "MSG", "a.txt"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)
        self.assertEqual(self.commits(), 1)

    def test_an_unreadable_message_file_is_a_usage_error(self):
        self.write("a.txt", "a\n")
        done = subprocess.run(["python3", str(SCRIPT), "ghost-msg", "a.txt"],
                              cwd=self.root, capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)
        self.assertEqual(self.commits(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
