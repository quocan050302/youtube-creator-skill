#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Adapted from: https://github.com/jakeschincariol/youtube-agent-skill
#   Pinned commit: a2feb2104981a375ffd4f87ee04f4f5344ac43c6
#   Source path:   skills/yt-script/hookscore.py & skills/yt-script/hooks.json
#   Upstream Copyright (c) 2026 Jake Schincariol
# Modifications Copyright (c) 2026 quocan050302:
#   - Standalone single-file execution (zero sibling file reads; embedded 21 formulas)
#   - UTF-8 stdin/file CLI, 10 MB input cap, strict exit codes (0=ok, 2=invalid input)
#   - Added POV-neutral narrative Shorts mode (--pov narrative / --shorts-story)
#   - Transparent 5-dimension rubric (0-2 each, 0-10 total) + upstream compatibility panel
"""Standalone YouTube hook heuristic scorer and 21-formula classifier.

Heuristic text linter only — NEVER a retention or view-count predictor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 10 * 1024 * 1024
RUBRIC_ID = "yt-hook-heuristic-v1.0.0"
LIMITATION_NOTE = (
    "Deterministic lexical heuristic only. Useful for catching vague hype, filler, "
    "excess length, or self-answering hooks; NEVER predicts views or viewer retention."
)

# Embedded 21 formulas (exact parity with assets/hooks.json; verified by unit tests)
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

FILLER = {
    "basically", "actually", "literally", "just", "really", "very", "so",
    "kind", "sort", "like", "guys", "hey", "welcome", "today", "video",
    "subscribe", "channel",
}
INTRO_SPAM = re.compile(r"\b(hey guys|welcome back|in today'?s video|before we get started|smash that subscribe)\b", re.I)
VAGUE = {
    "amazing", "incredible", "insane", "crazy", "huge", "massive", "game",
    "changer", "secret", "powerful", "ultimate", "best", "revolutionary",
    "mind", "blowing", "unbelievable", "epic",
}
CONCRETE = re.compile(r"\b(\d[\d,.]*\s?(%|k|m|x|s|h|ft|lb|kg|km)?|\$\d[\d,.]*|\d+\s?(second|minute|hour|day|week|month|year)s?)\b", re.I)
YOU = re.compile(r"\b(you|your|you're|youre|yourself)\b", re.I)
STAKE = re.compile(r"\b(lose|lost|wasting|waste|quit|fail|failed|broke|broken|cost|risk|before|stop|stopped|never|die|dying|dead|collapse|collapsed|trap|scam|freeze|freezes|slow|slows|kill|killed|snap|snaps|snapped)\b", re.I)
CURIOSITY = re.compile(r"\b(why|how|what|which|until|before|but|yet|nobody|almost|except|reason|actually|still|without|instead)\b", re.I)
SELF_CLOSING = re.compile(r"\b(because|so that|which means|the answer is)\b", re.I)
STOP = {"the", "a", "an", "of", "for", "to", "in", "on", "and", "or", "is", "are", "was", "were", "it", "this", "that", "with"}


def formulas_fingerprint() -> str:
    canonical = json.dumps(EMBEDDED_FORMULAS, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def normalize_hook(text: str) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = unicodedata.normalize("NFC", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)?", text.lower(), flags=re.UNICODE)


def classify_formula(text: str) -> tuple[str | None, str, int]:
    best: dict[str, Any] | None = None
    best_hits = 0
    for formula in EMBEDDED_FORMULAS:
        hits = sum(1 for pat in formula["match"] if re.search(pat, text, re.I))
        if hits > best_hits:
            best = formula
            best_hits = hits
    if best is None:
        return None, "Unclassified", 0
    return best["id"], best["name"], best_hits


def score_hook(hook_text: str, pov: str = "direct", title: str | None = None) -> dict[str, Any]:
    t = normalize_hook(hook_text)
    tokens = _tokenize(t)
    word_count = len(tokens)
    if word_count == 0:
        raise ValueError("Hook text must contain at least one word.")

    nums = CONCRETE.findall(t)
    vague_hits = sorted({w for w in tokens if w in VAGUE})
    filler_hits = sorted({w for w in tokens if w in FILLER})
    intro_hit = bool(INTRO_SPAM.search(t))
    mid_caps = sum(1 for w in t.split()[1:] if w[:1].isupper() and any(ch.isalpha() for ch in w))

    # Upstream-compatible 0-100 feature panel
    spec_100 = max(0, min(100, 34 + len(nums) * 22 - len(vague_hits) * 16 - len(filler_hits) * 5 + min(18, 6 * mid_caps)))
    you_hits = len(YOU.findall(t))
    you_early = bool(YOU.search(" ".join(t.split()[:6])))
    if pov == "narrative":
        # POV-neutral storytelling mode: do not penalize 3rd-person concrete hooks
        concrete_subject_bonus = 24 if (nums or mid_caps or word_count >= 7) else 0
        addr_100 = max(0, min(100, 62 + concrete_subject_bonus - (25 if intro_hit else 0)))
    else:
        addr_100 = max(0, min(100, 26 + you_hits * 20 + (30 if you_early else 0) - (20 if intro_hit else 0)))

    stake_hits = len(STAKE.findall(t))
    stakes_100 = max(0, min(100, 22 + stake_hits * 26 + (14 if nums else 0)))
    cur_hits = len(CURIOSITY.findall(t))
    q_bonus = 18 if t.endswith("?") else 0
    closed_pen = -18 if SELF_CLOSING.search(t) else 0
    curiosity_100 = max(0, min(100, 24 + cur_hits * 17 + q_bonus + closed_pen))

    if 8 <= word_count <= 24:
        brevity_100 = 100
    elif word_count < 8:
        brevity_100 = max(30, 100 - (8 - word_count) * 11)
    else:
        brevity_100 = max(10, 100 - (word_count - 24) * 7)

    panel = {
        "specificity": spec_100,
        "address": addr_100,
        "stakes": stakes_100,
        "curiosity": curiosity_100,
        "brevity": brevity_100,
    }
    vals = list(panel.values())
    verdict_100 = round(0.6 * (sum(vals) / len(vals)) + 0.4 * min(vals))
    band = "STRONG" if verdict_100 >= 72 else ("WORKABLE" if verdict_100 >= 55 else "WEAK")

    # 5-dimension human-readable heuristic rubric (0-2 each, 0-10 total)
    reasons: list[str] = []
    r_spec = 2 if (spec_100 >= 60 and not vague_hits) else (1 if spec_100 >= 38 else 0)
    if vague_hits:
        reasons.append(f"Vague hype terms detected: {', '.join(vague_hits)}")
    if intro_hit:
        reasons.append("Generic channel intro phrase weakens the opening.")

    r_comp = 2 if (not intro_hit and 6 <= word_count <= 24 and len(filler_hits) <= 1) else (1 if word_count <= 34 else 0)
    if word_count > 24:
        reasons.append(f"Opening is {word_count} words; trim toward 8-24 words for faster breath.")

    r_cur = 2 if (curiosity_100 >= 55 or (stakes_100 >= 50 and closed_pen == 0)) else (1 if (curiosity_100 >= 35 or stakes_100 >= 36) else 0)
    if closed_pen < 0:
        reasons.append("Contains self-answering connector ('because'/'which means') that closes the curiosity gap early.")

    if title:
        title_toks = {w for w in _tokenize(title) if w not in STOP}
        hook_toks = {w for w in tokens if w not in STOP}
        overlap = title_toks & hook_toks
        if title_toks and overlap:
            r_align = 2 if len(overlap) / max(1, len(title_toks)) < 0.9 else 1
            if r_align == 1:
                reasons.append("Hook nearly repeats the title verbatim; confirm the promise with a fresh angle.")
        else:
            r_align = 0
            reasons.append("Lexical overlap with title is zero; verify manually that the hook confirms the title promise.")
    else:
        r_align = 1 if not intro_hit else 0
        reasons.append("No title supplied; promise_alignment requires manual verification against title/first frame.")

    r_speak = 2 if (brevity_100 >= 80 and not intro_hit and len(filler_hits) <= 1) else (1 if brevity_100 >= 50 else 0)
    if filler_hits:
        reasons.append(f"Filler words present: {', '.join(filler_hits)}")

    rubric = {
        "specificity": r_spec,
        "immediate_comprehension": r_comp,
        "curiosity_stakes": r_cur,
        "promise_alignment": r_align,
        "speakability_visual": r_speak,
    }
    rubric_total = sum(rubric.values())
    formula_id, formula_name, formula_hits = classify_formula(t)
    weakest_key = min(panel, key=lambda k: panel[k])

    return {
        "hook": t,
        "word_count": word_count,
        "pov_mode": pov,
        "formula_id": formula_id,
        "formula_name": formula_name,
        "formula_patterns_matched": formula_hits,
        "rubric_0_to_10": rubric,
        "rubric_total": rubric_total,
        "rubric_max": 10,
        "legacy_panel_0_to_100": panel,
        "legacy_verdict_0_to_100": verdict_100,
        "heuristic_band": band,
        "weakest_property": weakest_key,
        "reasons": reasons,
    }


def rank_hooks(hooks: list[str], pov: str = "direct", title: str | None = None) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for idx, raw in enumerate(hooks):
        norm = normalize_hook(raw)
        if not norm:
            continue
        key = norm.casefold()
        if key in seen:
            duplicates.append(norm)
            continue
        seen[key] = idx
        item = score_hook(norm, pov=pov, title=title)
        item["input_index"] = idx
        results.append(item)

    if not results:
        raise ValueError("No non-empty hook candidates supplied.")

    results.sort(key=lambda r: (-r["rubric_total"], -r["legacy_verdict_0_to_100"], r["input_index"]))
    for rank, item in enumerate(results, start=1):
        item["rank"] = rank

    return {
        "tool": "hookscore.py",
        "rubric_id": RUBRIC_ID,
        "formulas_count": len(EMBEDDED_FORMULAS),
        "formulas_sha256": formulas_fingerprint(),
        "pov_mode": pov,
        "title_reference": normalize_hook(title) if title else None,
        "count_evaluated": len(results),
        "duplicates_removed": len(duplicates),
        "results": results,
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


def _extract_hooks(raw_text: str) -> list[str]:
    stripped = raw_text.strip()
    if not stripped:
        return []
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            data = json.loads(stripped)
            if isinstance(data, list):
                return [str(x) if isinstance(x, str) else str(x.get("hook", "")) for x in data]
            if isinstance(data, dict) and isinstance(data.get("hooks"), list):
                return [str(x) if isinstance(x, str) else str(x.get("hook", "")) for x in data["hooks"]]
        except json.JSONDecodeError:
            pass
    return [line for line in raw_text.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Standalone YouTube hook heuristic scorer and 21-formula classifier (JSON stdout)."
    )
    parser.add_argument("input", nargs="?", help="Path to text/JSON file of hooks, or '-' for stdin.")
    parser.add_argument("--hook", action="append", default=[], help="Hook text to score (repeatable).")
    parser.add_argument("--title", default=None, help="Optional video title to check lexical promise overlap.")
    parser.add_argument("--pov", choices=["direct", "narrative"], default="direct", help="POV scoring mode.")
    parser.add_argument("--shorts-story", action="store_true", help="Alias for --pov narrative (3rd-person Shorts).")
    parser.add_argument("--json", action="store_true", help="Output JSON (default behavior).")
    parser.add_argument("--max-bytes", type=int, default=MAX_INPUT_BYTES, help="Max input size in bytes.")
    args = parser.parse_args(argv)

    if args.max_bytes <= 0:
        print("Error: --max-bytes must be positive.", file=sys.stderr)
        return 2

    pov = "narrative" if args.shorts_story else args.pov
    hooks: list[str] = list(args.hook)
    try:
        if args.input:
            hooks.extend(_extract_hooks(_read_bounded_text(args.input, args.max_bytes)))
        elif not hooks and not sys.stdin.isatty():
            hooks.extend(_extract_hooks(_read_bounded_text("-", args.max_bytes)))
        if not hooks:
            print("Error: Provide --hook, a file path, or stdin input.", file=sys.stderr)
            return 2
        payload = rank_hooks(hooks, pov=pov, title=args.title)
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
