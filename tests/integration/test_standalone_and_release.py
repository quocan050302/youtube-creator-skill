# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Integration & security tests: isolated single-file CLI execution and reproducible ZIP packaging."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "youtube-creator-skill" / "scripts"
TOOLS_DIR = REPO_ROOT / "tools"


class TestIsolatedStandaloneScripts(unittest.TestCase):
    """Simulate Agensi isolated temp-file execution: each script copied alone into an empty temp dir."""

    def _run_isolated(self, script_name: str, args: list[str], stdin_text: str | None = None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="yt_iso_") as td:
            iso_script = Path(td) / script_name
            shutil.copyfile(SCRIPTS_DIR / script_name, iso_script)
            return subprocess.run(
                [sys.executable, str(iso_script), *args],
                cwd=td,
                input=stdin_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

    def test_all_seven_scripts_run_isolated_via_stdin(self) -> None:
        # 1. hookscore.py
        p1 = self._run_isolated("hookscore.py", ["--shorts-story", "-"], "Copper isn't magnetic, yet it stops a falling magnet.\n")
        self.assertEqual(p1.returncode, 0, p1.stderr)
        self.assertEqual(json.loads(p1.stdout)["formulas_count"], 21)

        # 2. title_linter.py
        p2 = self._run_isolated("title_linter.py", ["--format", "SHORT", "--thumb", "NOT MAGNETIC", "-"], "Why Copper Stops a Falling Magnet\n")
        self.assertEqual(p2.returncode, 0, p2.stderr)
        self.assertEqual(json.loads(p2.stdout)["count_evaluated"], 1)

        # 3. outlier_analyzer.py
        outlier_json = json.dumps([
            {"channel": "C", "video_id": "v0", "title": "Why 90% fail", "format": "SHORT", "published_at": "2026-11-10", "views": 500},
            {"channel": "C", "video_id": "v1", "title": "P1", "format": "SHORT", "published_at": "2026-11-11", "views": 50},
            {"channel": "C", "video_id": "v2", "title": "P2", "format": "SHORT", "published_at": "2026-11-12", "views": 100},
            {"channel": "C", "video_id": "v3", "title": "P3", "format": "SHORT", "published_at": "2026-11-13", "views": 100},
            {"channel": "C", "video_id": "v4", "title": "P4", "format": "SHORT", "published_at": "2026-11-14", "views": 150},
            {"channel": "C", "video_id": "v5", "title": "P5", "format": "SHORT", "published_at": "2026-11-15", "views": 200},
        ])
        p3 = self._run_isolated("outlier_analyzer.py", ["--as-of", "2026-11-25", "--min", "2.0", "-"], outlier_json)
        self.assertEqual(p3.returncode, 0, p3.stderr)
        self.assertAlmostEqual(json.loads(p3.stdout)["outliers"][0]["outlier_ratio"], 5.0)

        # 4. retention.py
        ret_csv = "seconds,retention\n0,100\n3,80\n15,75\n30,70\n"
        p4 = self._run_isolated("retention.py", ["--format", "SHORT", "--duration", "30", "-"], ret_csv)
        self.assertEqual(p4.returncode, 0, p4.stderr)
        self.assertAlmostEqual(json.loads(p4.stdout)["early_window_change"]["windows"][0]["delta_pp"], -20.0)

        # 5. transcript_analyzer.py
        srt = "1\n00:00:00,000 --> 00:00:02,000\nHello world\n\n2\n00:00:04,000 --> 00:00:06,000\nNext line\n"
        p5 = self._run_isolated("transcript_analyzer.py", ["--floor", "0.45", "-"], srt)
        self.assertEqual(p5.returncode, 0, p5.stderr)
        self.assertEqual(json.loads(p5.stdout)["candidate_count"], 1)

        # 6. chapters.py
        ch_txt = "00:00 Intro\n00:25 Demo\n01:05 Mechanism\n"
        p6 = self._run_isolated("chapters.py", ["--validate", "--duration", "120", "-"], ch_txt)
        self.assertEqual(p6.returncode, 0, p6.stderr)
        self.assertTrue(json.loads(p6.stdout)["valid"])

        # 7. validate_output.py
        min_pack = json.dumps({
            "schema_version": "1.0.0", "pack_id": "p1", "created_at_utc": "2026-11-27T00:00:00Z",
            "mode": "TITLE_PACKAGE", "format": "SHORT", "language": "en-US", "audience_market": "US",
            "inputs": [], "capabilities": {"used": ["TEXT_ONLY"], "unavailable": []},
            "assumptions": [], "limitations": [], "evidence": [],
            "recommendation": {"action": "Pick title 1", "rationale": "Clear gap", "evidence_ids": [], "confidence": "MEDIUM"},
            "quality": {"checks": ["tt01"], "status": "READY_FOR_CREATOR_REVIEW", "unresolved": []}, "files": []
        })
        p7 = self._run_isolated("validate_output.py", ["-"], min_pack)
        self.assertEqual(p7.returncode, 0, p7.stderr)
        self.assertTrue(json.loads(p7.stdout)["valid"])

    def test_oversized_input_rejected_exit_code_2(self) -> None:
        p = self._run_isolated("hookscore.py", ["--max-bytes", "32", "-"], "x" * 100)
        self.assertEqual(p.returncode, 2)
        self.assertIn("Invalid input", p.stderr)


class TestReproducibleReleaseAndOfflineInstall(unittest.TestCase):
    def test_build_release_reproducible_and_offline_extract_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="yt_rel_test_") as td:
            out_dir = Path(td) / "dist"
            proc = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "build_release.py"), "--version", "1.0.0-rc.1", "--out-dir", str(out_dir), "--verify"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            manifest = json.loads(proc.stdout)
            self.assertTrue(manifest["reproducible_verified"])
            self.assertTrue(manifest["agensi_extraction_verified"]["verified"])

            uni_zip = out_dir / "youtube-creator-skill-universal-v1.0.0-rc.1.zip"
            agensi_zip = out_dir / "youtube-creator-skill-agensi-v1.0.0-rc.1.zip"
            self.assertTrue(uni_zip.is_file())
            self.assertTrue(agensi_zip.is_file())

            # Verify Universal ZIP contents and offline install from extracted ZIP
            with tempfile.TemporaryDirectory(prefix="yt_install_smoke_") as inst_dir:
                with zipfile.ZipFile(uni_zip, "r") as zf:
                    names = zf.namelist()
                    self.assertIn("START_HERE.md", names)
                    self.assertIn("UNIVERSAL_PROMPT.md", names)
                    self.assertIn("LICENSE", names)
                    self.assertIn("THIRD_PARTY_NOTICES.md", names)
                    # No nested zips or forbidden files
                    self.assertFalse(any(n.endswith(".zip") or ".git/" in n or "__pycache__" in n for n in names))
                    # Exact prompt parity between ZIP and standalone file
                    zip_prompt_hash = hashlib.sha256(zf.read("UNIVERSAL_PROMPT.md")).hexdigest()
                    disk_prompt_hash = hashlib.sha256((out_dir / "UNIVERSAL_PROMPT.md").read_bytes()).hexdigest()
                    self.assertEqual(zip_prompt_hash, disk_prompt_hash)
                    zf.extractall(inst_dir)

                installed_skill = Path(inst_dir) / "youtube-creator-skill"
                val = subprocess.run(
                    [sys.executable, str(TOOLS_DIR / "validate_skill.py"), str(installed_skill)],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(val.returncode, 0, val.stdout + val.stderr)


if __name__ == "__main__":
    unittest.main()
