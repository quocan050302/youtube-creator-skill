# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Baseline-vs-adapted regression tests using pinned synthetic fixtures."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "youtube-creator-skill" / "scripts"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


class TestFixtureRegressions(unittest.TestCase):
    def test_outlier_fixture_eliminates_candidate_in_median_leakage(self) -> None:
        # With candidate=500 included in median([50,100,100,150,200,500]) => median=125 => ratio=4.0 (WRONG / upstream bug)
        # With leave-one-out peers=[50,100,100,150,200] => median=100 => ratio=5.0 (CORRECT)
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "outlier_analyzer.py"), str(FIXTURES_DIR / "sample_outliers.json"), "--min", "2.0"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        top = data["outliers"][0]
        self.assertEqual(top["video_id"], "vid_01")
        self.assertAlmostEqual(top["peer_median_views"], 100.0)
        self.assertAlmostEqual(top["outlier_ratio"], 5.0)

    def test_locale_csv_retention_fixture(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "retention.py"), str(FIXTURES_DIR / "sample_retention_locale.csv"), "--format", "SHORT", "--duration", "45"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertAlmostEqual(data["early_window_change"]["windows"][0]["delta_pp"], -20.0)
        self.assertTrue(data["overview"]["has_rewatch_above_100pct"])
        self.assertAlmostEqual(data["overview"]["max_retention_pct"], 110.0)

    def test_transcript_and_chapters_fixtures(self) -> None:
        p_tr = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "transcript_analyzer.py"), str(FIXTURES_DIR / "sample_transcript.srt"), "--floor", "0.45"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(p_tr.returncode, 0, p_tr.stderr)
        tr_data = json.loads(p_tr.stdout)
        kinds = {c["kind"] for c in tr_data["candidates"]}
        self.assertEqual(kinds, {"FILLER_CANDIDATE", "RESTART_CANDIDATE", "GAP_CANDIDATE"})

        p_ch = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "chapters.py"), "--validate", str(FIXTURES_DIR / "sample_chapters.txt"), "--duration", "180"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(p_ch.returncode, 0, p_ch.stderr)
        self.assertTrue(json.loads(p_ch.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
