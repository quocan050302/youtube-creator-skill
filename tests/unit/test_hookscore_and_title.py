# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Unit tests for hookscore.py and title_linter.py."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "youtube-creator-skill" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import hookscore  # noqa: E402
import title_linter  # noqa: E402


class TestHookscore(unittest.TestCase):
    def test_strong_vs_weak_hook_and_narrative_mode(self) -> None:
        weak = hookscore.score_hook("Hey guys welcome back to my channel today for an amazing crazy video because it is cool.", pov="direct")
        strong = hookscore.score_hook("Copper isn't magnetic, yet it stops a falling magnet in midair without touching it.", pov="narrative", title="Why Copper Stops a Falling Magnet")
        self.assertGreater(strong["rubric_total"], weak["rubric_total"])
        self.assertGreater(strong["legacy_verdict_0_to_100"], weak["legacy_verdict_0_to_100"])
        self.assertEqual(strong["formula_id"], "the-impossible")
        # Direct mode vs narrative mode behaves distinctly for 3rd-person hooks
        direct_story = hookscore.score_hook("Copper isn't magnetic, yet it stops a falling magnet in midair without touching it.", pov="direct")
        self.assertGreater(strong["legacy_panel_0_to_100"]["address"], direct_story["legacy_panel_0_to_100"]["address"])

    def test_empty_duplicate_unicode_and_stable_ties(self) -> None:
        with self.assertRaises(ValueError):
            hookscore.score_hook("   ")
        ranked = hookscore.rank_hooks([
            "Tại sao đồng làm chậm nam châm rơi mà không cần chạm vào?",
            "Tại sao đồng làm chậm nam châm rơi mà không cần chạm vào?",
            "97% of channels quit before video 30 — here is what changes.",
        ], pov="narrative")
        self.assertEqual(ranked["duplicates_removed"], 1)
        self.assertEqual(ranked["count_evaluated"], 2)
        self.assertIn("NEVER predicts", ranked["limitations"])
        self.assertEqual(ranked["formulas_count"], 21)

    def test_cli_exit_code_2_on_missing_input(self) -> None:
        rc = hookscore.main(["nonexistent_file_xyz.txt"])
        self.assertEqual(rc, 2)


class TestTitleLinter(unittest.TestCase):
    def test_identical_thumb_and_caps_emoji_spam_flagged(self) -> None:
        res = title_linter.lint_title(
            "AMAZING SECRET TRICK YOU MUST SEE NOW!! 🔥🔥",
            thumbs=["AMAZING SECRET TRICK YOU MUST SEE NOW!! 🔥🔥"],
            video_format="SHORT",
        )
        codes = {w["code"] for w in res["warnings"]}
        self.assertIn("caps_spam", codes)
        self.assertIn("vague_hype", codes)
        self.assertIn("punctuation_emoji_clutter", codes)
        thumb_codes = {w["code"] for w in res["thumbnail_comparisons"][0]["warnings"]}
        self.assertIn("identical_title_thumb", thumb_codes)

    def test_clean_complementary_title_and_missing_thumb_unknown(self) -> None:
        res = title_linter.lint_title("Why Copper Stops a Falling Magnet", thumbs=["NOT MAGNETIC"], video_format="SHORT")
        self.assertEqual(res["thumbnail_comparisons"][0]["status"], "COMPLEMENTARY_LEXICAL")
        self.assertEqual(res["thumbnail_comparisons"][0]["shared_tokens"], [])
        self.assertGreaterEqual(res["heuristic_score_0_to_100"], 90)

        no_thumb = title_linter.lint_title("Why Copper Stops a Falling Magnet", thumbs=None, video_format="SHORT")
        self.assertEqual(no_thumb["thumbnail_comparisons"][0]["status"], "UNKNOWN_NO_THUMBNAIL_TEXT")

    def test_multilingual_and_near_duplicate_detection(self) -> None:
        ranked = title_linter.rank_titles([
            "Tại sao ống đồng làm chậm nam châm rơi",
            "Tại sao ống đồng làm chậm nam châm rơi?",
            "How Eddy Currents Brake a Falling Magnet Without Magnetic Attraction or Contact in High-Speed Lab Tests Over 100 Characters Long",
        ], video_format="SHORT")
        self.assertEqual(len(ranked["near_duplicates_detected"]), 1)
        hard_warns = [w["code"] for r in ranked["results"] for w in r["warnings"]]
        self.assertIn("exceeds_hard_limit", hard_warns)


if __name__ == "__main__":
    unittest.main()
