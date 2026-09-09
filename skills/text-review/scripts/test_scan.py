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


class ContrastiveVoice(Scanned):
    """The construction is out of his voice, so every hit is a violation."""

    def test_rather_than_fires(self):
        hits = self.hits("The size difference is aggregation rather than better linking.",
                         "contrastive-voice")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].check.action, "REWRITE")

    def test_comma_not_fires(self):
        self.assertEqual(len(self.hits("Format is a covariate, not a control.",
                                       "contrastive-voice")), 1)

    def test_a_heading_fires(self):
        # Section titles carried two of these until the sweep of 2026-09-02.
        text = "### 5.4 Low precision is over-inclusion, not invention"
        self.assertEqual(len(self.hits(text, "contrastive-voice")), 1)

    def test_a_table_cell_fires(self):
        self.assertEqual(len(self.hits("| a | Metric configuration, not model behavior |",
                                       "contrastive-voice")), 1)

    def test_a_blockquote_stays_quiet(self):
        # Quoted material is a record of what was sent or said. Editing it
        # misreports the source.
        text = "> A Brief Hospital Course summarizes the trajectory, not the full record."
        self.assertEqual(self.hits(text, "contrastive-voice"), [])

    def test_more_than_does_not_fire(self):
        self.assertEqual(self.hits("Recall is larger than precision here.",
                                   "contrastive-voice"), [])


class CommaJoin(Scanned):
    """Independent clauses take a period, whichever conjunction joins them."""

    def test_a_new_subject_fires(self):
        hits = self.hits("The model converged, and the loss plateaued at 0.3.",
                         "comma-join")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].check.action, "REWRITE")

    def test_the_paired_cross_reference_fires(self):
        # Ten of these in the paper, all under 25 words, so long-sentence
        # never reached them.
        text = ("[@Sec:working-budget] states how the overhead term was determined, "
                "and [@sec:feasibility] reports it.")
        self.assertEqual(len(self.hits(text, "comma-join")), 1)

    def test_a_pronoun_subject_fires(self):
        self.assertEqual(len(self.hits("The filter is group-level, and it stays that way.",
                                       "comma-join")), 1)

    def test_a_serial_list_whose_last_item_looks_finite_stays_quiet(self):
        # "the process ... are" reads as subject plus verb. An earlier comma in
        # the same sentence is what tells the two shapes apart.
        text = ("The header patterns, the end-boundary list, and the process "
                "that produced them are in Appendix [ref].")
        self.assertEqual(self.hits(text, "comma-join"), [])

    def test_a_second_sentence_is_judged_on_its_own(self):
        # The check reads one sentence at a time, so a list in the first must
        # not silence a join in the second.
        text = ("It reads notes, labs, and orders. The model converged, "
                "and the loss plateaued at 0.3.")
        self.assertEqual(len(self.hits(text, "comma-join")), 1)

    def test_a_serial_list_stays_quiet(self):
        text = "The input holds notes, laboratory results, and medication orders."
        self.assertEqual(self.hits(text, "comma-join"), [])

    def test_a_compound_predicate_stays_quiet(self):
        # One subject, two verbs. A period would strand the second.
        text = "The script reads the artifact, and writes the scores beside it."
        self.assertEqual(self.hits(text, "comma-join"), [])

    def test_a_trailing_participle_stays_quiet(self):
        text = "Recall moves by 0.007, and every interval spanning zero."
        self.assertEqual(self.hits(text, "comma-join"), [])

    def test_a_blockquote_stays_quiet(self):
        self.assertEqual(self.hits("> The model converged, and the loss plateaued.",
                                   "comma-join"), [])


class HtmlComments(Scanned):
    """Half of the dissertation file is drafting comments, which drown the report."""

    NOTE = "<!-- Storyline: the section is aggregation rather than better linking. -->"
    PROSE = "The size difference is aggregation rather than linking."

    def skipped(self, text, name="contrastive-voice"):
        path = Path(self.tmp.name) / "fixture.md"
        path.write_text(text)
        return [h for h in scan.scan(path, scan.checks_for(path), skip_html_comments=True)
                if h.check.name == name]

    def test_a_comment_is_scanned_by_default(self):
        self.assertEqual(len(self.hits(self.NOTE, "contrastive-voice")), 1)

    def test_skip_drops_the_comment(self):
        self.assertEqual(self.skipped(self.NOTE), [])

    def test_skip_keeps_prose_after_a_blank_line(self):
        self.assertEqual(len(self.skipped(self.NOTE + "\n\n" + self.PROSE)), 1)

    def test_a_multiline_comment_is_skipped_whole(self):
        self.assertEqual(
            self.skipped("<!-- Storyline:\nthe rule is a covariate, not a control.\n-->"), [])

    # A note written tight against its paragraph used to take the paragraph
    # with it, silently, because the flag was one boolean per unit.
    def test_skip_keeps_prose_on_the_line_after_a_comment(self):
        self.assertEqual(len(self.skipped(self.NOTE + "\n" + self.PROSE)), 1)

    def test_skip_keeps_prose_on_the_line_before_a_comment(self):
        self.assertEqual(len(self.skipped(self.PROSE + "\n" + self.NOTE)), 1)

    def test_skip_keeps_prose_sharing_a_line_with_a_comment(self):
        self.assertEqual(len(self.skipped(self.NOTE + " " + self.PROSE)), 1)

    def test_a_comment_marker_inside_a_fence_opens_nothing(self):
        text = "```\nx <!-- y\n```\n\n" + self.PROSE
        self.assertEqual(len(self.skipped(text)), 1)


class DedupLabel(Scanned):
    """A constant label collapses repeats inside one unit and undercounts."""

    def test_two_contrasts_in_one_unit_both_report(self):
        text = "A is x rather than y. B is p rather than q."
        self.assertEqual(len(self.hits(text, "contrastive-voice")), 2)

    def test_two_joins_in_one_unit_both_report(self):
        text = ("The model converged, and the loss plateaued. "
                "The cache grew, and the budget held.")
        self.assertEqual(len(self.hits(text, "comma-join")), 2)


class Conjunctions(Scanned):
    """The rule names "and" alone. Every other coordinator states a relation."""

    def test_but_stays_quiet(self):
        # A concession is a relationship, and a period drops it.
        self.assertEqual(self.hits("The model converged, but the loss held.",
                                   "comma-join"), [])

    def test_or_stays_quiet(self):
        self.assertEqual(self.hits("The model converges, or the loader retries.",
                                   "comma-join"), [])

    def test_so_stays_quiet(self):
        # 89 of these in one manuscript against 4 with ", and". A period drops
        # the consequence the conjunction states.
        self.assertEqual(self.hits("The gates closed negative, so the build does not happen.",
                                   "comma-join"), [])

    def test_for_stays_quiet(self):
        self.assertEqual(self.hits("The table does not compare, for four reasons hold.",
                                   "comma-join"), [])

    def test_an_introductory_comma_suppresses_a_genuine_join(self):
        # Known cost of skipping a sentence that already holds a comma. Two
        # genuine joins in one manuscript are lost this way.
        self.assertEqual(self.hits("However, the model converged, and the loss plateaued.",
                                   "comma-join"), [])


class VagueHold(Scanned):
    """"Hold" reads as possession or as staying steady, and only the first goes."""

    def test_possession_fires(self):
        self.assertEqual(len(self.hits("The cohort holds 116 admissions.",
                                       "possession-verb")), 1)

    def test_staying_steady_is_quiet(self):
        self.assertEqual(self.hits(
            "The rule holds where the contrast is informative.", "possession-verb"), [])

    def test_the_particle_senses_are_quiet(self):
        for line in ("The argument holds together.",
                     "Recall holds to the longest admissions.",
                     "The jargon check is held back from prose.",
                     "Many tables give the reader more to hold at once."):
            with self.subTest(line=line):
                self.assertEqual(self.hits(line, "possession-verb"), [])

    def test_the_participle_never_fires(self):
        # His sweep of one manuscript rewrote 44 instances and left every
        # "held", so the form costs more in noise than it finds.
        self.assertEqual(self.hits("The file held 7.5B parameters.",
                                   "possession-verb"), [])

    def test_a_comment_is_read(self):
        # The word reaches a comment the same way it reaches a paragraph.
        self.assertEqual(len(self.hits("# The index holds the staged paths.\n",
                                       "possession-verb", ".py")), 1)

    def test_it_asks_rather_than_rewrites(self):
        hits = self.hits("The row holds three statistics.", "possession-verb")
        self.assertEqual(hits[0].check.action, "TEST")


class Unchanged(Scanned):
    def test_vague_quantifier_still_rewrites(self):
        hits = self.hits("Latency was elevated.", "vague-quantifier")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].check.action, "REWRITE")

    def test_em_dash_reports_once_per_comment_line(self):
        # A source file scans comment lines and then every line, at different
        # offsets for the same text, so the dedup key has to ignore offsets.
        self.assertEqual(len(self.hits("# a — b\n", "em-dash", ".py")), 1)

    def test_the_noisy_checks_still_ask(self):
        by_name = {c.name: c for c in scan.PROSE_CHECKS + scan.PROSE_ONLY_CHECKS}
        for name in ("long-sentence", "unquantified"):
            with self.subTest(name=name):
                self.assertEqual(by_name[name].action, "TEST")
                self.assertNotIn(name, scan.OPT_IN)

    def test_the_two_voice_checks_assert(self):
        by_name = {c.name: c for c in scan.PROSE_CHECKS}
        for name in ("contrastive-voice", "comma-join"):
            with self.subTest(name=name):
                self.assertEqual(by_name[name].action, "REWRITE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
