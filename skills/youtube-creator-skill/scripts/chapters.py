#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Adapted from: https://github.com/jakeschincariol/youtube-agent-skill
#   Pinned commit: a2feb2104981a375ffd4f87ee04f4f5344ac43c6
#   Source path:   skills/yt-chapters/chapters.py
#   Upstream Copyright (c) 2026 Jake Schincariol
# Modifications Copyright (c) 2026 quocan050302:
#   - Zero sibling imports (standalone built-in SRT/VTT/JSON parser)
#   - Dedicated --validate mode for checking existing chapter lists against YouTube rules
#   - Canonical 00:00 formatting, duration bounds check, and zero fabricated timestamps
"""Standalone YouTube chapters validator & transcript boundary drafter (JSON stdout)."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 10 * 1024 * 1024
MIN_CHAPTERS = 3
MIN_CHAPTER_SECONDS = 10.0
STOP = set(
    "the a an of for to in on and or is are was were be been with this that it as at by from "
    "you your i my we our they them he she but so if then than there here what which who how "
    "when where why not no yes do does did just really very like about into over out up down "
    "can could will would should have has had get got make made go going went one two three".split()
)


def _parse_ts(ts: str) -> float:
    s = ts.strip().replace(",", ".")
    parts = s.split(":")
    if len(parts) == 3:
        h, m, sec = int(parts[0]), int(parts[1]), float(parts[2])
        if m >= 60 or sec >= 60 or h < 0 or m < 0 or sec < 0:
            raise ValueError(f"Invalid H:MM:SS timestamp: {ts}")
        val = h * 3600 + m * 60 + sec
    elif len(parts) == 2:
        m, sec = int(parts[0]), float(parts[1])
        if sec >= 60 or m < 0 or sec < 0:
            raise ValueError(f"Invalid MM:SS timestamp: {ts}")
        val = m * 60 + sec
    else:
        raise ValueError(f"Invalid timestamp syntax: {ts}")
    if not math.isfinite(val):
        raise ValueError(f"Non-finite timestamp: {ts}")
    return val


def format_timestamp(seconds: float) -> str:
    sec_int = int(round(seconds))
    h, rem = divmod(sec_int, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def format_chapters(chapters: list[dict[str, Any]]) -> str:
    return "\n".join(f"{format_timestamp(c['start_s'])} {c['title']}" for c in chapters)


def validate_chapters(
    chapters: list[dict[str, Any]],
    video_duration_s: float | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    normalized: list[dict[str, Any]] = []

    if video_duration_s is not None and (not math.isfinite(video_duration_s) or video_duration_s <= 0):
        raise ValueError("video_duration_s must be finite and > 0.")

    for idx, ch in enumerate(chapters):
        st = ch.get("start_s")
        title = str(ch.get("title") or "").strip()
        if st is None or not isinstance(st, (int, float)) or not math.isfinite(float(st)) or float(st) < 0:
            errors.append(f"Chapter {idx + 1}: invalid or negative start_s ({st}).")
            continue
        if not title:
            errors.append(f"Chapter {idx + 1} at {format_timestamp(float(st))}: missing title.")
        normalized.append({"start_s": round(float(st), 3), "label": format_timestamp(float(st)), "title": title})

    if len(normalized) < MIN_CHAPTERS:
        errors.append(f"YouTube requires at least {MIN_CHAPTERS} chapters (found {len(normalized)}).")

    if normalized and abs(normalized[0]["start_s"]) > 1e-6:
        errors.append(f"First chapter must start at 00:00 (found {normalized[0]['label']}).")

    for i in range(1, len(normalized)):
        prev = normalized[i - 1]
        cur = normalized[i]
        if cur["start_s"] <= prev["start_s"]:
            errors.append(f"Chapters must be strictly ascending: {cur['label']} follows {prev['label']}.")
        else:
            span = cur["start_s"] - prev["start_s"]
            prev["duration_s"] = round(span, 3)
            if span < MIN_CHAPTER_SECONDS:
                errors.append(
                    f"Chapter '{prev['title']}' ({prev['label']}) is {span:.1f}s; YouTube minimum is {int(MIN_CHAPTER_SECONDS)}s."
                )

    if normalized:
        last = normalized[-1]
        if video_duration_s is not None:
            if last["start_s"] >= video_duration_s:
                errors.append(f"Last chapter ({last['label']}) starts at or after video duration ({video_duration_s}s).")
            else:
                tail = video_duration_s - last["start_s"]
                last["duration_s"] = round(tail, 3)
                if tail < MIN_CHAPTER_SECONDS:
                    errors.append(
                        f"Final chapter '{last['title']}' ({last['label']}) is {tail:.1f}s; minimum is {int(MIN_CHAPTER_SECONDS)}s."
                    )
        else:
            last["duration_s"] = None
            warnings.append("Total video duration not provided; could not verify whether the final chapter lasts >= 10s.")

    return {
        "valid": len(errors) == 0,
        "rules_checked": {
            "starts_at_00_00": True,
            "minimum_chapters": MIN_CHAPTERS,
            "minimum_chapter_seconds": MIN_CHAPTER_SECONDS,
            "strictly_ascending": True,
        },
        "chapter_count": len(normalized),
        "chapters": normalized,
        "formatted_block": format_chapters(normalized) if normalized else "",
        "errors": errors,
        "warnings": warnings,
    }


def _parse_chapter_list(raw_text: str) -> list[dict[str, Any]]:
    stripped = raw_text.strip()
    if not stripped:
        raise ValueError("Chapter list input is empty.")
    if stripped.startswith("[") or stripped.startswith("{"):
        data = json.loads(stripped)
        items = data.get("chapters", data) if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise ValueError("JSON chapter list must be an array or {'chapters': [...]}.")
        out: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each JSON chapter must be an object.")
            if "start_s" in item:
                st = float(item["start_s"])
            elif "timestamp" in item or "label" in item:
                st = _parse_ts(str(item.get("timestamp") or item.get("label")))
            else:
                raise ValueError("Chapter object missing start_s or timestamp.")
            out.append({"start_s": st, "title": str(item.get("title") or "").strip()})
        return out

    out = []
    for line in raw_text.splitlines():
        ls = line.strip()
        if not ls:
            continue
        m = re.match(r"^(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]?\s*(.*)$", ls)
        if not m:
            raise ValueError(f"Could not parse chapter line: {ls}")
        out.append({"start_s": _parse_ts(m.group(1)), "title": m.group(2).strip()})
    return out


def _parse_transcript(raw_text: str, hint: str = "") -> list[tuple[float, float, str]]:
    stripped = raw_text.strip()
    if stripped.startswith("{") or stripped.startswith("[") or hint.lower().endswith(".json"):
        data = json.loads(stripped)
        segs = data.get("segments", data if isinstance(data, list) else [])
        out: list[tuple[float, float, str]] = []
        for s in segs:
            if isinstance(s, dict):
                st, en = float(s["start"]), float(s["end"])
                txt = str(s.get("text") or "").strip()
                if en >= st and txt:
                    out.append((st, en, txt))
        return out

    cues: list[list[Any]] = []
    cur: list[Any] | None = None
    for line in raw_text.splitlines():
        ls = line.strip()
        if not ls or ls.upper().startswith(("WEBVTT", "NOTE", "STYLE")):
            cur = None
            continue
        m = re.match(r"(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", ls)
        if m:
            st, en = _parse_ts(m.group(1)), _parse_ts(m.group(2))
            if en >= st:
                cur = [st, en, []]
                cues.append(cur)
            else:
                cur = None
        elif cur is not None and not ls.isdigit():
            cur[2].append(ls)
    return [(a, b, " ".join(t)) for a, b, t in cues if t]


def _keywords(text: str) -> set[str]:
    return {w for w in re.findall(r"[^\W_]{4,}", text.lower(), flags=re.UNICODE) if w not in STOP}


def draft_from_transcript(cues: list[tuple[float, float, str]], target: int = 6) -> dict[str, Any]:
    if len(cues) < 4:
        raise ValueError("Need at least 4 timestamped cues to draft chapter boundaries.")
    cues = sorted(cues, key=lambda c: c[0])
    dur = cues[-1][1]
    if dur < MIN_CHAPTERS * MIN_CHAPTER_SECONDS:
        raise ValueError(f"Transcript duration ({dur:.1f}s) is too short for 3+ valid 10-second chapters.")

    scored: list[tuple[float, float]] = []
    for i in range(1, len(cues)):
        gap = max(0.0, cues[i][0] - cues[i - 1][1])
        before = " ".join(c[2] for c in cues[max(0, i - 10):i])
        after = " ".join(c[2] for c in cues[i:i + 10])
        kb, ka = _keywords(before), _keywords(after)
        union = kb | ka
        shift = (1.0 - len(kb & ka) / len(union)) if union else 0.0
        scored.append((gap * 1.6 + shift * 3.2, cues[i][0]))
    scored.sort(key=lambda x: (-x[0], x[1]))

    picked = [0.0]
    for _, ts in scored:
        if len(picked) >= target:
            break
        if all(abs(ts - p) >= MIN_CHAPTER_SECONDS for p in picked) and (dur - ts) >= MIN_CHAPTER_SECONDS:
            picked.append(ts)
    picked.sort()

    draft_list: list[dict[str, Any]] = []
    for idx, st in enumerate(picked):
        en = picked[idx + 1] if idx + 1 < len(picked) else dur
        seg_text = " ".join(c[2] for c in cues if c[0] >= st and c[1] <= en + 0.001)
        kw_list = sorted(_keywords(seg_text), key=lambda w: (-seg_text.lower().count(w), w))
        draft_title = " ".join(w.capitalize() for w in kw_list[:3]) or f"Section {idx + 1}"
        draft_list.append({"start_s": round(st, 2), "title": draft_title})

    result = validate_chapters(draft_list, video_duration_s=dur)
    result["mode"] = "DRAFT_FROM_TRANSCRIPT"
    result["note"] = "Draft titles are keyword extracts only — rewrite each into a clear 3-5 word viewer promise before publishing."
    return result


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
        description="Standalone YouTube chapters validator & transcript drafter (JSON stdout)."
    )
    parser.add_argument("input", nargs="?", default="-", help="Chapter list (--validate) or SRT/VTT/JSON transcript, or '-' for stdin.")
    parser.add_argument("--validate", action="store_true", help="Validate an existing chapter list instead of drafting from transcript.")
    parser.add_argument("--duration", type=float, default=None, help="Total video duration in seconds (recommended for --validate).")
    parser.add_argument("--target", type=int, default=6, help="Target chapter count in draft mode (default 6).")
    parser.add_argument("--json", action="store_true", help="Output JSON (default behavior).")
    parser.add_argument("--max-bytes", type=int, default=MAX_INPUT_BYTES, help="Max input size in bytes.")
    args = parser.parse_args(argv)

    if args.max_bytes <= 0 or args.target < MIN_CHAPTERS:
        print("Error: --max-bytes must be > 0 and --target >= 3.", file=sys.stderr)
        return 2

    try:
        if args.input == "-" and sys.stdin.isatty():
            print("Error: Provide an input file path or pipe stdin.", file=sys.stderr)
            return 2
        raw_text = _read_bounded(args.input, args.max_bytes)
        if args.validate:
            chapters = _parse_chapter_list(raw_text)
            payload = {"tool": "chapters.py", "mode": "VALIDATE_CHAPTERS", **validate_chapters(chapters, args.duration)}
        else:
            cues = _parse_transcript(raw_text, args.input)
            payload = {"tool": "chapters.py", **draft_from_transcript(cues, target=args.target)}
    except (ValueError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
