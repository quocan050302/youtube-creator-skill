#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Adapted from: https://github.com/jakeschincariol/youtube-agent-skill
#   Pinned commit: a2feb2104981a375ffd4f87ee04f4f5344ac43c6
#   Source path:   skills/yt-edit/deadair.py
#   Upstream Copyright (c) 2026 Jake Schincariol
# Modifications Copyright (c) 2026 quocan050302:
#   - Strict SRT/VTT/Whisper-JSON validation (monotonicity, invalid spans, overlaps)
#   - Explicit evidence tagging: transcript gap != proven audio silence
#   - Untimed plain-text mode returns qualitative summary without invented timestamps
#   - Optional CSV export with formula-injection protection
"""Standalone transcript-to-edit decision analyzer (JSON stdout)."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 10 * 1024 * 1024
FILLER_ONLY = re.compile(
    r"^[\s,.\-!?]*((um+|uh+|er+|ah+|so|okay|ok|right|yeah|like|anyway|basically|"
    r"actually|you know|i mean|let me see|hold on)[\s,.\-!?]*)+$",
    re.I,
)
LIMITATION_NOTE = (
    "All candidates are TRANSCRIPT_IMPLIED only — NOT measured audio silence or inspected video frames. "
    "A gap between subtitle cues may contain intentional B-roll, visual demos, or dramatic beats. "
    "This tool never edits media files."
)


def _parse_ts(ts: str) -> float:
    s = ts.strip().replace(",", ".")
    parts = s.split(":")
    if len(parts) == 3:
        val = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        val = int(parts[0]) * 60 + float(parts[1])
    else:
        raise ValueError(f"Invalid timestamp syntax: {ts}")
    if not math.isfinite(val) or val < 0:
        raise ValueError(f"Non-finite or negative timestamp: {ts}")
    return val


def parse_srt_vtt_or_json(raw_text: str, hint: str = "") -> tuple[list[dict[str, Any]], str]:
    stripped = raw_text.strip()
    if not stripped:
        raise ValueError("Transcript input is empty.")

    if stripped.startswith("{") or stripped.startswith("[") or hint.lower().endswith(".json"):
        data = json.loads(stripped)
        segs = data.get("segments", data.get("words", data if isinstance(data, list) else None))
        if not isinstance(segs, list):
            raise ValueError("JSON transcript must be a list or contain 'segments'/'words'.")
        out: list[dict[str, Any]] = []
        for idx, item in enumerate(segs):
            if not isinstance(item, dict):
                raise ValueError(f"Segment {idx} must be an object.")
            st = float(item["start"])
            en = float(item["end"])
            txt = str(item.get("text") or item.get("word") or "").strip()
            out.append({"index": idx, "start": st, "end": en, "text": txt})
        return out, "json"

    is_vtt = stripped.upper().startswith("WEBVTT") or hint.lower().endswith(".vtt")
    cues: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None
    skip_block = False
    for line in raw_text.splitlines():
        ls = line.strip()
        if ls.upper().startswith(("WEBVTT", "NOTE", "STYLE", "REGION")):
            skip_block = ls.upper().startswith(("NOTE", "STYLE", "REGION"))
            cur = None
            continue
        if not ls:
            skip_block = False
            cur = None
            continue
        if skip_block:
            continue
        m = re.match(r"(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", ls)
        if m:
            st = _parse_ts(m.group(1))
            en = _parse_ts(m.group(2))
            cur = {"index": len(cues), "start": st, "end": en, "lines": []}
            cues.append(cur)
        elif cur is not None:
            if not cur["lines"] and ls.isdigit():
                continue
            cur["lines"].append(ls)

    parsed: list[dict[str, Any]] = []
    for c in cues:
        txt = " ".join(c["lines"]).strip()
        parsed.append({"index": c["index"], "start": c["start"], "end": c["end"], "text": txt})
    return parsed, ("vtt" if is_vtt else "srt")


def validate_segments(segments: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    if not segments:
        raise ValueError("No timestamped segments parsed from input.")

    warnings: list[str] = []
    for s in segments:
        st, en = s["start"], s["end"]
        if not (math.isfinite(st) and math.isfinite(en)):
            raise ValueError(f"Segment {s['index']} has non-finite timestamps.")
        if st < 0 or en < 0:
            raise ValueError(f"Segment {s['index']} has negative timestamp.")
        if en < st:
            raise ValueError(f"Segment {s['index']} has end < start ({en} < {st}).")

    unsorted = any(segments[i]["start"] < segments[i - 1]["start"] for i in range(1, len(segments)))
    if unsorted:
        warnings.append("Segments were out of chronological order; sorted ascending by start timestamp.")
        segments = sorted(segments, key=lambda s: (s["start"], s["end"], s["index"]))

    overlaps = 0
    for i in range(1, len(segments)):
        if segments[i]["start"] < segments[i - 1]["end"] - 1e-6:
            overlaps += 1
    if overlaps:
        warnings.append(f"Detected {overlaps} overlapping cue interval(s); gaps are only computed where next.start > prev.end.")

    return segments, warnings


def detect_gaps(segments: list[dict[str, Any]], floor_s: float = 0.45) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    keep = floor_s / 2.0
    for i in range(1, len(segments)):
        prev_end = segments[i - 1]["end"]
        cur_start = segments[i]["start"]
        gap = cur_start - prev_end
        if gap > floor_s:
            cut_s = round(prev_end + keep, 3)
            cut_e = round(cur_start - keep, 3)
            if cut_e > cut_s:
                gaps.append({
                    "kind": "GAP_CANDIDATE",
                    "priority": "P1" if gap >= floor_s * 2 else "P2",
                    "start_s": cut_s,
                    "end_s": cut_e,
                    "removed_s": round(cut_e - cut_s, 3),
                    "raw_gap_s": round(gap, 3),
                    "evidence_source": "TRANSCRIPT_IMPLIED",
                    "issue": f"{gap:.2f}s caption gap (> {floor_s:.2f}s floor)",
                    "recommended_fix": "Verify footage first; trim center of gap while keeping breath on both edges if truly dead air.",
                    "expected_tradeoff": "Tightens speech pacing; do NOT cut if silent visual demo/action occurs here.",
                })
    return gaps


def _norm_words(text: str) -> list[str]:
    return re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)


def find_filler_candidates(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for s in segments:
        txt = s["text"].strip()
        if txt and FILLER_ONLY.match(txt) and s["end"] > s["start"]:
            out.append({
                "kind": "FILLER_CANDIDATE",
                "priority": "P2",
                "start_s": round(s["start"], 3),
                "end_s": round(s["end"], 3),
                "removed_s": round(s["end"] - s["start"], 3),
                "evidence_source": "TRANSCRIPT_IMPLIED",
                "issue": f'Filler-only cue: "{txt[:48]}"',
                "recommended_fix": "Review for jump-cut or B-roll cover if cutting does not clip adjacent consonants.",
                "expected_tradeoff": "Improves crispness; may create visual jump cut without B-roll or punch-in.",
            })
    return out


def make_edit_candidates(segments: list[dict[str, Any]], floor_s: float = 0.45) -> dict[str, Any]:
    gaps = detect_gaps(segments, floor_s=floor_s)
    fillers = find_filler_candidates(segments)
    restarts: list[dict[str, Any]] = []

    for i, cur in enumerate(segments):
        txt = cur["text"].strip()
        if not txt or FILLER_ONLY.match(txt):
            continue
        j = i - 1
        while j >= 0 and (not segments[j]["text"].strip() or FILLER_ONLY.match(segments[j]["text"].strip())):
            j -= 1
        if j >= 0 and segments[j]["end"] > segments[j]["start"]:
            a_words = _norm_words(segments[j]["text"])[:5]
            b_words = _norm_words(txt)[:5]
            if len(a_words) >= 3 and a_words == b_words:
                restarts.append({
                    "kind": "RESTART_CANDIDATE",
                    "priority": "P0",
                    "start_s": round(segments[j]["start"], 3),
                    "end_s": round(segments[j]["end"], 3),
                    "removed_s": round(segments[j]["end"] - segments[j]["start"], 3),
                    "evidence_source": "TRANSCRIPT_IMPLIED",
                    "issue": f'Possible false-start take repeating "{" ".join(a_words)}"',
                    "recommended_fix": "Keep the cleaner second take and drop the false start after listening to audio.",
                    "expected_tradeoff": "Eliminates noticeable stutter; verify second take actually finishes cleanly.",
                })

    candidates = sorted(gaps + fillers + restarts, key=lambda c: (c["start_s"], c["end_s"], c["kind"]))
    total_dur = max(s["end"] for s in segments)
    removed = round(sum(c["removed_s"] for c in candidates), 3)
    return {
        "duration_in_s": round(total_dur, 3),
        "cues_count": len(segments),
        "floor_s": floor_s,
        "candidate_count": len(candidates),
        "speech_gap_removed_estimate_s": removed,
        "estimated_duration_after_speech_cuts_s": round(max(0.0, total_dur - removed), 3),
        "candidates": candidates,
    }


def _sanitize_csv_cell(val: Any) -> Any:
    if isinstance(val, str):
        stripped = val.lstrip(" ")
        if stripped and stripped[0] in ("=", "+", "-", "@", "\t", "\r"):
            return "'" + val
    return val


def export_edl_csv(candidates: list[dict[str, Any]]) -> str:
    buf = io.StringIO()
    fields = ["priority", "kind", "start_s", "end_s", "removed_s", "evidence_source", "issue", "recommended_fix", "expected_tradeoff"]
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for c in candidates:
        writer.writerow({k: _sanitize_csv_cell(c.get(k, "")) for k in fields})
    return buf.getvalue()


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
        description="Standalone SRT/VTT/Whisper-JSON transcript edit analyzer (JSON stdout)."
    )
    parser.add_argument("input", nargs="?", default="-", help="Path to .srt/.vtt/.json/.txt transcript, or '-' for stdin.")
    parser.add_argument("--floor", type=float, default=0.45, help="Minimum gap seconds to flag (default 0.45).")
    parser.add_argument("--untimed", action="store_true", help="Treat input as plain untimed text (qualitative summary only).")
    parser.add_argument("--csv-out", default=None, help="Optional safe path to write formula-escaped EDIT_DECISIONS.csv.")
    parser.add_argument("--json", action="store_true", help="Output JSON (default behavior).")
    parser.add_argument("--max-bytes", type=int, default=MAX_INPUT_BYTES, help="Max input size in bytes.")
    args = parser.parse_args(argv)

    if args.max_bytes <= 0 or not math.isfinite(args.floor) or args.floor <= 0:
        print("Error: --floor and --max-bytes must be positive finite numbers.", file=sys.stderr)
        return 2

    try:
        if args.input == "-" and sys.stdin.isatty():
            print("Error: Provide a transcript path or pipe stdin.", file=sys.stderr)
            return 2
        raw_text = _read_bounded(args.input, args.max_bytes)
        if args.untimed:
            words = _norm_words(raw_text)
            payload: dict[str, Any] = {
                "tool": "transcript_analyzer.py",
                "mode": "UNTIMED_QUALITATIVE_ONLY",
                "word_count": len(words),
                "candidates": [],
                "warnings": ["No timestamps provided; cannot compute edit timecodes or dead-air gaps."],
                "limitations": LIMITATION_NOTE,
            }
        else:
            segs, fmt = parse_srt_vtt_or_json(raw_text, args.input)
            valid_segs, warnings = validate_segments(segs)
            edl = make_edit_candidates(valid_segs, floor_s=args.floor)
            payload = {
                "tool": "transcript_analyzer.py",
                "mode": "TIMESTAMPED_EDL",
                "input_format": fmt,
                **edl,
                "warnings": warnings,
                "limitations": LIMITATION_NOTE,
            }
            if args.csv_out:
                out_path = Path(args.csv_out)
                if ".." in out_path.parts:
                    raise ValueError("Path traversal ('..') is not allowed in --csv-out.")
                out_path.write_text(export_edl_csv(edl["candidates"]), encoding="utf-8")
                payload["csv_written"] = str(out_path)
    except (ValueError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
