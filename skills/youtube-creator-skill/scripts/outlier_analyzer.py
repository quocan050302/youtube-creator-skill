#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Adapted from: https://github.com/jakeschincariol/youtube-agent-skill
#   Pinned commit: a2feb2104981a375ffd4f87ee04f4f5344ac43c6
#   Source path:   skills/yt-viral/swipe.py & skills/yt-script/hooks.json
#   Upstream Copyright (c) 2026 Jake Schincariol
# Modifications Copyright (c) 2026 quocan050302:
#   - Leave-one-out peer median (fixes candidate self-contamination in baseline)
#   - Strict format (SHORT vs LONG) and configurable age-bucket cohort separation
#   - Deduplication by video_id or canonical URL; missing/null views excluded (never 0)
#   - Standalone single-file execution with embedded 21-formula lexical classifier
"""Standalone cohort-safe YouTube competitor outlier analyzer (JSON stdout)."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import statistics
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

MAX_INPUT_BYTES = 10 * 1024 * 1024
DEFAULT_AGE_BUCKETS = [(0, 7, "0-7d"), (8, 30, "8-30d"), (31, 90, "31-90d"), (91, 365, "91-365d"), (366, 10**9, "365d+")]
LIMITATION_NOTE = (
    "Outlier ratio is a configurable within-channel cohort screening signal, NOT causal proof. "
    "Title formula classification reflects visible wording only — hook retention, thumbnail visuals, "
    "and traffic sources are unobserved unless supplied separately."
)

EMBEDDED_FORMULAS: list[dict[str, Any]] = [
    {"id": "the-statistic", "name": "The Statistic", "match": [r"\b\d+(\.\d+)?\s?%", r"\b\d+ (out of|in) \d+\b", r"\b\d{2,}(,\d{3})+\b"]},
    {"id": "someone-elses-result", "name": "Someone Else's Result", "match": [r"\bthis (channel|guy|creator|account)\b", r"\bwent from .* to\b", r"\bin (a|one|two|three|\d+) (week|month|year)s?\b"]},
    {"id": "the-mistake", "name": "The Mistake", "match": [r"\byou('re| are) (probably |still )?(doing|making)\b", r"\bthe (mistake|reason) (everyone|most people|nobody)\b", r"\bstop (doing )?\b"]},
    {"id": "contrarian-flip", "name": "Contrarian Flip", "match": [r"\beveryone (says|thinks|tells you)\b", r"\bis (actually )?wrong\b", r"\bnobody (tells|talks about)\b"]},
    {"id": "the-reveal", "name": "The Reveal", "match": [r"\bI('m| am) going to show you\b", r"\bhere('s| is) (the|exactly)\b", r"\bon screen\b"]},
    {"id": "the-superlative", "name": "The Superlative", "match": [r"\bthe (best|worst|fastest|easiest|only)\b", r"\bnumber one\b"]},
    {"id": "the-clock", "name": "The Clock", "match": [r"\bin (the next )?\d+ (seconds|minutes|hours)\b", r"\bby the end of this video\b", r"\bunder \d+\b"]},
    {"id": "i-tried-it", "name": "I Tried It", "match": [r"\bI (tried|spent|tested|let|gave)\b", r"\bfor \d+ (days|weeks|months)\b", r"\bso you don'?t have to\b"]},
    {"id": "the-question", "name": "The Question", "match": [r"^(why|how|what|when|should|can|do|does|is)\b", r"\?\s*$"]},
    {"id": "the-before-after", "name": "Before and After", "match": [r"\bbefore\b.*\bafter\b", r"\bthis was\b.*\bthis is\b", r"\bused to\b"]},
    {"id": "the-teardown", "name": "The Teardown", "match": [r"\b(broke|break|breaking) (it )?down\b", r"\bteardown\b", r"\banalys(ed|ed|is|e)\b", r"\bI pulled\b"]},
    {"id": "the-stack", "name": "The Stack", "match": [r"\b\w+ (plus|\+) \w+\b", r"\bcombine\b", r"\btogether\b"]},
    {"id": "the-warning", "name": "The Warning", "match": [r"\bdo not\b", r"\bdon'?t (upload|post|publish|start)\b", r"\bbefore you\b", r"\bstop\b"]},
    {"id": "the-list", "name": "The List", "match": [r"^\d+ \w+", r"\b(here are|these are) \d+\b"]},
    {"id": "the-receipt", "name": "The Receipt", "match": [r"\bthis is (the|my)\b", r"\bscreenshot\b", r"\bproof\b", r"\breceipts?\b"]},
    {"id": "the-insider", "name": "The Insider", "match": [r"\b(nobody|almost nobody|most people) (knows?|opens?|uses?)\b", r"\bhidden\b", r"\bburied\b"]},
    {"id": "the-impossible", "name": "The Impossible Claim", "match": [r"\bwithout\b", r"\bnever\b", r"\bin one\b", r"\bzero\b"]},
    {"id": "the-comparison", "name": "The Comparison", "match": [r"\bvs\.?\b", r"\bversus\b", r"\bwhich (one )?(is|wins)\b", r"\bsame .* (three|two) ways\b"]},
    {"id": "the-origin", "name": "The Origin", "match": [r"\bevery (video|post) .* starts\b", r"\bit all (starts|started)\b", r"\bthe (real )?reason\b"]},
    {"id": "the-deadline", "name": "The Deadline", "match": [r"\b(this|next) (week|month|year)\b", r"\bis changing\b", r"\bno longer\b", r"\bas of\b"]},
    {"id": "the-direct-address", "name": "The Direct Address", "match": [r"^if you\b", r"\bfor (anyone|everyone|people) who\b", r"\byou specifically\b"]},
]


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s).date()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        f = float(value)
        return f if math.isfinite(f) else None
    s = str(value).strip()
    if not s or s.lower() in {"null", "none", "na", "n/a", "nan", "-"}:
        return None
    s = s.replace(",", "").replace("_", "")
    try:
        f = float(s)
        return f if math.isfinite(f) else None
    except ValueError:
        return None


def _canonical_video_id(row: dict[str, Any]) -> str | None:
    vid = row.get("video_id")
    if vid is not None and str(vid).strip():
        return str(vid).strip()
    url = str(row.get("url") or "").strip()
    if not url:
        return None
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if "youtu.be" in host:
        part = parsed.path.strip("/").split("/")[0]
        return part or url
    if "youtube.com" in host:
        if parsed.path.startswith("/shorts/"):
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2:
                return parts[1]
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]
    return f"{host}{parsed.path}".rstrip("/") or url


def _classify_title(title: str) -> str:
    scored: list[tuple[int, str]] = []
    for f in EMBEDDED_FORMULAS:
        hits = sum(1 for p in f["match"] if re.search(p, title, re.I))
        if hits:
            scored.append((hits, f["name"]))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[0][1] if scored else "Unclassified"


def _age_bucket(age_days: int | None) -> str:
    if age_days is None:
        return "age_unknown"
    for lo, hi, label in DEFAULT_AGE_BUCKETS:
        if lo <= age_days <= hi:
            return label
    return "365d+"


def validate_rows(
    raw_rows: list[dict[str, Any]],
    as_of: date | None = None,
    allow_missing_dates: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    valid: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    warnings: list[str] = []
    observed_dates: list[date] = []

    for idx, row in enumerate(raw_rows):
        if not isinstance(row, dict):
            excluded.append({"row_index": idx, "reason": "row_not_object"})
            continue

        channel = str(row.get("channel_id") or row.get("channel") or "").strip()
        if not channel:
            excluded.append({"row_index": idx, "reason": "missing_channel"})
            continue

        vid = _canonical_video_id(row)
        if not vid:
            excluded.append({"row_index": idx, "channel": channel, "reason": "missing_video_id_or_url"})
            continue

        fmt_raw = str(row.get("format") or "").strip().upper()
        if fmt_raw in {"SHORT", "SHORTS"}:
            fmt = "SHORT"
        elif fmt_raw in {"LONG", "LONG_FORM", "LONG-FORM", "VIDEO"}:
            fmt = "LONG"
        else:
            excluded.append({"row_index": idx, "video_id": vid, "reason": "missing_or_invalid_format"})
            continue

        views = _parse_float(row.get("views"))
        if views is None or views < 0:
            excluded.append({"row_index": idx, "video_id": vid, "reason": "missing_or_invalid_views"})
            continue

        duration = _parse_float(row.get("duration_s", row.get("duration")))
        if duration is not None and duration <= 0:
            excluded.append({"row_index": idx, "video_id": vid, "reason": "invalid_nonpositive_duration"})
            continue

        pub_date = _parse_date(row.get("published_at"))
        obs_date = _parse_date(row.get("observed_at")) or as_of
        if obs_date is not None:
            observed_dates.append(obs_date)

        age_days: int | None = None
        if pub_date is not None and obs_date is not None:
            age_days = (obs_date - pub_date).days
            if age_days < 0:
                excluded.append({"row_index": idx, "video_id": vid, "reason": "published_after_observed"})
                continue
        elif not allow_missing_dates:
            excluded.append({"row_index": idx, "video_id": vid, "reason": "missing_published_or_observed_date"})
            continue

        valid.append({
            "channel": channel,
            "video_id": vid,
            "url": str(row.get("url") or "").strip() or None,
            "title": str(row.get("title") or "").strip(),
            "format": fmt,
            "views": views,
            "duration_s": duration,
            "published_at": pub_date.isoformat() if pub_date else None,
            "observed_at": obs_date.isoformat() if obs_date else None,
            "age_days": age_days,
            "age_bucket": _age_bucket(age_days),
        })

    if observed_dates:
        span = (max(observed_dates) - min(observed_dates)).days
        if span > 7:
            warnings.append(
                f"Observation dates span {span} days ({min(observed_dates)} to {max(observed_dates)}); "
                "cross-video snapshot comparability may be reduced."
            )
    if allow_missing_dates and any(r["age_days"] is None for r in valid):
        warnings.append("Some rows lack published_at/observed_at; grouped under age_unknown (reduced comparability).")

    return valid, excluded, warnings


def dedupe(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seen: set[str] = set()
    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for r in rows:
        key = r["video_id"]
        if key in seen:
            dropped.append({"video_id": key, "channel": r["channel"], "reason": "duplicate_video_id"})
            continue
        seen.add(key)
        kept.append(r)
    return kept, dropped


def cohort_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (row["channel"], row["format"], row["age_bucket"])


def peer_baseline(cohort_rows: list[dict[str, Any]], candidate_id: str) -> tuple[float | None, int]:
    peer_views = [r["views"] for r in cohort_rows if r["video_id"] != candidate_id]
    if not peer_views:
        return None, 0
    return float(statistics.median(peer_views)), len(peer_views)


def compute_outlier(
    candidate: dict[str, Any],
    cohort_rows: list[dict[str, Any]],
    min_peers: int = 4,
) -> dict[str, Any] | None:
    med, n_peers = peer_baseline(cohort_rows, candidate["video_id"])
    if n_peers < min_peers or med is None or med <= 0:
        return None
    ratio = candidate["views"] / med
    vpd = None
    if candidate["age_days"] is not None:
        vpd = round(candidate["views"] / max(1, candidate["age_days"]), 2)
    return {
        "channel": candidate["channel"],
        "video_id": candidate["video_id"],
        "title": candidate["title"],
        "url": candidate["url"],
        "format": candidate["format"],
        "age_bucket": candidate["age_bucket"],
        "published_at": candidate["published_at"],
        "observed_at": candidate["observed_at"],
        "views": int(candidate["views"]) if candidate["views"].is_integer() else candidate["views"],
        "peer_count_excluding_candidate": n_peers,
        "peer_median_views": round(med, 2),
        "outlier_ratio": round(ratio, 4),
        "sample_quality": "exploratory_low_n" if n_peers < 5 else "target_n_met",
        "views_per_day_naive_proxy": vpd,
        "title_formula_lexical_only": _classify_title(candidate["title"]),
    }


def rank_outliers(
    raw_rows: list[dict[str, Any]],
    min_ratio: float = 1.5,
    min_peers: int = 4,
    as_of: date | None = None,
    allow_missing_dates: bool = False,
) -> dict[str, Any]:
    if min_peers < 1:
        raise ValueError("min_peers must be >= 1.")
    valid, excluded, warnings = validate_rows(raw_rows, as_of=as_of, allow_missing_dates=allow_missing_dates)
    deduped, dup_dropped = dedupe(valid)
    excluded.extend(dup_dropped)

    cohorts: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for r in deduped:
        cohorts.setdefault(cohort_key(r), []).append(r)

    scored_all: list[dict[str, Any]] = []
    insufficient_cohorts: list[dict[str, Any]] = []

    for ckey, crows in sorted(cohorts.items()):
        if len(crows) - 1 < min_peers:
            insufficient_cohorts.append({
                "channel": ckey[0],
                "format": ckey[1],
                "age_bucket": ckey[2],
                "eligible_videos": len(crows),
                "peers_per_candidate": max(0, len(crows) - 1),
                "reason": f"insufficient_peers_need_at_least_{min_peers}",
            })
            continue
        for cand in crows:
            res = compute_outlier(cand, crows, min_peers=min_peers)
            if res is None:
                excluded.append({"video_id": cand["video_id"], "reason": "zero_or_invalid_peer_median"})
            else:
                scored_all.append(res)

    outliers = [r for r in scored_all if r["outlier_ratio"] >= min_ratio]
    outliers.sort(key=lambda r: (-r["outlier_ratio"], -r["views"], r["video_id"]))
    for rank, item in enumerate(outliers, start=1):
        item["rank"] = rank

    return {
        "tool": "outlier_analyzer.py",
        "as_of": as_of.isoformat() if as_of else None,
        "cohort_rules": {
            "partition_by": ["channel", "format", "age_bucket"],
            "leave_one_out_median": True,
            "min_peers_required": min_peers,
            "target_peers_recommended": 5,
            "min_outlier_ratio_filter": min_ratio,
        },
        "summary": {
            "rows_input": len(raw_rows),
            "rows_eligible_deduped": len(deduped),
            "rows_excluded": len(excluded),
            "cohorts_total": len(cohorts),
            "cohorts_insufficient": len(insufficient_cohorts),
            "candidates_scored": len(scored_all),
            "outliers_above_threshold": len(outliers),
        },
        "warnings": warnings,
        "outliers": outliers,
        "insufficient_cohorts": insufficient_cohorts,
        "excluded_rows": excluded,
        "limitations": LIMITATION_NOTE,
    }


def _load_rows(raw_text: str, filename_hint: str) -> list[dict[str, Any]]:
    stripped = raw_text.strip()
    if not stripped:
        raise ValueError("Empty input.")
    if stripped.startswith("[") or stripped.startswith("{") or filename_hint.lower().endswith(".json"):
        data = json.loads(stripped)
        if isinstance(data, dict) and isinstance(data.get("videos"), list):
            return data["videos"]
        if isinstance(data, list):
            return data
        raise ValueError("JSON input must be a list of video objects or {'videos': [...]}.")
    dialect = csv.Sniffer().sniff(stripped[:4096], delimiters=",;\t") if ("\n" in stripped and ("," in stripped or ";" in stripped)) else csv.excel
    reader = csv.DictReader(io.StringIO(raw_text), dialect=dialect)
    return [dict(row) for row in reader]


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
        description="Standalone cohort-safe YouTube competitor outlier analyzer (JSON stdout)."
    )
    parser.add_argument("input", nargs="?", default="-", help="Path to JSON/CSV dataset, or '-' for stdin.")
    parser.add_argument("--min", dest="min_ratio", type=float, default=1.5, help="Minimum outlier ratio filter.")
    parser.add_argument("--min-peers", type=int, default=4, help="Minimum peer videos excluding candidate (default 4).")
    parser.add_argument("--as-of", default=None, help="Explicit observation date YYYY-MM-DD when rows omit observed_at.")
    parser.add_argument("--allow-missing-dates", action="store_true", help="Allow rows without dates under age_unknown.")
    parser.add_argument("--json", action="store_true", help="Output JSON (default behavior).")
    parser.add_argument("--max-bytes", type=int, default=MAX_INPUT_BYTES, help="Max input size in bytes.")
    args = parser.parse_args(argv)

    if args.max_bytes <= 0 or not math.isfinite(args.min_ratio) or args.min_ratio < 0:
        print("Error: Invalid numeric flag.", file=sys.stderr)
        return 2

    as_of_date = _parse_date(args.as_of) if args.as_of else None
    if args.as_of and as_of_date is None:
        print("Error: --as-of must be ISO date YYYY-MM-DD.", file=sys.stderr)
        return 2

    try:
        if args.input == "-" and sys.stdin.isatty():
            print("Error: Provide a JSON/CSV input path or pipe stdin.", file=sys.stderr)
            return 2
        raw_text = _read_bounded(args.input, args.max_bytes)
        rows = _load_rows(raw_text, args.input)
        payload = rank_outliers(
            rows,
            min_ratio=args.min_ratio,
            min_peers=args.min_peers,
            as_of=as_of_date,
            allow_missing_dates=args.allow_missing_dates,
        )
    except (ValueError, FileNotFoundError, OSError, csv.Error, json.JSONDecodeError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
