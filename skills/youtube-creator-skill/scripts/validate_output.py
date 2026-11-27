#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Original implementation Copyright (c) 2026 quocan050302
"""Standalone Creator Action Pack structural & parity validator (JSON stdout).

Implements a deterministic stdlib subset validator for creator-pack.json v1.0.0
plus cross-file checks when --pack-dir is supplied. Does NOT claim full JSON
Schema Draft 2020-12 conformance or semantic/editorial PASS.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 10 * 1024 * 1024
SCHEMA_VERSION = "1.0.0"
VALID_MODES = {
    "GENERATE", "AUDIT_SCRIPT", "CHANNEL_AUDIT", "COMPETITOR_RESEARCH",
    "NICHE_DISCOVERY", "TOPIC_RESEARCH", "TITLE_PACKAGE", "HOOK_LAB",
    "THUMBNAIL_LAB", "EDIT_REVIEW", "ANALYTICS_DIAGNOSIS", "CONTENT_PLAN",
    "REPURPOSE", "SEO", "COMMENTS", "CHAPTERS", "IMPROVE",
}
VALID_FORMATS = {"SHORT", "LONG", "MIXED"}
VALID_EVIDENCE_STATUS = {"VERIFIED_FACT", "SUPPLIED_FACT", "INFERENCE", "FICTIONAL_OR_DEMO", "UNVERIFIED"}
VALID_QUALITY_STATUS = {"DRAFT", "READY_FOR_CREATOR_REVIEW", "BLOCKED_MISSING_EVIDENCE"}
VALID_CONFIDENCE = {"LOW", "MEDIUM", "HIGH"}
VALID_TIMING_BASIS = {"ESTIMATED_WPM", "MEASURED_AUDIO", "NOT_APPLICABLE"}
STAGE_LABEL_RE = re.compile(r"(\[ON SCREEN|\[BEAT\s*\d|\[VISUAL|\[SFX|^#{1,3}\s)", re.I | re.M)
REQUIRED_TOP_KEYS = [
    "schema_version", "pack_id", "created_at_utc", "mode", "format",
    "language", "audience_market", "inputs", "capabilities", "assumptions",
    "limitations", "evidence", "recommendation", "quality", "files",
]


def _has_non_finite(obj: Any, path: str = "$") -> list[str]:
    errs: list[str] = []
    if isinstance(obj, float):
        if not math.isfinite(obj):
            errs.append(f"{path}: non-finite number ({obj}).")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            errs.extend(_has_non_finite(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            errs.extend(_has_non_finite(item, f"{path}[{idx}]"))
    return errs


def _is_safe_rel_path(p_str: str) -> bool:
    if not p_str or p_str.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", p_str):
        return False
    parts = re.split(r"[\\/]+", p_str)
    return ".." not in parts and all(part != "" for part in parts)


def check_evidence_refs(pack: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ev_list = pack.get("evidence")
    if not isinstance(ev_list, list):
        return ["evidence must be an array."], warnings

    ev_ids: set[str] = set()
    has_unverified = False
    for idx, ev in enumerate(ev_list):
        if not isinstance(ev, dict):
            errors.append(f"evidence[{idx}] must be an object.")
            continue
        eid = ev.get("id")
        if not isinstance(eid, str) or not eid.strip():
            errors.append(f"evidence[{idx}].id must be a non-empty string.")
            continue
        if eid in ev_ids:
            errors.append(f"Duplicate evidence id: {eid}")
        ev_ids.add(eid)
        st = ev.get("status")
        if st not in VALID_EVIDENCE_STATUS:
            errors.append(f"evidence[{idx}].status invalid: {st}")
        if st == "UNVERIFIED":
            has_unverified = True
        src = ev.get("url_or_user_input")
        if not isinstance(src, str) or not src.strip():
            errors.append(f"evidence[{idx}].url_or_user_input must be non-empty.")

    rec = pack.get("recommendation")
    if isinstance(rec, dict):
        for ref in rec.get("evidence_ids", []):
            if ref not in ev_ids:
                errors.append(f"recommendation.evidence_ids references missing evidence id: {ref}")

    for idx, beat in enumerate(pack.get("storyboard") or []):
        if isinstance(beat, dict):
            for ref in beat.get("evidence_ids", []):
                if ref not in ev_ids:
                    errors.append(f"storyboard[{idx}].evidence_ids references missing evidence id: {ref}")

    q = pack.get("quality") or {}
    if isinstance(q, dict):
        if q.get("status") == "READY_FOR_CREATOR_REVIEW" and (has_unverified or q.get("unresolved")):
            errors.append("quality.status cannot be READY_FOR_CREATOR_REVIEW while unverified evidence or unresolved items exist.")

    return errors, warnings


def check_duration_bounds(pack: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    script = pack.get("script")
    storyboard = pack.get("storyboard") or []

    script_dur: float | None = None
    if isinstance(script, dict) and script.get("text"):
        wc = script.get("word_count")
        wpm = script.get("wpm_basis")
        dur = script.get("duration_estimate_s")
        tbasis = script.get("timing_basis")
        if tbasis not in VALID_TIMING_BASIS:
            errors.append(f"script.timing_basis invalid: {tbasis}")
        if wc is not None and (not isinstance(wc, int) or wc < 0):
            errors.append(f"script.word_count must be integer >= 0 (got {wc}).")
        if wpm is not None and (not isinstance(wpm, (int, float)) or wpm <= 0):
            errors.append(f"script.wpm_basis must be > 0 (got {wpm}).")
        if dur is not None:
            if not isinstance(dur, (int, float)) or dur <= 0:
                errors.append(f"script.duration_estimate_s must be > 0 (got {dur}).")
            else:
                script_dur = float(dur)
                if isinstance(wc, int) and isinstance(wpm, (int, float)) and wpm > 0 and wc > 0:
                    expected = wc / (float(wpm) / 60.0)
                    if abs(script_dur - expected) > max(8.0, expected * 0.35):
                        warnings.append(
                            f"script.duration_estimate_s ({script_dur}s) differs notably from word_count/wpm ({expected:.1f}s)."
                        )

    if isinstance(storyboard, list) and storyboard:
        seen_bids: set[str] = set()
        prev_end = 0.0
        for idx, b in enumerate(storyboard):
            if not isinstance(b, dict):
                errors.append(f"storyboard[{idx}] must be an object.")
                continue
            bid = b.get("id")
            if not isinstance(bid, str) or not bid.strip():
                errors.append(f"storyboard[{idx}].id missing.")
            elif bid in seen_bids:
                errors.append(f"Duplicate storyboard beat id: {bid}")
            else:
                seen_bids.add(bid)

            st, en = b.get("start_s"), b.get("end_s")
            if not isinstance(st, (int, float)) or not isinstance(en, (int, float)):
                errors.append(f"storyboard[{idx}] start_s/end_s must be numbers.")
                continue
            if st < 0 or en < 0 or en <= st:
                errors.append(f"storyboard[{idx}] invalid interval [{st}, {en}].")
            if idx > 0 and st < prev_end - 1e-6:
                errors.append(f"storyboard[{idx}] overlaps previous beat ({st} < {prev_end}).")
            prev_end = max(prev_end, float(en))

        if script_dur is not None and prev_end > 0:
            if abs(prev_end - script_dur) > max(6.0, script_dur * 0.25):
                errors.append(
                    f"Storyboard end ({prev_end:.1f}s) inconsistent with script.duration_estimate_s ({script_dur:.1f}s)."
                )

    return errors, warnings


def check_cross_fields(pack: dict[str, Any], pack_dir: Path | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    mode = pack.get("mode")
    script = pack.get("script")
    title = pack.get("title")

    if mode == "GENERATE":
        if not isinstance(title, dict) or not title.get("selected"):
            errors.append("GENERATE mode requires title.selected.")
        if not isinstance(script, dict) or not script.get("text"):
            errors.append("GENERATE mode requires script.text.")

    if isinstance(script, dict) and isinstance(script.get("text"), str) and script["text"].strip():
        if STAGE_LABEL_RE.search(script["text"]):
            errors.append("script.text contains stage/Markdown labels ([ON SCREEN]/[BEAT]/headings); clean voice text only.")

    # Check duplicate input IDs
    seen_inputs: set[str] = set()
    for idx, inp in enumerate(pack.get("inputs") or []):
        if isinstance(inp, dict):
            iid = inp.get("id")
            if not isinstance(iid, str) or not iid.strip():
                errors.append(f"inputs[{idx}].id missing.")
            elif iid in seen_inputs:
                errors.append(f"Duplicate input id: {iid}")
            else:
                seen_inputs.add(iid)

    files = pack.get("files") or []
    if not isinstance(files, list):
        errors.append("files must be an array.")
        files = []
    for f in files:
        if not isinstance(f, str) or not _is_safe_rel_path(f):
            errors.append(f"Unsafe or invalid file reference in files[]: {f!r}")

    if pack_dir is not None:
        for f in files:
            if isinstance(f, str) and _is_safe_rel_path(f):
                fp = pack_dir / f
                if not fp.is_file():
                    errors.append(f"Listed file missing in pack_dir: {f}")

        script_file = pack_dir / "SCRIPT.txt"
        if script_file.is_file() and isinstance(script, dict) and isinstance(script.get("text"), str):
            disk_txt = script_file.read_text(encoding="utf-8-sig").strip()
            if STAGE_LABEL_RE.search(disk_txt):
                errors.append("SCRIPT.txt contains forbidden stage or Markdown labels.")
            if disk_txt != script["text"].strip():
                errors.append("SCRIPT.txt text does not match creator-pack.json -> script.text.")

        title_file = pack_dir / "TITLE_HOOKS.md"
        if title_file.is_file() and isinstance(title, dict) and title.get("selected"):
            th_text = title_file.read_text(encoding="utf-8-sig")
            if title["selected"] not in th_text:
                errors.append("Selected title in creator-pack.json not found in TITLE_HOOKS.md.")

        # Verify CSV formula injection safety on any listed CSV file
        for f in files:
            if isinstance(f, str) and f.lower().endswith(".csv") and _is_safe_rel_path(f):
                cp = pack_dir / f
                if cp.is_file():
                    with cp.open("r", encoding="utf-8-sig", newline="") as fh:
                        for r_idx, row in enumerate(csv.reader(fh)):
                            for c_idx, cell in enumerate(row):
                                s = cell.lstrip(" ")
                                if s and s[0] in ("=", "+", "@"):
                                    errors.append(f"{f} row {r_idx + 1} col {c_idx + 1} starts with unsafe formula char '{s[0]}'.")
                                elif s.startswith("-") and not re.match(r"^-\d+(\.\d+)?$", s):
                                    errors.append(f"{f} row {r_idx + 1} col {c_idx + 1} starts with unescaped '-' text formula risk.")

    return errors, warnings


def validate_pack(pack: Any, pack_dir: Path | None = None, expected_plan_rows: int | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(pack, dict):
        return {
            "tool": "validate_output.py",
            "validator_scope": "custom_stdlib_subset_validator_v1.0.0",
            "valid": False,
            "errors": ["Root JSON must be an object."],
            "warnings": [],
        }

    errors.extend(_has_non_finite(pack))
    for k in REQUIRED_TOP_KEYS:
        if k not in pack:
            errors.append(f"Missing required top-level key: {k}")

    if pack.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be '{SCHEMA_VERSION}' (got {pack.get('schema_version')!r}).")
    if pack.get("mode") not in VALID_MODES:
        errors.append(f"Invalid mode: {pack.get('mode')!r}")
    if pack.get("format") not in VALID_FORMATS:
        errors.append(f"Invalid format: {pack.get('format')!r}")

    rec = pack.get("recommendation")
    if isinstance(rec, dict):
        if rec.get("confidence") not in VALID_CONFIDENCE:
            errors.append(f"recommendation.confidence invalid: {rec.get('confidence')!r}")
        if not rec.get("action") or not rec.get("rationale"):
            errors.append("recommendation.action and recommendation.rationale must be non-empty.")
    else:
        errors.append("recommendation must be an object.")

    qual = pack.get("quality")
    if isinstance(qual, dict):
        if qual.get("status") not in VALID_QUALITY_STATUS:
            errors.append(f"quality.status invalid (never use PUBLISH_READY): {qual.get('status')!r}")
    else:
        errors.append("quality must be an object.")

    caps = pack.get("capabilities")
    if not isinstance(caps, dict) or not isinstance(caps.get("used"), list) or not isinstance(caps.get("unavailable"), list):
        errors.append("capabilities must contain 'used' and 'unavailable' arrays.")

    if expected_plan_rows is not None:
        cp = pack.get("content_plan") or []
        if not isinstance(cp, list) or len(cp) != expected_plan_rows:
            errors.append(f"content_plan row count mismatch: expected {expected_plan_rows}, got {len(cp) if isinstance(cp, list) else 'non-list'}.")

    e1, w1 = check_evidence_refs(pack)
    e2, w2 = check_duration_bounds(pack)
    e3, w3 = check_cross_fields(pack, pack_dir=pack_dir)
    errors.extend(e1 + e2 + e3)
    warnings.extend(w1 + w2 + w3)

    return {
        "tool": "validate_output.py",
        "validator_scope": "custom_stdlib_subset_validator_v1.0.0",
        "note": "Structural, numeric, evidence-link, and cross-file parity check only; NOT a substitute for editorial/human review.",
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def _read_bounded(path_or_dash: str, max_bytes: int) -> str:
    if path_or_dash == "-":
        raw = sys.stdin.buffer.read(max_bytes + 1)
    else:
        p = Path(path_or_dash)
        if not p.is_file():
            raise FileNotFoundError(f"Input file not found: {path_or_dash}")
        if p.stat().st_size > max_bytes:
            raise ValueError(f"Input exceeds max allowed bytes ({max_bytes}).")
        raw = p.read_bytes()
    if len(raw) > max_bytes:
        raise ValueError(f"Input exceeds max allowed bytes ({max_bytes}).")
    return raw.decode("utf-8-sig", errors="replace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Standalone Creator Action Pack structural & cross-file validator (JSON stdout)."
    )
    parser.add_argument("input", nargs="?", default="-", help="Path to creator-pack.json, or '-' for stdin.")
    parser.add_argument("--pack-dir", default=None, help="Optional directory containing sibling pack files for cross-file verification.")
    parser.add_argument("--expected-plan-rows", type=int, default=None, help="Optional required row count for content_plan[].")
    parser.add_argument("--json", action="store_true", help="Output JSON (default behavior).")
    parser.add_argument("--max-bytes", type=int, default=MAX_INPUT_BYTES, help="Max input size in bytes.")
    args = parser.parse_args(argv)

    if args.max_bytes <= 0:
        print("Error: --max-bytes must be > 0.", file=sys.stderr)
        return 2

    try:
        if args.input == "-" and sys.stdin.isatty():
            print("Error: Provide a creator-pack.json path or pipe stdin.", file=sys.stderr)
            return 2
        raw = _read_bounded(args.input, args.max_bytes)
        data = json.loads(raw, parse_constant=lambda c: float(c))
        pdir = Path(args.pack_dir) if args.pack_dir else (Path(args.input).parent if args.input != "-" and Path(args.input).is_file() else None)
        payload = validate_pack(data, pack_dir=pdir, expected_plan_rows=args.expected_plan_rows)
    except (ValueError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
