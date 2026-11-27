#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Adapted from: https://github.com/jakeschincariol/youtube-agent-skill
#   Pinned commit: a2feb2104981a375ffd4f87ee04f4f5344ac43c6
#   Source path:   skills/yt-package/title.py
#   Upstream Copyright (c) 2026 Jake Schincariol
# Modifications Copyright (c) 2026 quocan050302:
#   - Standalone UTF-8 CLI with stdin/file support and 10 MB cap
#   - Unicode-aware tokenization for global multilingual creators
#   - Multi-thumbnail lexical overlap check without penalizing missing thumbnails
#   - Shorts/Long flexible length heuristics (never presented as CTR guarantees)
"""Standalone YouTube title and thumbnail lexical linter (JSON stdout)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 10 * 1024 * 1024
DESKTOP_CAUTION = 60
MOBILE_CAUTION = 40
YOUTUBE_HARD_LIMIT = 100
LIMITATION_NOTE = (
    "Lexical and length heuristic only. Truncation varies by device, language, and UI surface. "
    "Token overlap detects repeated words but does not prove semantic duplication or predict CTR."
)

VAGUE = {
    "amazing", "incredible", "insane", "crazy", "huge", "massive", "ultimate",
    "best", "powerful", "secret", "revolutionary", "mindblowing", "epic",
    "perfect", "complete", "everything", "unbelievable", "shocking",
}
STOP = {
    "the", "a", "an", "of", "for", "to", "in", "on", "and", "or", "is", "are",
    "was", "were", "with", "your", "you", "my", "i", "this", "that", "it",
    "how", "what", "why", "who", "from", "into", "about",
}


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def _tokens(text: str) -> list[str]:
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)?", text.lower(), flags=re.UNICODE)


def _count_emoji_or_symbols(text: str) -> int:
    count = 0
    for ch in text:
        cat = unicodedata.category(ch)
        if cat == "So":
            count += 1
    return count


def compare_title_thumb(title: str, thumb: str | None) -> dict[str, Any]:
    if thumb is None or not normalize_text(thumb):
        return {
            "thumbnail_text": None,
            "status": "UNKNOWN_NO_THUMBNAIL_TEXT",
            "shared_tokens": [],
            "thumb_word_count": None,
            "warnings": [],
        }

    t_norm = normalize_text(title)
    h_norm = normalize_text(thumb)
    tw = {w for w in _tokens(t_norm) if w not in STOP}
    hw = {w for w in _tokens(h_norm) if w not in STOP}
    shared = sorted(tw & hw)
    h_words = _tokens(h_norm)
    warnings: list[dict[str, str]] = []

    if t_norm.casefold() == h_norm.casefold():
        warnings.append({
            "code": "identical_title_thumb",
            "severity": "high",
            "message": "Thumbnail text is identical to the title — use complementary framing instead of repeating.",
        })
    elif shared:
        warnings.append({
            "code": "duplicate_tokens",
            "severity": "medium",
            "message": f"Lexical overlap on: {', '.join(shared)} (check whether thumbnail adds new context).",
        })

    if len(h_words) > 3:
        warnings.append({
            "code": "thumb_word_count",
            "severity": "low",
            "message": f"{len(h_words)} words on thumbnail (0-3 words is a common mobile legibility heuristic).",
        })

    return {
        "thumbnail_text": h_norm,
        "status": "WARN" if warnings else "COMPLEMENTARY_LEXICAL",
        "shared_tokens": shared,
        "thumb_word_count": len(h_words),
        "warnings": warnings,
    }


def lint_title(
    title: str,
    thumbs: list[str] | None = None,
    video_format: str = "LONG",
) -> dict[str, Any]:
    t = normalize_text(title)
    if not t:
        raise ValueError("Title cannot be empty.")

    toks = _tokens(t)
    char_len = len(t)
    word_count = len(toks)
    warnings: list[dict[str, str]] = []
    strengths: list[str] = []

    if char_len > YOUTUBE_HARD_LIMIT:
        warnings.append({
            "code": "exceeds_hard_limit",
            "severity": "high",
            "message": f"{char_len} chars exceeds YouTube's {YOUTUBE_HARD_LIMIT}-character title limit.",
        })
    elif char_len > DESKTOP_CAUTION:
        warnings.append({
            "code": "desktop_truncation_risk",
            "severity": "medium",
            "message": f"{char_len} chars may truncate on desktop search (~{DESKTOP_CAUTION}-char heuristic).",
        })
    else:
        strengths.append(f"{char_len} chars fits within the ~{DESKTOP_CAUTION}-char desktop heuristic.")

    if char_len > MOBILE_CAUTION:
        preview = t[:MOBILE_CAUTION].rsplit(" ", 1)[0] if " " in t[:MOBILE_CAUTION] else t[:MOBILE_CAUTION]
        warnings.append({
            "code": "mobile_truncation_caution",
            "severity": "low",
            "message": f'Mobile feeds may truncate near "{preview}..." — verify the core subject stays visible.',
        })

    if video_format == "SHORT" and word_count > 10:
        warnings.append({
            "code": "shorts_word_length",
            "severity": "low",
            "message": f"{word_count} words; Shorts titles often scan faster around 5-8 words (flexible preference).",
        })

    raw_words = t.split()
    all_caps = [
        w for w in raw_words
        if sum(1 for ch in w if ch.isalpha()) >= 3 and w == w.upper() and w != w.lower()
    ]
    if len(all_caps) > 2:
        warnings.append({
            "code": "caps_spam",
            "severity": "medium",
            "message": f"{len(all_caps)} ALL-CAPS words ({', '.join(all_caps[:4])}); cap at 0-2 to avoid spam look.",
        })

    exclam = t.count("!")
    emojis = _count_emoji_or_symbols(t)
    if exclam >= 2 or emojis >= 2:
        warnings.append({
            "code": "punctuation_emoji_clutter",
            "severity": "medium",
            "message": f"Detected {exclam} exclamation marks and {emojis} symbol/emoji chars; simplify for clarity.",
        })

    vague_hits = sorted({w for w in toks if w in VAGUE})
    if vague_hits:
        warnings.append({
            "code": "vague_hype",
            "severity": "medium",
            "message": f"Generic hype terms ({', '.join(vague_hits)}); swap for concrete action, entity, or figure.",
        })

    nums = re.findall(r"\d[\d,.]*%?", t)
    proper_mid = [w for w in raw_words[1:] if w[:1].isupper() and any(ch.isalpha() for ch in w)]
    if nums:
        strengths.append(f"Contains concrete figure(s): {', '.join(nums[:3])}.")
    elif proper_mid:
        strengths.append("Contains concrete named subject(s).")
    elif word_count >= 4:
        strengths.append("Concrete phrasing check: human/agent should verify clear visual subject and curiosity gap.")

    if toks and all(w in STOP for w in toks[:3]) and len(toks) >= 3:
        warnings.append({
            "code": "weak_front_load",
            "severity": "low",
            "message": "First three words are stopwords; consider front-loading the subject.",
        })

    thumb_checks: list[dict[str, Any]] = []
    if thumbs:
        for th in thumbs:
            thumb_checks.append(compare_title_thumb(t, th))
    else:
        thumb_checks.append(compare_title_thumb(t, None))

    thumb_warn_penalty = sum(
        18 if w["severity"] == "high" else (10 if w["severity"] == "medium" else 4)
        for tc in thumb_checks
        for w in tc["warnings"]
    )
    title_warn_penalty = sum(
        22 if w["severity"] == "high" else (12 if w["severity"] == "medium" else 5)
        for w in warnings
    )
    heuristic_score = max(0, min(100, 100 - title_warn_penalty - thumb_warn_penalty))

    return {
        "title": t,
        "format": video_format,
        "char_count": char_len,
        "word_count": word_count,
        "heuristic_score_0_to_100": heuristic_score,
        "warnings": warnings,
        "strengths": strengths,
        "thumbnail_comparisons": thumb_checks,
    }


def rank_titles(
    titles: list[str],
    thumbs: list[str] | None = None,
    video_format: str = "LONG",
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    seen_norm: list[tuple[int, str, set[str]]] = []
    near_duplicates: list[dict[str, Any]] = []

    for idx, raw in enumerate(titles):
        norm = normalize_text(raw)
        if not norm:
            continue
        toks = {w for w in _tokens(norm) if w not in STOP}
        for prev_idx, prev_title, prev_toks in seen_norm:
            if toks and prev_toks:
                jacc = len(toks & prev_toks) / len(toks | prev_toks)
                if jacc >= 0.8:
                    near_duplicates.append({
                        "title_a": prev_title,
                        "title_b": norm,
                        "token_jaccard": round(jacc, 3),
                    })
        seen_norm.append((idx, norm, toks))
        entry = lint_title(norm, thumbs=thumbs, video_format=video_format)
        entry["input_index"] = idx
        items.append(entry)

    if not items:
        raise ValueError("No non-empty titles supplied.")

    items.sort(key=lambda r: (-r["heuristic_score_0_to_100"], r["char_count"], r["input_index"]))
    for rank, entry in enumerate(items, start=1):
        entry["rank"] = rank

    return {
        "tool": "title_linter.py",
        "format": video_format,
        "count_evaluated": len(items),
        "near_duplicates_detected": near_duplicates,
        "results": items,
        "limitations": LIMITATION_NOTE,
    }


def _read_bounded_text(path_or_dash: str, max_bytes: int) -> str:
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


def _extract_titles(raw_text: str) -> list[str]:
    stripped = raw_text.strip()
    if not stripped:
        return []
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            data = json.loads(stripped)
            if isinstance(data, list):
                return [str(x) if isinstance(x, str) else str(x.get("title", "")) for x in data]
            if isinstance(data, dict) and isinstance(data.get("titles"), list):
                return [str(x) if isinstance(x, str) else str(x.get("title", "")) for x in data["titles"]]
        except json.JSONDecodeError:
            pass
    return [line for line in raw_text.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Standalone YouTube title & thumbnail lexical linter (JSON stdout)."
    )
    parser.add_argument("input", nargs="?", help="Path to titles text/JSON file, or '-' for stdin.")
    parser.add_argument("--title", action="append", default=[], help="Title to lint (repeatable).")
    parser.add_argument("--thumb", action="append", default=[], help="Optional thumbnail text (repeatable).")
    parser.add_argument("--format", choices=["SHORT", "LONG"], default="LONG", help="Video format context.")
    parser.add_argument("--json", action="store_true", help="Output JSON (default behavior).")
    parser.add_argument("--max-bytes", type=int, default=MAX_INPUT_BYTES, help="Max input size in bytes.")
    args = parser.parse_args(argv)

    if args.max_bytes <= 0:
        print("Error: --max-bytes must be positive.", file=sys.stderr)
        return 2

    titles = list(args.title)
    try:
        if args.input:
            titles.extend(_extract_titles(_read_bounded_text(args.input, args.max_bytes)))
        elif not titles and not sys.stdin.isatty():
            titles.extend(_extract_titles(_read_bounded_text("-", args.max_bytes)))
        if not titles:
            print("Error: Provide --title, a file path, or stdin input.", file=sys.stderr)
            return 2
        payload = rank_titles(titles, thumbs=args.thumb or None, video_format=args.format)
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
