# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Hotfix regression tests for YT-01.R1.A6.HOTFIX (FIX-01..FIX-04) in v1.0.0-rc.3."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "youtube-creator-skill" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import hookscore  # noqa: E402
import retention  # noqa: E402


class TestRC3HotfixIntegrity(unittest.TestCase):
    # --- FIX-01: CSV Column Integrity ---
    def test_fix01_three_column_nan_does_not_shift_views_into_retention(self) -> None:
        csv_data = (
            "time_s,retention_pct,views\n"
            "0,100,500\n"
            "5,80,400\n"
            "10,NaN,700\n"
            "15,105,350\n"
            "20,60,200\n"
        )
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "retention.py"), "--format", "SHORT", "--duration", "20", "-"],
            input=csv_data, capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["axis"]["points_count"], 4)
        self.assertEqual(out["overview"]["dropped_invalid_rows"], 1)
        self.assertAlmostEqual(out["overview"]["max_retention_pct"], 105.0)
        self.assertTrue(any("Skipped 1" in w for w in out["warnings"]))
        # Must NOT take 700 views as retention or produce fake -595 pp cliff
        for cliff in out["cliffs_and_slide"]["cliffs"]:
            self.assertNotAlmostEqual(cliff["start_pct"], 700.0)
            self.assertGreater(cliff["delta_pp"], -100.0)

    def test_fix01_missing_x_missing_y_infinity_reordered_ambiguous_and_headerless(self) -> None:
        # Missing x, missing y, Infinity, -Infinity -> all dropped cleanly, views column never leaked
        dirty_csv = (
            "views,retention_pct,time_s\n"
            "500,100,0\n"
            "400,80,\n"          # missing x
            "300,,5\n"           # missing y
            "999,Infinity,10\n"  # Infinity y
            "888,75,-Infinity\n" # -Infinity x
            "350,90,15\n"
            "200,65,20\n"
        )
        pts, meta = retention.parse_curve(dirty_csv)
        self.assertEqual(pts, [(0.0, 100.0), (15.0, 90.0), (20.0, 65.0)])
        self.assertEqual(meta["rows_skipped"], 4)
        self.assertEqual(meta["x_header"], "time_s")
        self.assertEqual(meta["y_header"], "retention_pct")

        # Reordered 2-column CSV: retention first, time second
        reordered = "retention_pct,time_s\n100,0\n85,5\n70,10\n"
        pts_r, meta_r = retention.parse_curve(reordered)
        self.assertEqual(pts_r, [(0.0, 100.0), (5.0, 85.0), (10.0, 70.0)])

        # Ambiguous headers must fail closed with ValueError
        for bad_csv in [
            "col_a,col_b,col_c\n0,100,500\n5,80,400\n10,60,300\n",
            "time_s,elapsed_s,retention_pct\n0,0,100\n5,5,80\n10,10,60\n",
            "col1,col2\n0,100\n5,80\n10,60\n",
            "0,100,500\n5,80,400\n10,60,300\n",  # headerless 3-column CSV
        ]:
            with self.assertRaises(ValueError, msg=f"Expected ValueError for: {bad_csv}"):
                retention.parse_curve(bad_csv)

        # Headerless 2-column CSV works cleanly by fixed position [x, y]
        headerless_2 = "0,100\n5,85\n10,NaN\n15,70\n"
        pts_h, meta_h = retention.parse_curve(headerless_2)
        self.assertEqual(pts_h, [(0.0, 100.0), (5.0, 85.0), (15.0, 70.0)])
        self.assertEqual(meta_h["rows_skipped"], 1)

    # --- FIX-02: Axis Detection ---
    def test_fix02_retention_percent_y_header_does_not_force_percent_x_axis(self) -> None:
        csv_data = "time_s,retention_percent\n0,100\n10,80\n20,60\n"
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "retention.py"), "--format", "SHORT", "--duration", "20", "--time-unit", "auto", "-"],
            input=csv_data, capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["axis"]["input_time_unit"], "seconds")
        self.assertEqual(out["axis"]["observed_range_s"], [0.0, 20.0])

    def test_fix02_normalized_percentage_x_axis_still_detected(self) -> None:
        csv_pct = "video_percent,retention_pct\n0,100\n50,80\n100,60\n"
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "retention.py"), "--format", "SHORT", "--duration", "40", "--time-unit", "auto", "-"],
            input=csv_pct, capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["axis"]["input_time_unit"], "percent")
        self.assertEqual(out["axis"]["observed_range_s"], [0.0, 40.0])

        # Headerless percent x-axis with '%' markers
        csv_h_pct = "0%,100%\n50%,80%\n100%,60%\n"
        pts, meta = retention.parse_curve(csv_h_pct)
        t_pts, axis = retention.normalize_time(pts, "auto", 40.0, meta)
        self.assertEqual(axis["input_time_unit"], "percent")
        self.assertEqual(axis["observed_range_s"], [0.0, 40.0])

    # --- FIX-03: Transcript JSON Parser ---
    def test_fix03_transcript_json_array_segments_words_and_malformed_errors(self) -> None:
        # 1. Top-level JSON array (previously crashed with AttributeError: 'list' object has no attribute 'get')
        arr_json = json.dumps([
            {"start": 0.0, "end": 3.0, "text": "Hook reveal"},
            {"start": 12.0, "end": 15.0, "text": "Subscribe pitch"},
        ])
        cues_arr = retention._load_transcript_text(arr_json, "cues.json")
        self.assertEqual(len(cues_arr), 2)
        self.assertEqual(cues_arr[1][2], "Subscribe pitch")

        # 2. Segments object
        seg_json = json.dumps({"segments": [{"start": 0, "end": 2, "text": "Hello"}]})
        self.assertEqual(len(retention._load_transcript_text(seg_json, "seg.json")), 1)

        # 3. Words object
        word_json = json.dumps({"words": [{"start": 0.0, "end": 0.5, "word": "Drop"}]})
        self.assertEqual(retention._load_transcript_text(word_json, "w.json")[0][2], "Drop")

        # 4. Malformed JSON structures raise clean ValueError (and CLI returns exit 2 without traceback)
        for bad_json in [
            json.dumps({"unrelated": []}),
            json.dumps({"segments": "not_a_list"}),
            json.dumps([123, 456]),
            json.dumps([{"start": 5, "end": 2, "text": "reversed"}]),
        ]:
            with self.assertRaises(ValueError):
                retention._load_transcript_text(bad_json, "bad.json")

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            (tdp / "r.csv").write_text("time_s,retention_pct\n0,100\n5,80\n10,60\n", encoding="utf-8")
            (tdp / "arr.json").write_text(arr_json, encoding="utf-8")
            (tdp / "bad.json").write_text(json.dumps({"oops": 1}), encoding="utf-8")
            p_ok = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "retention.py"), str(tdp / "r.csv"), "--transcript", str(tdp / "arr.json")],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(p_ok.returncode, 0, p_ok.stderr)
            p_bad = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "retention.py"), str(tdp / "r.csv"), "--transcript", str(tdp / "bad.json")],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(p_bad.returncode, 2)
            self.assertNotIn("Traceback", p_bad.stderr)

    # --- FIX-04: Hook Timing Consistency ---
    def test_fix04_exact_wpm_math_and_format_consistency(self) -> None:
        # 9 words: 3.6s at 150 WPM (False), 3.0s at 180 WPM (True)
        h9 = hookscore.score_hook(
            "Copper isn't magnetic—why does it slow falling magnets?",
            pov="narrative", title="Why a Copper Pipe Slows Falling Magnets", video_format="SHORT",
        )
        self.assertEqual(h9["word_count"], 9)
        self.assertAlmostEqual(h9["est_spoken_sec_150_wpm"], 3.6)
        self.assertAlmostEqual(h9["est_spoken_sec_180_wpm"], 3.0)
        self.assertFalse(h9["fits_3s_at_150_wpm"])
        self.assertTrue(h9["fits_3s_at_180_wpm"])

        # 7 words: 2.8s at 150 WPM (True)
        h7 = hookscore.score_hook("Your cold balloon didn't lose its helium.", pov="direct", video_format="SHORT")
        self.assertEqual(h7["word_count"], 7)
        self.assertAlmostEqual(h7["est_spoken_sec_150_wpm"], 2.8)
        self.assertTrue(h7["fits_3s_at_150_wpm"])
        self.assertTrue(h7["fits_3s_at_180_wpm"])

        # 12-word hook in SHORT mode capped identically for BOTH direct AND narrative POVs
        h12_text = "You left your helium balloon in a cold car and it shrank."
        h12_short_direct = hookscore.score_hook(h12_text, pov="direct", video_format="SHORT")
        h12_short_narr = hookscore.score_hook(h12_text, pov="narrative", video_format="SHORT")
        self.assertLessEqual(h12_short_direct["rubric_0_to_10"]["speakability_visual"], 1)
        self.assertLessEqual(h12_short_narr["rubric_0_to_10"]["speakability_visual"], 1)
        self.assertTrue(any("Shorts opening" in r for r in h12_short_direct["reasons"]))
        self.assertTrue(any("Shorts opening" in r for r in h12_short_narr["reasons"]))

        # Same 12-word hook in LONG mode MUST NOT trigger Shorts 0-3s cap or Shorts warning
        h12_long_direct = hookscore.score_hook(h12_text, pov="direct", video_format="LONG")
        self.assertEqual(h12_long_direct["rubric_0_to_10"]["speakability_visual"], 2)
        self.assertFalse(any("Shorts opening" in r for r in h12_long_direct["reasons"]))


if __name__ == "__main__":
    unittest.main()
