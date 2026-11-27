# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Unit & regression tests for outlier_analyzer.py and retention.py."""
from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "youtube-creator-skill" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import outlier_analyzer  # noqa: E402
import retention  # noqa: E402


class TestOutlierAnalyzer(unittest.TestCase):
    def test_known_fixture_leave_one_out_median(self) -> None:
        # Prompt Section 10.1 exact fixture:
        # candidate=500, peer views=[50, 100, 100, 150, 200] => baseline=100, ratio=5.0
        rows = [
            {"channel": "LabA", "video_id": "v_cand", "title": "Why Copper Stops a Magnet", "format": "SHORT", "published_at": "2026-11-10", "observed_at": "2026-11-25", "views": 500},
            {"channel": "LabA", "video_id": "v_p1", "title": "Peer 1", "format": "SHORT", "published_at": "2026-11-11", "observed_at": "2026-11-25", "views": 50},
            {"channel": "LabA", "video_id": "v_p2", "title": "Peer 2", "format": "SHORT", "published_at": "2026-11-12", "observed_at": "2026-11-25", "views": 100},
            {"channel": "LabA", "video_id": "v_p3", "title": "Peer 3", "format": "SHORT", "published_at": "2026-11-13", "observed_at": "2026-11-25", "views": 100},
            {"channel": "LabA", "video_id": "v_p4", "title": "Peer 4", "format": "SHORT", "published_at": "2026-11-14", "observed_at": "2026-11-25", "views": 150},
            {"channel": "LabA", "video_id": "v_p5", "title": "Peer 5", "format": "SHORT", "published_at": "2026-11-15", "observed_at": "2026-11-25", "views": 200},
        ]
        res = outlier_analyzer.rank_outliers(rows, min_ratio=2.0)
        self.assertEqual([o["video_id"] for o in res["outliers"]], ["v_cand", "v_p5"])
        top = res["outliers"][0]
        self.assertEqual(top["video_id"], "v_cand")
        self.assertEqual(top["peer_count_excluding_candidate"], 5)
        self.assertAlmostEqual(top["peer_median_views"], 100.0)
        self.assertAlmostEqual(top["outlier_ratio"], 5.0)
        self.assertEqual(top["sample_quality"], "target_n_met")
        self.assertAlmostEqual(res["outliers"][1]["outlier_ratio"], 2.0)

    def test_mixed_formats_age_buckets_dupes_nulls_and_zero_median(self) -> None:
        rows = [
            # Valid SHORT cohort (8-30d)
            {"channel": "Ch1", "video_id": "s1", "title": "A", "format": "SHORT", "published_at": "2026-11-10", "views": 400},
            {"channel": "Ch1", "video_id": "s1", "title": "A dup", "format": "SHORT", "published_at": "2026-11-10", "views": 400},  # dup
            {"channel": "Ch1", "video_id": "s2", "title": "B", "format": "SHORT", "published_at": "2026-11-11", "views": 100},
            {"channel": "Ch1", "video_id": "s3", "title": "C", "format": "SHORT", "published_at": "2026-11-12", "views": 100},
            {"channel": "Ch1", "video_id": "s4", "title": "D", "format": "SHORT", "published_at": "2026-11-13", "views": 100},
            {"channel": "Ch1", "video_id": "s5", "title": "E", "format": "SHORT", "published_at": "2026-11-14", "views": 100},
            # Null view -> MUST be excluded, NEVER coerced to 0
            {"channel": "Ch1", "video_id": "s_null", "title": "Missing", "format": "SHORT", "published_at": "2026-11-14", "views": None},
            # LONG video must stay in separate cohort (insufficient peers)
            {"channel": "Ch1", "video_id": "l1", "title": "Long vid", "format": "LONG", "published_at": "2026-11-10", "views": 50000},
            # Mature 365d+ video must stay in separate age bucket
            {"channel": "Ch1", "video_id": "s_old", "title": "Old", "format": "SHORT", "published_at": "2024-01-01", "views": 999999},
            # Future publish date invalid
            {"channel": "Ch1", "video_id": "s_future", "title": "Future", "format": "SHORT", "published_at": "2027-01-01", "views": 500},
            # Zero-median cohort
            {"channel": "ZeroCh", "video_id": "z1", "title": "Z1", "format": "SHORT", "published_at": "2026-11-10", "views": 50},
            {"channel": "ZeroCh", "video_id": "z2", "title": "Z2", "format": "SHORT", "published_at": "2026-11-11", "views": 0},
            {"channel": "ZeroCh", "video_id": "z3", "title": "Z3", "format": "SHORT", "published_at": "2026-11-12", "views": 0},
            {"channel": "ZeroCh", "video_id": "z4", "title": "Z4", "format": "SHORT", "published_at": "2026-11-13", "views": 0},
            {"channel": "ZeroCh", "video_id": "z5", "title": "Z5", "format": "SHORT", "published_at": "2026-11-14", "views": 0},
        ]
        res = outlier_analyzer.rank_outliers(rows, min_ratio=2.0, as_of=dt.date(2026, 11, 25))
        self.assertEqual([o["video_id"] for o in res["outliers"]], ["s1"])
        self.assertEqual(res["outliers"][0]["sample_quality"], "exploratory_low_n")
        reasons = {e["reason"] for e in res["excluded_rows"]}
        self.assertIn("duplicate_video_id", reasons)
        self.assertIn("missing_or_invalid_views", reasons)
        self.assertIn("published_after_observed", reasons)
        self.assertIn("zero_or_invalid_peer_median", reasons)
        self.assertGreaterEqual(len(res["insufficient_cohorts"]), 2)


class TestRetention(unittest.TestCase):
    def test_pp_drop_and_rewatch_above_100_preserved(self) -> None:
        # 100 -> 80 between 0 and 3s is -20.0 pp; rewatch spike at 15s -> 112% must NOT be clamped
        csv_data = "\ufeffseconds;retention\n0;100,0%\n3;80,0%\n10;78,0%\n15;112,5%\n25;65,0%\n30;45,0%\n40;42,0%\n"
        pts, meta = retention.parse_curve(csv_data)
        t_pts, axis = retention.normalize_time(pts, "seconds", 40.0, meta)
        n_pts, rate = retention.normalize_rate(t_pts, "auto", meta)
        early = retention.detect_early_change(n_pts, "SHORT", 40.0)
        cliffs = retention.detect_cliffs(n_pts, min_drop_pp=5.0, slope_multiplier=1.2)
        summary = retention.summarize(n_pts, axis, rate, early, cliffs, None)

        w3 = early["windows"][0]
        self.assertEqual(w3["window_end_s"], 3.0)
        self.assertAlmostEqual(w3["delta_pp"], -20.0)
        self.assertTrue(summary["overview"]["has_rewatch_above_100pct"])
        self.assertAlmostEqual(summary["overview"]["max_retention_pct"], 112.5)
        self.assertTrue(any(s["delta_pp"] > 30 for s in cliffs["rewatch_or_skip_spikes"]))

    def test_percent_axis_requires_duration_and_aligns_srt(self) -> None:
        csv_pct = "pct,retention\n0%,100%\n10%,92%\n30%,88%\n40%,64%\n60%,62%\n100%,55%\n"
        pts, meta = retention.parse_curve(csv_pct)
        with self.assertRaises(ValueError):
            retention.normalize_time(pts, "percent", None, meta)

        t_pts, axis = retention.normalize_time(pts, "percent", 100.0, meta)
        n_pts, rate = retention.normalize_rate(t_pts, "percent", meta)
        cliffs = retention.detect_cliffs(n_pts, min_drop_pp=5.0, slope_multiplier=1.5)
        srt = "1\n00:00:29,000 --> 00:00:38,000\nNow before we get started let me thank our sponsor.\n"
        cues = retention._load_transcript_text(srt, "test.srt")
        aligned = retention.align_transcript(cliffs["cliffs"], cues)
        self.assertGreaterEqual(len(aligned), 1)
        self.assertEqual(aligned[0]["cliff_interval_s"], [30.0, 40.0])
        self.assertAlmostEqual(aligned[0]["delta_pp"], -24.0)
        self.assertIn("thank our sponsor", aligned[0]["transcript_excerpt"])
        self.assertEqual(aligned[0]["attribution_note"], "possible_contributor_not_proven_cause")

    def test_rejects_bad_duration_and_ambiguous_rate(self) -> None:
        pts = [(0.0, 1.4), (5.0, 1.2), (10.0, 0.9)]
        with self.assertRaises(ValueError):
            retention.normalize_time(pts, "seconds", 0.0, {})
        with self.assertRaises(ValueError):
            retention.normalize_rate(pts, "auto", {"pct_sign_seen_y": False})


if __name__ == "__main__":
    unittest.main()
