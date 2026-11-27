# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Regression tests for FINAL MICRO-FIX — RETENTION UNIT PRECEDENCE in v1.0.0-rc.4."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "youtube-creator-skill" / "scripts"


def _run_retention(raw_input: str, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "retention.py"), *extra_args, "-"],
        input=raw_input,
        capture_output=True,
        text=True,
        check=False,
    )


class TestRC4RetentionUnitPrecedence(unittest.TestCase):
    # --- Mandatory Fixture 1 ---
    def test_fixture1_csv_retention_pct_small_values_kept_as_percent_not_x100(self) -> None:
        csv_data = "time_s,retention_pct\n0,1\n5,0.8\n10,0.5\n"
        proc = _run_retention(csv_data, "--format", "SHORT", "--duration", "10")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["rate_unit_input"], "percent")
        self.assertAlmostEqual(out["overview"]["start_retention_pct"], 1.0)
        self.assertAlmostEqual(out["overview"]["max_retention_pct"], 1.0)
        self.assertAlmostEqual(out["overview"]["end_retention_pct"], 0.5)
        self.assertAlmostEqual(out["overview"]["min_retention_pct"], 0.5)

    # --- Mandatory Fixture 2 ---
    def test_fixture2_json_time_s_0_50_100_duration_120_keeps_seconds_range(self) -> None:
        shapes = [
            json.dumps([
                {"time_s": 0, "retention_pct": 100},
                {"time_s": 50, "retention_pct": 80},
                {"time_s": 100, "retention_pct": 60},
            ]),
            json.dumps({"points": [
                {"time_s": 0, "retention_pct": 100},
                {"time_s": 50, "retention_pct": 80},
                {"time_s": 100, "retention_pct": 60},
            ]}),
            json.dumps({"time_s": [0, 50, 100], "retention_pct": [100, 80, 60]}),
        ]
        for idx, payload in enumerate(shapes):
            proc = _run_retention(payload, "--duration", "120", "--time-unit", "auto")
            self.assertEqual(proc.returncode, 0, f"shape {idx}: {proc.stderr}")
            out = json.loads(proc.stdout)
            self.assertEqual(out["axis"]["input_time_unit"], "seconds", f"shape {idx}")
            self.assertEqual(out["axis"]["observed_range_s"], [0.0, 100.0], f"shape {idx}")
            self.assertAlmostEqual(out["axis"]["duration_s"], 120.0)

    # --- Mandatory Fixture 3 ---
    def test_fixture3_json_pct_0_20_40_duration_200_converts_to_0_80s(self) -> None:
        shapes = [
            json.dumps([
                {"pct": 0, "retention_pct": 100},
                {"pct": 20, "retention_pct": 80},
                {"pct": 40, "retention_pct": 60},
            ]),
            json.dumps({"points": [
                {"pct": 0, "retention_pct": 100},
                {"pct": 20, "retention_pct": 80},
                {"pct": 40, "retention_pct": 60},
            ]}),
            json.dumps({"pct": [0, 20, 40], "retention_pct": [100, 80, 60]}),
        ]
        for idx, payload in enumerate(shapes):
            proc = _run_retention(payload, "--duration", "200", "--time-unit", "auto")
            self.assertEqual(proc.returncode, 0, f"shape {idx}: {proc.stderr}")
            out = json.loads(proc.stdout)
            self.assertEqual(out["axis"]["input_time_unit"], "percent", f"shape {idx}")
            self.assertEqual(out["axis"]["observed_range_s"], [0.0, 80.0], f"shape {idx}")
            self.assertAlmostEqual(out["axis"]["duration_s"], 200.0)

    # --- Precedence: CLI explicit > CSV header / JSON key > warned inference ---
    def test_precedence_cli_explicit_overrides_header_and_key_with_warning(self) -> None:
        # CLI --rate-unit ratio overrides CSV retention_pct header
        p_rate = _run_retention("time_s,retention_pct\n0,1\n5,0.8\n10,0.5\n", "--rate-unit", "ratio")
        self.assertEqual(p_rate.returncode, 0, p_rate.stderr)
        out_r = json.loads(p_rate.stdout)
        self.assertEqual(out_r["rate_unit_input"], "ratio")
        self.assertAlmostEqual(out_r["overview"]["max_retention_pct"], 100.0)
        self.assertAlmostEqual(out_r["overview"]["end_retention_pct"], 50.0)
        self.assertTrue(any("overrides" in w for w in out_r["warnings"]))

        # CLI --time-unit seconds overrides JSON pct key
        j_pct = json.dumps({"pct": [0, 20, 40], "retention_pct": [100, 80, 60]})
        p_sec = _run_retention(j_pct, "--duration", "200", "--time-unit", "seconds")
        self.assertEqual(p_sec.returncode, 0, p_sec.stderr)
        out_s = json.loads(p_sec.stdout)
        self.assertEqual(out_s["axis"]["input_time_unit"], "seconds")
        self.assertEqual(out_s["axis"]["observed_range_s"], [0.0, 40.0])
        self.assertTrue(any("overrides" in w for w in out_s["warnings"]))

        # CLI --time-unit percent overrides JSON time_s key
        j_sec = json.dumps({"time_s": [0, 50, 100], "retention_pct": [100, 80, 60]})
        p_pct = _run_retention(j_sec, "--duration", "120", "--time-unit", "percent")
        self.assertEqual(p_pct.returncode, 0, p_pct.stderr)
        out_p = json.loads(p_pct.stdout)
        self.assertEqual(out_p["axis"]["input_time_unit"], "percent")
        self.assertEqual(out_p["axis"]["observed_range_s"], [0.0, 120.0])
        self.assertTrue(any("overrides" in w for w in out_p["warnings"]))

    def test_explicit_ratio_header_and_tier3_warned_inference(self) -> None:
        # Explicit retention_ratio header -> ratio without CLI flag
        p_ratio = _run_retention("time_s,retention_ratio\n0,1\n5,0.8\n10,0.5\n")
        self.assertEqual(p_ratio.returncode, 0, p_ratio.stderr)
        out_ratio = json.loads(p_ratio.stdout)
        self.assertEqual(out_ratio["rate_unit_input"], "ratio")
        self.assertAlmostEqual(out_ratio["overview"]["max_retention_pct"], 100.0)

        # Tier 3 inference on unitless headerless data emits warnings
        p_inf = _run_retention("0,1\n50,0.8\n100,0.5\n", "--duration", "120")
        self.assertEqual(p_inf.returncode, 0, p_inf.stderr)
        out_inf = json.loads(p_inf.stdout)
        self.assertEqual(out_inf["axis"]["input_time_unit"], "percent")
        self.assertEqual(out_inf["axis"]["observed_range_s"], [0.0, 120.0])
        self.assertEqual(out_inf["rate_unit_input"], "ratio")
        self.assertAlmostEqual(out_inf["overview"]["max_retention_pct"], 100.0)
        self.assertTrue(any("Inferred x-axis as percent" in w for w in out_inf["warnings"]))
        self.assertTrue(any("Inferred 0..1 ratio" in w for w in out_inf["warnings"]))

    # --- Ambiguity and Contradictions -> exit 2 ---
    def test_ambiguous_or_contradictory_units_return_exit_2(self) -> None:
        cases = [
            # Contradictory headers
            ("seconds_pct,retention_pct\n0,100\n50,80\n100,60\n", ("--duration", "120")),
            ("time_s,retention_pct_ratio\n0,1\n5,0.8\n10,0.5\n", ()),
            # Seconds header vs '%' x-values
            ("time_s,retention_pct\n0%,100\n50%,80\n100%,60\n", ("--duration", "120")),
            # Ratio header vs '%' y-values
            ("time_s,retention_ratio\n0,100%\n5,80%\n10,60%\n", ()),
            # Ratio header vs 0..100 values
            ("time_s,retention_ratio\n0,100\n5,80\n10,60\n", ()),
            # CLI --time-unit seconds vs '%' x-values
            ("0%,100\n50%,80\n100%,60\n", ("--time-unit", "seconds", "--duration", "120")),
            # CLI --rate-unit ratio vs '%' y-values or 100-scale values
            ("time_s,retention\n0,100%\n5,80%\n10,60%\n", ("--rate-unit", "ratio")),
            ("time_s,retention\n0,100\n5,80\n10,60\n", ("--rate-unit", "ratio")),
            # Conflicting JSON x keys in one object
            (json.dumps([
                {"time_s": 0, "pct": 0, "retention_pct": 100},
                {"time_s": 50, "pct": 50, "retention_pct": 80},
                {"time_s": 100, "pct": 100, "retention_pct": 60},
            ]), ("--duration", "120")),
            # Mixed JSON x keys across objects
            (json.dumps([
                {"time_s": 0, "retention_pct": 100},
                {"pct": 50, "retention_pct": 80},
                {"time_s": 100, "retention_pct": 60},
            ]), ("--duration", "120")),
            # Mismatched columnar JSON array lengths
            (json.dumps({"time_s": [0, 50], "retention_pct": [100, 80, 60]}), ("--duration", "120")),
            # Ambiguous headerless 0..100 x-axis without --duration
            ("0,100\n50,80\n100,60\n", ()),
            # Ambiguous unitless y-axis in 0..2.5
            ("time_s,retention\n0,1.4\n5,1.2\n10,0.9\n", ()),
            ("time_s,retention\n0,0.15\n5,0.10\n10,0.05\n", ()),
        ]
        for payload, args in cases:
            proc = _run_retention(payload, *args)
            self.assertEqual(proc.returncode, 2, f"Expected rc=2 for {payload!r} args={args!r}, got {proc.returncode}: {proc.stdout}")
            self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
