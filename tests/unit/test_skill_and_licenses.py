# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Unit tests for canonical SKILL.md validation, 21-formula parity, and MIT license audit."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "youtube-creator-skill"
SCRIPTS_DIR = SKILL_DIR / "scripts"
TOOLS_DIR = REPO_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))
import audit_licenses  # noqa: E402
import hookscore  # noqa: E402
import outlier_analyzer  # noqa: E402
import validate_skill  # noqa: E402


class TestSkillSpecAndLicenses(unittest.TestCase):
    def test_canonical_skill_passes_validation(self) -> None:
        rep = validate_skill.validate_skill_dir(SKILL_DIR)
        self.assertTrue(rep["valid"], f"Skill validation failed: {rep['errors']}")
        self.assertEqual(rep["frontmatter"]["name"], "youtube-creator-skill")
        self.assertLessEqual(rep["line_count"], 250)
        self.assertLessEqual(rep["approx_tokens"], 5000)

    def test_invalid_frontmatter_cases_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad-skill"
            bad.mkdir()
            (bad / "SKILL.md").write_text("---\nname: Bad_Name\ndescription: ''\n---\nBody\n", encoding="utf-8")
            rep = validate_skill.validate_skill_dir(bad)
            self.assertFalse(rep["valid"])
            self.assertTrue(any("kebab-case" in e or "match directory" in e for e in rep["errors"]))

        with tempfile.TemporaryDirectory() as td:
            dup = Path(td) / "dup-skill"
            (dup / "nested").mkdir(parents=True)
            fm = "---\nname: dup-skill\ndescription: Valid desc.\n---\nSee `references/missing.md`.\n"
            (dup / "SKILL.md").write_text(fm, encoding="utf-8")
            (dup / "nested" / "SKILL.md").write_text(fm, encoding="utf-8")
            rep = validate_skill.validate_skill_dir(dup)
            self.assertFalse(rep["valid"])
            self.assertTrue(any("Expected exactly 1 canonical SKILL.md" in e for e in rep["errors"]))
            self.assertTrue(any("Broken reference" in e for e in rep["errors"]))

    def test_hooks_json_exact_21_formula_parity(self) -> None:
        assets_hooks = json.loads((SKILL_DIR / "assets" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(len(assets_hooks), 21)
        expected = [{"id": h["id"], "name": h["name"], "match": h["match"]} for h in assets_hooks]
        self.assertEqual(hookscore.EMBEDDED_FORMULAS, expected)
        self.assertEqual(outlier_analyzer.EMBEDDED_FORMULAS, expected)

    def test_license_audit_passes_and_catches_tampering(self) -> None:
        rep = audit_licenses.run_license_audit(REPO_ROOT)
        self.assertTrue(rep["valid"], f"License audit failed: {rep['errors']}")

        # Verify tampering with upstream notice triggers failure
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "repo"
            for sub in ["LICENSES", "docs", "skills/youtube-creator-skill/LICENSES", "skills/youtube-creator-skill/scripts"]:
                (fake / sub).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / "LICENSE", fake / "LICENSE")
            shutil.copyfile(REPO_ROOT / "THIRD_PARTY_NOTICES.md", fake / "THIRD_PARTY_NOTICES.md")
            shutil.copyfile(REPO_ROOT / "docs" / "provenance.json", fake / "docs" / "provenance.json")
            (fake / "LICENSES" / "mromidev-claude-animated-shorts-MIT.txt").write_text("TAMPERED", encoding="utf-8")
            (fake / "LICENSES" / "jakeschincariol-youtube-agent-skill-MIT.txt").write_text("TAMPERED", encoding="utf-8")
            bad_rep = audit_licenses.run_license_audit(fake)
            self.assertFalse(bad_rep["valid"])
            self.assertTrue(any("Byte parity mismatch" in e for e in bad_rep["errors"]))


if __name__ == "__main__":
    unittest.main()
