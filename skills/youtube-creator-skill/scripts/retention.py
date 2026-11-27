#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Adapted from: https://github.com/jakeschincariol/youtube-agent-skill
#   Pinned commit: a2feb2104981a375ffd4f87ee04f4f5344ac43c6
#   Source path:   skills/yt-retention/retention.py
#   Upstream Copyright (c) 2026 Jake Schincariol
# Modifications Copyright (c) 2026 quocan050302:
#   - Zero sibling imports (built-in SRT/VTT/Whisper JSON parser for isolated execution)
#   - Explicit Shorts vs Long early windows; rejected universal 30s/25% folklore
#   - Percentage-point (pp) deltas & pp/s slopes; valid >100% rewatch/loop spikes preserved
#   - Strict axis/unit validation, unsorted/duplicate handling, non-causal transcript alignment
"""Standalone YouTube audience-retention curve analyzer (JSON stdout)."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import statistics
import sys
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 10 * 1024 * 1024
LIMITATION_NOTE = (
    "Retention curves show WHERE viewers left or rewatched, not WHY. "
    "Aligned transcript lines are possible contributors — never proven causes — "
    "and cannot separate script issues from editing or audio issues without media inspection."
)


def _parse_num(raw: Any) -> tuple[float | None, bool]:
    if raw is None or isinstance(raw, bool):
        return None, False
    if isinstance(raw, (int, float)):
        f = float(raw)
        return (f, False) if math.isfinite(f) else (None, False)
    s = str(raw).strip()
    if not s or s.lower() in {"null", "none", "na", "n/a", "nan", "-"}:
        return None, False
    has_pct = "%" in s
    s = s.replace("%", "").replace(" ", "")
    # Handle European decimal comma when single comma and no dot (e.g. "85,4")
    if "," in s and "." not in s and len(s.split(",")) == 2 and len(s.split(",")[1]) <= 2:
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        f = float(s)
        return (f, has_pct) if math.isfinite(f) else (None, False)
    except ValueError:
        return None, False


def _parse_ts(ts: str) -> float:
    s = ts.strip().replace(",", ".")
    parts = s.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    raise ValueError(f"Unparseable timestamp: {ts}")


def _load_transcript_text(raw: str, hint: str = "") -> list[tuple[float, float, str]]:
    stripped = raw.strip()
    if not stripped:
        return []
    if stripped.startswith("{") or stripped.startswith("[") or hint.lower().endswith(".json"):
        data = json.loads(stripped)
        segs = data.get("segments", data.get("words", data if isinstance(data, list) else []))
        out: list[tuple[float, float, str]] = []
        for s in segs:
            if not isinstance(s, dict):
                continue
            st, en = _parse_num(s.get("start"))[0], _parse_num(s.get("end"))[0]
            txt = str(s.get("text") or s.get("word") or "").strip()
            if st is not None and en is not None and en >= st and txt:
                out.append((st, en, txt))
        return out

    cues: list[list[Any]] = []
    cur: list[Any] | None = None
    skip_block = False
    for line in raw.splitlines():
        ls = line.strip()
        if ls.startswith(("WEBVTT", "NOTE", "STYLE", "REGION")):
            skip_block = ls.startswith(("NOTE", "STYLE"))
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
            st, en = _parse_ts(m.group(1)), _parse_ts(m.group(2))
            if en >= st:
                cur = [st, en, []]
                cues.append(cur)
            else:
                cur = None
        elif cur is not None and not ls.isdigit():
            cur[2].append(ls)
    return [(a, b, " ".join(t)) for a, b, t in cues if t]


def parse_curve(raw_text: str) -> tuple[list[tuple[float, float]], dict[str, Any]]:
    if not raw_text.strip():
        raise ValueError("Retention input is empty.")
    stripped = raw_text.strip()
    meta: dict[str, Any] = {"headers": [], "pct_sign_seen_x": False, "pct_sign_seen_y": False, "rows_skipped": 0}
    pts: list[tuple[float, float]] = []
    if stripped[0] in "[{":
        data = json.loads(stripped)
        rows = data.get("points", data) if isinstance(data, dict) else data
        if not isinstance(rows, list):
            raise ValueError("JSON retention input must be a list or {'points': [...]}.")
        for item in rows:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                (x, xp), (y, yp) = _parse_num(item[0]), _parse_num(item[1])
            elif isinstance(item, dict):
                (x, xp) = _parse_num(item.get("x", item.get("time_s", item.get("pct"))))
                (y, yp) = _parse_num(item.get("y", item.get("retention_pct", item.get("retention"))))
            else:
                meta["rows_skipped"] += 1
                continue
            if x is None or y is None:
                meta["rows_skipped"] += 1
                continue
            meta["pct_sign_seen_x"] |= xp
            meta["pct_sign_seen_y"] |= yp
            pts.append((x, y))
        return pts, meta

    delim = ";" if (stripped[:4096].count(";") > stripped[:4096].count(",")) else ","
    for idx, row in enumerate(csv.reader(io.StringIO(raw_text), delimiter=delim)):
        if not row or all(not c.strip() for c in row):
            continue
        nums = [(v, hp) for v, hp in (_parse_num(c) for c in row) if v is not None]
        if idx == 0 and len(nums) < 2:
            meta["headers"] = [c.strip() for c in row]
            continue
        if len(nums) >= 2:
            (x, xp), (y, yp) = nums[0], nums[1]
            meta["pct_sign_seen_x"] |= xp
            meta["pct_sign_seen_y"] |= yp
            pts.append((x, y))
        else:
            meta["rows_skipped"] += 1
    return pts, meta


def normalize_time(
    points: list[tuple[float, float]],
    time_unit: str,
    duration_s: float | None,
    meta: dict[str, Any],
) -> tuple[list[tuple[float, float]], dict[str, Any]]:
    if len(points) < 3:
        raise ValueError(f"At least 3 valid retention data points required (got {len(points)}).")
    if duration_s is not None and (not math.isfinite(duration_s) or duration_s <= 0):
        raise ValueError("duration_s must be finite and > 0.")

    xs = [p[0] for p in points]
    if any(x < 0 or not math.isfinite(x) for x in xs):
        raise ValueError("Timestamps/positions must be finite and >= 0.")

    warnings: list[str] = []
    unsorted = any(xs[i] < xs[i - 1] for i in range(1, len(xs)))
    if unsorted:
        warnings.append("Input x-axis was unsorted; points were sorted ascending by position.")
    ordered = sorted(points, key=lambda p: p[0])

    # Deduplicate identical x values (policy: keep last observed value at duplicate timestamp)
    deduped: list[tuple[float, float]] = []
    dup_count = 0
    for x, y in ordered:
        if deduped and abs(x - deduped[-1][0]) < 1e-9:
            deduped[-1] = (x, y)
            dup_count += 1
        else:
            deduped.append((x, y))
    if dup_count:
        warnings.append(f"Resolved {dup_count} duplicate x-axis point(s) by keeping the last entry.")

    header_str = " ".join(meta.get("headers", [])).lower()
    if time_unit == "auto":
        if meta.get("pct_sign_seen_x") or "percent" in header_str or "%" in header_str:
            resolved_unit = "percent"
        elif "sec" in header_str or "time" in header_str:
            resolved_unit = "seconds"
        elif max(p[0] for p in deduped) <= 100.5 and duration_s is not None and abs(max(p[0] for p in deduped) - 100.0) <= 2.0 and duration_s != 100.0:
            resolved_unit = "percent"
            warnings.append("Inferred x-axis as percent (0-100%) from max~100 and explicit duration; pass --time-unit to override.")
        else:
            resolved_unit = "seconds"
    else:
        resolved_unit = time_unit

    if resolved_unit == "percent":
        if max(p[0] for p in deduped) > 100.5:
            raise ValueError("Percent x-axis exceeds 100%.")
        if duration_s is None:
            raise ValueError("duration_s is required when x-axis is normalized percentage.")
        converted = [(x / 100.0 * duration_s, y) for x, y in deduped]
    else:
        if duration_s is not None and max(p[0] for p in deduped) > duration_s * 1.05 + 1.0:
            raise ValueError(f"Observed timestamp {max(p[0] for p in deduped)}s exceeds supplied duration_s ({duration_s}s).")
        converted = deduped

    spacings = [converted[i][0] - converted[i - 1][0] for i in range(1, len(converted)) if converted[i][0] > converted[i - 1][0]]
    axis_info = {
        "input_time_unit": resolved_unit,
        "duration_s": duration_s if duration_s is not None else round(converted[-1][0], 3),
        "observed_range_s": [round(converted[0][0], 3), round(converted[-1][0], 3)],
        "points_count": len(converted),
        "median_step_s": round(statistics.median(spacings), 3) if spacings else None,
        "max_step_s": round(max(spacings), 3) if spacings else None,
        "warnings": warnings,
    }
    return converted, axis_info


def normalize_rate(
    points: list[tuple[float, float]],
    rate_unit: str,
    meta: dict[str, Any],
) -> tuple[list[tuple[float, float]], dict[str, Any]]:
    ys = [p[1] for p in points]
    if any(y < 0 or not math.isfinite(y) for y in ys):
        raise ValueError("Retention values must be finite and >= 0.")

    max_y = max(ys)
    warnings: list[str] = []
    if rate_unit == "auto":
        if meta.get("pct_sign_seen_y"):
            resolved = "percent"
        elif max_y <= 2.5 and any(0 < y <= 1.05 for y in ys) and max_y <= 1.5:
            # Ambiguous if values sit cleanly in 0..1.5 without % signs -> explicit check
            if max_y <= 1.05 and ys[0] <= 1.05 and ys[0] > 0.2:
                resolved = "ratio"
                warnings.append("Converted 0..1 ratio values to percentage (x100); pass --rate-unit percent|ratio to lock.")
            else:
                raise ValueError(
                    "Ambiguous retention y-axis unit (values <= 2.5 without '%' sign). "
                    "Pass --rate-unit percent or --rate-unit ratio explicitly."
                )
        else:
            resolved = "percent"
    else:
        resolved = rate_unit

    converted = [(x, y * 100.0) for x, y in points] if resolved == "ratio" else points
    if any(y > 100.0 for _, y in converted):
        warnings.append(
            "Retention exceeds 100% at one or more timestamps (valid YouTube rewatch/loop behavior — NOT clamped)."
        )
    return converted, {"input_rate_unit": resolved, "warnings": warnings}


def _value_at(points: list[tuple[float, float]], target_s: float) -> tuple[float | None, str]:
    if target_s < points[0][0] or target_s > points[-1][0]:
        return None, "out_of_observed_range"
    for x, y in points:
        if abs(x - target_s) < 1e-9:
            return y, "exact_observed_point"
    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        if x0 <= target_s <= x1 and x1 > x0:
            frac = (target_s - x0) / (x1 - x0)
            return y0 + frac * (y1 - y0), "linear_between_observed_points"
    return None, "unavailable"


def detect_early_change(
    points: list[tuple[float, float]],
    video_format: str,
    duration_s: float,
    custom_window_s: float | None = None,
) -> dict[str, Any]:
    if custom_window_s is not None:
        windows = [custom_window_s]
    elif video_format == "SHORT":
        windows = [3.0, round(duration_s * 0.15, 2)]
    else:
        windows = [15.0, 30.0]

    start_x, start_y = points[0]
    results: list[dict[str, Any]] = []
    seen_w: set[float] = set()
    for w in windows:
        if w <= start_x or w in seen_w:
            continue
        seen_w.add(w)
        val, method = _value_at(points, w)
        if val is None:
            results.append({
                "window_end_s": round(w, 2),
                "status": "NOT_OBSERVED_IN_RANGE",
                "method": method,
            })
            continue
        delta_pp = val - start_y
        rel_pct = (delta_pp / start_y * 100.0) if start_y > 0 else None
        results.append({
            "window_start_s": round(start_x, 2),
            "window_end_s": round(w, 2),
            "start_retention_pct": round(start_y, 2),
            "end_retention_pct": round(val, 2),
            "delta_pp": round(delta_pp, 2),
            "relative_change_pct": round(rel_pct, 2) if rel_pct is not None else None,
            "slope_pp_per_s": round(delta_pp / (w - start_x), 3),
            "method": method,
        })
    return {"format": video_format, "windows": results}


def detect_cliffs(
    points: list[tuple[float, float]],
    min_drop_pp: float = 3.0,
    slope_multiplier: float = 2.5,
) -> dict[str, Any]:
    segments: list[dict[str, Any]] = []
    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        dt = x1 - x0
        if dt <= 0:
            continue
        delta_pp = y1 - y0
        slope = delta_pp / dt
        segments.append({
            "start_s": round(x0, 3),
            "end_s": round(x1, 3),
            "dt_s": round(dt, 3),
            "start_pct": round(y0, 2),
            "end_pct": round(y1, 2),
            "delta_pp": round(delta_pp, 2),
            "slope_pp_per_s": round(slope, 3),
        })

    neg_slopes = [abs(s["slope_pp_per_s"]) for s in segments if s["delta_pp"] < 0]
    bg_drop_slope = statistics.median(neg_slopes) if neg_slopes else 0.0
    total_end = points[-1][0]

    cliffs: list[dict[str, Any]] = []
    spikes: list[dict[str, Any]] = []
    for seg in segments:
        is_end_tail = total_end > 0 and seg["start_s"] >= total_end * 0.90
        if seg["delta_pp"] <= -min_drop_pp:
            abs_slope = abs(seg["slope_pp_per_s"])
            ratio = (abs_slope / bg_drop_slope) if bg_drop_slope > 1e-6 else float("inf")
            if bg_drop_slope == 0.0 or ratio >= slope_multiplier:
                cliffs.append({
                    **seg,
                    "slope_vs_background_median": round(ratio, 2) if math.isfinite(ratio) else None,
                    "is_end_tail_likely_natural_exit": is_end_tail,
                    "is_post_rewatch_spike_return": seg["start_pct"] > 100.0,
                })
        elif seg["delta_pp"] >= min_drop_pp:
            spikes.append({**seg, "note": "Positive retention spike (possible rewatch or skip-to moment)."})

    cliffs.sort(key=lambda c: (c["delta_pp"], -abs(c["slope_pp_per_s"]), c["start_s"]))
    spikes.sort(key=lambda s: (-s["delta_pp"], s["start_s"]))

    # Steady middle slide excluding first 10% and last 10%
    mid_segs = [s for s in segments if total_end > 0 and (0.10 * total_end) <= s["start_s"] <= (0.90 * total_end)]
    middle_slide = round(statistics.mean([s["slope_pp_per_s"] for s in mid_segs]), 4) if mid_segs else None

    return {
        "background_median_drop_slope_pp_per_s": round(bg_drop_slope, 4),
        "middle_mean_slope_pp_per_s": middle_slide,
        "cliffs": cliffs[:10],
        "rewatch_or_skip_spikes": spikes[:5],
    }


def align_transcript(
    cliffs: list[dict[str, Any]],
    cues: list[tuple[float, float, str]],
    pad_s: float = 2.0,
) -> list[dict[str, Any]]:
    aligned: list[dict[str, Any]] = []
    for c in cliffs:
        lo, hi = c["start_s"] - pad_s, c["end_s"] + pad_s
        matched = [txt for st, en, txt in cues if st <= hi and en >= lo]
        aligned.append({
            "cliff_interval_s": [c["start_s"], c["end_s"]],
            "delta_pp": c["delta_pp"],
            "transcript_excerpt": " ".join(matched)[:240] if matched else None,
            "attribution_note": "possible_contributor_not_proven_cause" if matched else "no_transcript_cue_in_window",
        })
    return aligned


def summarize(
    points: list[tuple[float, float]],
    axis_info: dict[str, Any],
    rate_info: dict[str, Any],
    early: dict[str, Any],
    cliff_info: dict[str, Any],
    transcript_alignment: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    warnings = list(axis_info["warnings"]) + list(rate_info["warnings"])
    return {
        "tool": "retention.py",
        "axis": {k: v for k, v in axis_info.items() if k != "warnings"},
        "rate_unit_input": rate_info["input_rate_unit"],
        "overview": {
            "start_retention_pct": round(points[0][1], 2),
            "end_retention_pct": round(points[-1][1], 2),
            "max_retention_pct": round(max(y for _, y in points), 2),
            "min_retention_pct": round(min(y for _, y in points), 2),
            "has_rewatch_above_100pct": any(y > 100.0 for _, y in points),
        },
        "early_window_change": early,
        "cliffs_and_slide": cliff_info,
        "transcript_alignment": transcript_alignment,
        "warnings": warnings,
        "limitations": LIMITATION_NOTE,
    }


def _read_bounded(path_or_dash: str, max_bytes: int) -> str:
    if path_or_dash == "-":
        raw = sys.stdin.buffer.read(max_bytes + 1)
    else:
        p = Path(path_or_dash)
        if not p.is_file():
            raise FileNotFoundError(f"Not found: {path_or_dash}")
        if p.stat().st_size > max_bytes:
            raise ValueError(f"Exceeds {max_bytes} bytes.")
        raw = p.read_bytes()
    if len(raw) > max_bytes:
        raise ValueError(f"Exceeds {max_bytes} bytes.")
    return raw.decode("utf-8-sig", errors="replace")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Standalone YouTube audience-retention curve analyzer (JSON stdout).")
    p.add_argument("input", nargs="?", default="-")
    p.add_argument("--format", choices=["SHORT", "LONG"], default="LONG")
    p.add_argument("--duration", type=float, default=None)
    p.add_argument("--time-unit", choices=["auto", "seconds", "percent"], default="auto")
    p.add_argument("--rate-unit", choices=["auto", "percent", "ratio"], default="auto")
    p.add_argument("--early-sec", type=float, default=None)
    p.add_argument("--min-drop-pp", type=float, default=3.0)
    p.add_argument("--slope-mult", type=float, default=2.5)
    p.add_argument("--transcript", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--max-bytes", type=int, default=MAX_INPUT_BYTES)
    args = p.parse_args(argv)
    if args.max_bytes <= 0 or args.min_drop_pp <= 0 or args.slope_mult <= 0:
        print("Error: thresholds must be > 0.", file=sys.stderr)
        return 2
    try:
        if args.input == "-" and sys.stdin.isatty():
            print("Error: Provide retention CSV/JSON or stdin.", file=sys.stderr)
            return 2
        pts, meta = parse_curve(_read_bounded(args.input, args.max_bytes))
        t_pts, axis_info = normalize_time(pts, args.time_unit, args.duration, meta)
        norm_pts, rate_info = normalize_rate(t_pts, args.rate_unit, meta)
        early = detect_early_change(norm_pts, args.format, axis_info["duration_s"], args.early_sec)
        cliffs = detect_cliffs(norm_pts, args.min_drop_pp, args.slope_mult)
        aligned = align_transcript(cliffs["cliffs"], _load_transcript_text(_read_bounded(args.transcript, args.max_bytes), args.transcript)) if args.transcript else None
        payload = summarize(norm_pts, axis_info, rate_info, early, cliffs, aligned)
    except (ValueError, FileNotFoundError, OSError, csv.Error, json.JSONDecodeError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
