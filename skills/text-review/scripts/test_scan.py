#!/usr/bin/env python3
"""Fixtures for the checks a regex cannot express.

The pattern checks are readable on their own, so they are covered here only
where a bug would be silent: the sentence splitter, which decides what the
length check measures, and the dedup key, which a match string without a word
count would collide on.

    scripts/test_scan.py
"""

import tempfile
import unittest
from pathlib import Path

import scan


def sentence_of(n, tail="."):
    return " ".join(["alpha"] * n) + tail


class Scanned(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def hits(self, text, name, suffix=".md"):
        path = Path(self.tmp.name) / f"fixture{suffix}"
        path.write_text(text)
        return [h for h in scan.scan(path, scan.checks_for(path))
                if h.check.name == name]


class LongSentence(Scanned):
    LIMIT = 40

    def test_fires_above_the_limit(self):
        self.assertEqual(len(self.hits(sentence_of(41), "long-sentence")), 1)

    def test_quiet_at_the_limit(self):
        self.assertEqual(self.hits(sentence_of(self.LIMIT), "long-sentence"), [])

    def test_quiet_in_a_table_row(self):
        row = "| " + sentence_of(60, "") + " | b |"
        self.assertEqual(self.hits(row, "long-sentence"), [])

    def test_quiet_in_a_code_fence(self):
        fenced = "```\n" + sentence_of(60) + "\n```"
        self.assertEqual(self.hits(fenced, "long-sentence"), [])

    def test_quiet_in_an_html_comment(self):
        note = "<!-- " + sentence_of(60) + " -->"
        self.assertEqual(self.hits(note, "long-sentence"), [])

    def test_quiet_in_display_math(self):
        self.assertEqual(self.hits("$$ " + sentence_of(60) + " $$", "long-sentence"), [])

    def test_a_decimal_does_not_end_a_sentence(self):
        # Split here and one 45-word sentence reads as two short ones.
        text = " ".join(["alpha"] * 22 + ["0.405"] + ["beta"] * 22) + "."
        self.assertEqual(len(self.hits(text, "long-sentence")), 1)

    def test_a_number_before_a_period_still_ends_a_sentence(self):
        text = sentence_of(25, " 0.760.") + " " + sentence_of(25).capitalize()
        self.assertEqual(self.hits(text, "long-sentence"), [])

    def test_an_abbreviation_does_not_end_a_sentence(self):
        text = " ".join(["alpha"] * 20 + ["Fig. 1 and Smith et al. report"] + ["beta"] * 20)
        self.assertEqual(len(self.hits(text, "long-sentence")), 1)

    def test_a_citation_key_does_not_end_a_sentence(self):
        text = " ".join(["alpha"] * 22 + ["[@sec:coverage]"] + ["beta"] * 22) + "."
        self.assertEqual(len(self.hits(text, "long-sentence")), 1)

    def test_two_long_sentences_in_one_unit_both_report(self):
        # The dedup key is (check, line, match text), so a match string of the
        # bare count would drop the second hit.
        text = sentence_of(41) + " " + sentence_of(45).capitalize()
        self.assertEqual(len(self.hits(text, "long-sentence")), 2)

    def test_the_match_states_the_count(self):
        hit = self.hits(sentence_of(41), "long-sentence")[0]
        self.assertTrue(hit.match.startswith("41 words"), hit.match)

    def test_the_context_is_the_whole_sentence(self):
        hit = self.hits(sentence_of(60), "long-sentence")[0]
        self.assertEqual(len(hit.context.split()), 60)

    def test_a_list_item_is_measured(self):
        # Long bullets are run-on paragraphs with a dash in front, so they count.
        self.assertEqual(len(self.hits("- " + sentence_of(41), "long-sentence")), 1)

    def test_a_number_counts_as_one_word(self):
        # Forty words with the number whole, forty-one with it split in two.
        text = " ".join(["alpha"] * 37 + ["0.405", "62%", "beta"]) + "."
        self.assertEqual(self.hits(text, "long-sentence"), [])

    def test_a_citation_key_counts_as_one_word(self):
        text = " ".join(["alpha"] * 37 + ["[@sec:coverage]", "beta", "gamma"]) + "."
        self.assertEqual(self.hits(text, "long-sentence"), [])

    def test_a_colon_does_not_join_two_words(self):
        text = " ".join(["alpha"] * 39 + ["reason:", "beta"]) + "."
        self.assertEqual(len(self.hits(text, "long-sentence")), 1)


class Unquantified(Scanned):
    def test_fires_without_a_number(self):
        text = "None recovers more than a small fraction of those concepts."
        self.assertEqual(len(self.hits(text, "unquantified")), 1)

    def test_quiet_when_the_sentence_carries_the_number(self):
        text = "Recall moves a few hundredths, from 0.020 to 0.030."
        self.assertEqual(self.hits(text, "unquantified"), [])

    def test_every_phrase_fires(self):
        for phrase in ("a few", "a handful", "a small fraction", "a little"):
            with self.subTest(phrase=phrase):
                text = f"The gate recovers {phrase} of the missing content."
                self.assertEqual(len(self.hits(text, "unquantified")), 1)

    def test_the_noisy_words_stay_out(self):
        # These fired on correct prose during the sweep and named no defect.
        for word in ("several", "slightly", "somewhat", "marginally",
                     "minimal", "small"):
            with self.subTest(word=word):
                text = f"The penalty is {word} under both extractors."
                self.assertEqual(self.hits(text, "unquantified"), [])


class Unchanged(Scanned):
    def test_vague_quantifier_still_rewrites(self):
        hits = self.hits("Latency was elevated.", "vague-quantifier")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].check.action, "REWRITE")

    def test_em_dash_reports_once_per_comment_line(self):
        # A source file scans comment lines and then every line, at different
        # offsets for the same text, so the dedup key has to ignore offsets.
        self.assertEqual(len(self.hits("# a — b\n", "em-dash", ".py")), 1)

    def test_the_new_checks_ask_rather_than_assert(self):
        by_name = {c.name: c for c in scan.PROSE_CHECKS + scan.PROSE_ONLY_CHECKS}
        for name in ("long-sentence", "unquantified"):
            with self.subTest(name=name):
                self.assertEqual(by_name[name].action, "TEST")
                self.assertNotIn(name, scan.OPT_IN)


if __name__ == "__main__":
    unittest.main(verbosity=2)
