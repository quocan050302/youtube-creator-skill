# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Unit tests for transcript_analyzer.py, chapters.py, and validate_output.py."""
from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "youtube-creator-skill" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import chapters  # noqa: E402
import transcript_analyzer  # noqa: E402
import validate_output  # noqa: E402


def _base_valid_pack() -> dict:
    return {
        "schema_version": "1.0.0",
        "pack_id": "test-pack-001",
        "created_at_utc": "2026-11-27T09:00:00Z",
        "mode": "GENERATE",
        "format": "SHORT",
        "language": "en-US",
        "audience_market": "US",
        "inputs": [{"id": "IN-01", "type": "user_prompt", "source": "chat", "scope": "topic", "observed_at": "2026-11-27"}],
        "capabilities": {"used": ["TEXT_ONLY", "CODE"], "unavailable": ["VISION"]},
        "assumptions": ["165 WPM conversational English"],
        "limitations": ["Estimated duration; no measured audio"],
        "evidence": [{
            "id": "E01",
            "url_or_user_input": "user_input",
            "claim": "Copper conducts electricity and opposes changing magnetic fields via eddy currents.",
            "source_date": "2026-11-27",
            "retrieved_at": "2026-11-27",
            "status": "SUPPLIED_FACT",
        }],
        "recommendation": {
            "action": "Open immediately on the falling magnet inside the copper tube.",
            "rationale": "Visual paradox creates immediate curiosity without intro filler.",
            "evidence_ids": ["E01"],
            "confidence": "HIGH",
        },
        "title": {"selected": "Why Copper Stops a Falling Magnet", "alternatives": [], "promise": "Explain copper magnetic braking"},
        "hook": {"selected": "Copper isn't magnetic, yet it stops a falling magnet in midair.", "alternatives": [], "heuristic_basis": "hookscore.py"},
        "first_frame": {"concept": "Magnet hovering slowly inside vertical copper pipe", "aspect_ratio": "9:16"},
        "script": {
            "text": "Copper isn't magnetic, yet it stops a falling magnet in midair. Watch it drop slowly.",
            "word_count": 15,
            "wpm_basis": 165,
            "duration_estimate_s": 6.0,
            "timing_basis": "ESTIMATED_WPM",
        },
        "storyboard": [
            {"id": "B01", "start_s": 0.0, "end_s": 3.0, "timing_basis": "ESTIMATED_WPM", "voice": "Copper isn't magnetic", "visual": "Copper tube close-up", "overlay": None, "audio": None, "evidence_ids": ["E01"]},
            {"id": "B02", "start_s": 3.0, "end_s": 6.0, "timing_basis": "ESTIMATED_WPM", "voice": "Watch it drop slowly", "visual": "Slow descent cutaway", "overlay": None, "audio": None, "evidence_ids": ["E01"]},
        ],
        "thumbnail": {"concept": "Cutaway tube with magnet", "text": "NOT MAGNETIC", "prompt": "Clean macro photo", "aspect_ratio": "9:16", "status": "CONCEPT_ONLY"},
        "upload": {"description": "Why a magnet slows down in copper.", "tags": ["copper", "magnet"], "chapters": []},
        "analytics": None,
        "content_plan": [],
        "experiment": {"hypothesis": "Visual paradox improves 0-3s hold", "metric": "stayed_to_watch_pct", "window": "7d", "controls": "same niche", "decision": "PENDING"},
        "quality": {"checks": ["tt01", "kh01"], "status": "READY_FOR_CREATOR_REVIEW", "unresolved": []},
        "files": ["SCRIPT.txt", "STORYBOARD.csv", "TITLE_HOOKS.md", "creator-pack.json"],
    }


class TestTranscriptAnalyzer(unittest.TestCase):
    def test_srt_vtt_gaps_filler_restart_and_csv_escape(self) -> None:
        vtt = (
            "WEBVTT\n\nNOTE ignore this block\n\n"
            "00:00:00.000 --> 00:00:02.000\nWe tested three budget mics today\n\n"
            "00:00:02.100 --> 00:00:02.600\num\n\n"
            "00:00:02.700 --> 00:00:05.000\nWe tested three budget mics under fifty dollars.\n\n"
            "00:00:07.500 --> 00:00:09.000\nHere is what broke first.\n"
        )
        segs, fmt = transcript_analyzer.parse_srt_vtt_or_json(vtt, "sample.vtt")
        self.assertEqual(fmt, "vtt")
        valid_segs, warns = transcript_analyzer.validate_segments(segs)
        self.assertEqual(warns, [])
        edl = transcript_analyzer.make_edit_candidates(valid_segs, floor_s=0.45)
        kinds = {c["kind"] for c in edl["candidates"]}
        self.assertEqual(kinds, {"FILLER_CANDIDATE", "RESTART_CANDIDATE", "GAP_CANDIDATE"})
        self.assertTrue(all(c["evidence_source"] == "TRANSCRIPT_IMPLIED" for c in edl["candidates"]))

        # CSV formula injection neutralization
        csv_out = transcript_analyzer.export_edl_csv([
            {"priority": "P0", "kind": "FILLER", "start_s": 1.0, "end_s": 2.0, "removed_s": 1.0,
             "evidence_source": "TRANSCRIPT_IMPLIED", "issue": "=HYPERLINK(\"http://evil\")", "recommended_fix": "+cmd", "expected_tradeoff": "@macro"}
        ])
        self.assertIn("'=HYPERLINK", csv_out)
        self.assertIn("'+cmd", csv_out)
        self.assertIn("'@macro", csv_out)

    def test_invalid_span_rejected_and_overlap_warned(self) -> None:
        with self.assertRaises(ValueError):
            transcript_analyzer.validate_segments([{"index": 0, "start": 5.0, "end": 2.0, "text": "bad"}])
        _, warns = transcript_analyzer.validate_segments([
            {"index": 0, "start": 0.0, "end": 3.0, "text": "a"},
            {"index": 1, "start": 2.5, "end": 4.0, "text": "b"},
        ])
        self.assertTrue(any("overlapping" in w for w in warns))


class TestChapters(unittest.TestCase):
    def test_valid_and_invalid_chapter_rules(self) -> None:
        ok = chapters.validate_chapters([
            {"start_s": 0, "title": "Intro"},
            {"start_s": 35, "title": "Core Mechanism"},
            {"start_s": 90, "title": "Results"},
        ], video_duration_s=140)
        self.assertTrue(ok["valid"])
        self.assertTrue(ok["formatted_block"].startswith("00:00 Intro"))

        bad_start = chapters.validate_chapters([
            {"start_s": 5, "title": "Late start"},
            {"start_s": 20, "title": "Two"},
            {"start_s": 40, "title": "Three"},
        ], video_duration_s=60)
        self.assertFalse(bad_start["valid"])

        too_short = chapters.validate_chapters([
            {"start_s": 0, "title": "Intro"},
            {"start_s": 8, "title": "Too short"},
            {"start_s": 30, "title": "End"},
        ], video_duration_s=35)
        self.assertFalse(too_short["valid"])
        self.assertGreaterEqual(len(too_short["errors"]), 2)


class TestValidateOutput(unittest.TestCase):
    def test_valid_pack_and_disk_parity(self) -> None:
        pack = _base_valid_pack()
        with tempfile.TemporaryDirectory() as td:
            pdir = Path(td)
            (pdir / "SCRIPT.txt").write_text(pack["script"]["text"] + "\n", encoding="utf-8")
            (pdir / "TITLE_HOOKS.md").write_text(f"# Titles\nSelected: {pack['title']['selected']}\n", encoding="utf-8")
            (pdir / "STORYBOARD.csv").write_text("beat_id,start_s,end_s\nB01,0.0,3.0\n", encoding="utf-8")
            (pdir / "creator-pack.json").write_text("{}", encoding="utf-8")
            res = validate_output.validate_pack(pack, pack_dir=pdir)
            self.assertTrue(res["valid"], res["errors"])

    def test_catches_dangling_evidence_stage_labels_nan_traversal_and_csv_injection(self) -> None:
        bad = _base_valid_pack()
        bad["recommendation"]["evidence_ids"] = ["MISSING_EVID"]
        bad["script"]["text"] = "[ON SCREEN: tube] Hello world"
        bad["script"]["duration_estimate_s"] = float("nan")
        bad["files"] = ["../escape.txt", "STORYBOARD.csv"]
        bad["quality"]["status"] = "PUBLISH_READY"

        with tempfile.TemporaryDirectory() as td:
            pdir = Path(td)
            (pdir / "STORYBOARD.csv").write_text("beat_id,note\nB01,=1+1\n", encoding="utf-8")
            res = validate_output.validate_pack(bad, pack_dir=pdir)
            self.assertFalse(res["valid"])
            joined = " | ".join(res["errors"])
            self.assertIn("MISSING_EVID", joined)
            self.assertIn("stage/Markdown labels", joined)
            self.assertIn("non-finite", joined)
            self.assertIn("Unsafe or invalid file reference", joined)
            self.assertIn("PUBLISH_READY", joined)
            self.assertIn("unsafe formula char", joined)


if __name__ == "__main__":
    unittest.main()
