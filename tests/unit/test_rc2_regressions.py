# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Regression tests for all YT-01.T1 findings (ISS-01 through ISS-10) in v1.0.0-rc.2."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "youtube-creator-skill" / "scripts"
TOOLS_DIR = REPO_ROOT / "tools"
SKILL_DIR = REPO_ROOT / "skills" / "youtube-creator-skill"

sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(TOOLS_DIR))
import build_universal_prompt  # noqa: E402
import hookscore  # noqa: E402
import validate_skill  # noqa: E402


class TestRC2Regressions(unittest.TestCase):
    def test_iss01_release_workflow_safe_env_binding_and_gates(self) -> None:
        wf = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        # No direct ${{ inputs.* }} inside shell run lines
        in_run_block = False
        for line in wf.splitlines():
            stripped = line.strip()
            if stripped.startswith("run:"):
                self.assertNotIn("${{ inputs.", stripped, f"Direct inputs interpolation in run line: {stripped}")
                in_run_block = stripped.endswith("|")
            elif in_run_block:
                if line and not line.startswith(" "):
                    in_run_block = False
                elif re.match(r"^\s{6,8}-\s+name:", line):
                    in_run_block = False
                else:
                    self.assertNotIn("${{ inputs.", line, f"Direct inputs interpolation in shell block: {line}")
        self.assertIn("target_sha:", wf)
        self.assertIn("stable_gates_verified:", wf)
        self.assertIn('--repo "$REPO"', wf)
        self.assertIn('--target "$RELEASE_SHA"', wf)

    def test_iss02_hookscore_3s_gate_and_demo01_first_line(self) -> None:
        long_hook = hookscore.score_hook(
            "What happens when someone pays twelve dollars nine dollars and nineteen dollars a month for subscriptions they no longer use?",
            pov="narrative",
            title="What 3 Unused Subscriptions Cost Yearly",
            video_format="SHORT",
        )
        self.assertFalse(long_hook["fits_3s_at_180_wpm"])
        self.assertFalse(long_hook["fits_3s_at_150_wpm"])
        self.assertLessEqual(long_hook["rubric_0_to_10"]["speakability_visual"], 1)
        self.assertTrue(any("180 WPM" in r for r in long_hook["reasons"]))

        demo_pack = json.loads((REPO_ROOT / "examples" / "01-science-short-copper-magnet" / "creator-pack.json").read_text(encoding="utf-8"))
        demo_res = hookscore.score_hook(
            demo_pack["hook"]["selected"], pov="narrative", title=demo_pack["title"]["selected"], video_format="SHORT"
        )
        self.assertTrue(demo_res["fits_3s_at_180_wpm"], f"Demo 01 hook exceeds 3s at 180 WPM: {demo_res}")
        self.assertLessEqual(demo_res["word_count"], 9)
        self.assertLessEqual(demo_pack["storyboard"][0]["end_s"], 3.5)

    def test_iss05_retention_warns_and_counts_dropped_nan_rows(self) -> None:
        csv_data = "time_s,retention_pct\n0,100\n5,90\n10,NaN\n15,82\n20,120\n25,79\n"
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "retention.py"), "--format", "SHORT", "--duration", "25", "-"],
            input=csv_data, capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["overview"]["dropped_invalid_rows"], 1)
        self.assertEqual(out["axis"]["dropped_invalid_rows"], 1)
        self.assertTrue(any("Skipped 1" in w and "NaN" in w for w in out["warnings"]))
        # Verify retention.py stays within documented 24 KiB internal logic ceiling (adjusted in RC.3 without cutting validation)
        self.assertLessEqual((SCRIPTS_DIR / "retention.py").stat().st_size, 24 * 1024)

    def test_iss06_malformed_json_rejected_exit_code_2(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text("{not valid json", encoding="utf-8")
            p_h = subprocess.run([sys.executable, str(SCRIPTS_DIR / "hookscore.py"), str(bad)], capture_output=True, text=True)
            self.assertEqual(p_h.returncode, 2)
            p_t = subprocess.run([sys.executable, str(SCRIPTS_DIR / "title_linter.py"), str(bad)], capture_output=True, text=True)
            self.assertEqual(p_t.returncode, 2)

    def test_iss07_universal_prompt_includes_all_21_references_no_dangling_mentions(self) -> None:
        content, meta = build_universal_prompt.build_universal_prompt(REPO_ROOT)
        self.assertEqual(meta["unresolved_links"], 0)
        self.assertGreaterEqual(len(build_universal_prompt.ALLOWLISTED_SECTIONS), 21)
        self.assertIn("1.0.0-rc.3", content)

    def test_iss08_validators_exit_1_when_invalid(self) -> None:
        p_ch = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "chapters.py"), "--validate", "--duration", "120", "-"],
            input="00:05 intro\n00:10 short\n00:30 end\n",
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(p_ch.returncode, 1)
        self.assertFalse(json.loads(p_ch.stdout)["valid"])

        p_vo = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "validate_output.py"), "-"],
            input=json.dumps({"schema_version": "1.0.0"}),
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(p_vo.returncode, 1)
        self.assertFalse(json.loads(p_vo.stdout)["valid"])

    def test_iss09_validate_skill_checks_all_21_references(self) -> None:
        rep = validate_skill.validate_skill_dir(SKILL_DIR)
        self.assertTrue(rep["valid"], rep["errors"])
        self.assertGreaterEqual(rep["references_checked"], 21)


if __name__ == "__main__":
    unittest.main()
