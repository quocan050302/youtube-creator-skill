#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Deterministically build self-contained universal/UNIVERSAL_PROMPT.md from canonical skill sources."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "youtube-creator-skill"
OUT_PATH = REPO_ROOT / "universal" / "UNIVERSAL_PROMPT.md"

ALLOWLISTED_SECTIONS = [
    ("SEC-01", "Capability Boundaries & Prompt-Injection Safety", "references/capability-matrix.md"),
    ("SEC-02", "Master Router & Intent Handling", "references/master-router.md"),
    ("SEC-03", "Portable Creator Profile & Memory Rules", "references/creator-profile.md"),
    ("SEC-04", "Research Engine & Source Discipline", "references/research-engine.md"),
    ("SEC-05", "Fact Verification & Evidence Boundaries", "references/fact-verification.md"),
    ("SEC-06", "Competitor Cohort Rules (No Median Leakage)", "references/competitor-research.md"),
    ("SEC-07", "Topic Strategy & Angle Selection", "references/topic-strategy.md"),
    ("SEC-08", "Niche Profiles & Audience Calibration", "references/niche-profiles.md"),
    ("SEC-09", "TT-01 Title Curiosity Gate", "references/title-engine.md"),
    ("SEC-10", "Hook Lab & 5-Dimension Rubric", "references/hook-engine.md"),
    ("SEC-11", "KH-01 Storytelling, 10 Niche Modes & WPM Timing", "references/storytelling-engine.md"),
    ("SEC-12", "Humor, Deadpan Contrast & Analogy Guardrails", "references/humor-engine.md"),
    ("SEC-13", "Visual Packaging, First Frame & Storyboard Rules", "references/visual-packaging.md"),
    ("SEC-14", "Editing Intelligence & Transcript EDL Rules", "references/editing-intelligence.md"),
    ("SEC-15", "Analytics Truth Model & Retention Curve Diagnosis", "references/analytics-diagnosis.md"),
    ("SEC-16", "Channel Audit & Continuous Learning Loop", "references/channel-audit.md"),
    ("SEC-17", "Capacity-Aware Content Calendars", "references/planning-engine.md"),
    ("SEC-18", "Long-to-Short Repurpose Engine", "references/repurpose-engine.md"),
    ("SEC-19", "SEO, Comment Triage & YouTube Chapters", "references/seo-comments-chapters.md"),
    ("SEC-20", "Creator Action Pack & Output Contract", "references/output-contract.md"),
    ("SEC-21", "Pre-Delivery Quality Hard-Fail Gates", "references/quality-gates.md"),
]

REL_REF_RE = re.compile(r"`(?:references|scripts|assets)/[A-Za-z0-9_.\-/]+`")


def _strip_frontmatter(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    version = "1.0.0-rc.2"
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip().startswith("version:"):
                version = lines[i].split(":", 1)[1].strip().strip('"').strip("'")
            if lines[i].strip() == "---":
                return version, "\n".join(lines[i + 1 :]).strip()
    return version, text.strip()


def _neutralize_local_paths(text: str) -> str:
    """Replace internal native file paths so universal prompt has zero unresolved links."""
    text = re.sub(r"See `references/[a-z0-9\-]+\.md`\.", "", text)
    text = re.sub(r"\(`references/[a-z0-9\-]+\.md`\)", "", text)
    text = re.sub(r"`references/([a-z0-9\-]+)\.md`", lambda m: f"the {m.group(1).replace('-', ' ')} section below", text)
    text = re.sub(r"`scripts/([a-z0-9_]+\.py)`", lambda m: f"optional offline helper `{m.group(1)}` (if Python tools are available; otherwise apply the qualitative rubric below)", text)
    text = re.sub(r"`assets/([a-z0-9_\-.]+)`", lambda m: f"the bundled `{m.group(1)}` specification", text)
    text = re.sub(r"  +", " ", text)
    return text.strip()


def build_universal_prompt(repo_root: Path = REPO_ROOT) -> tuple[str, dict[str, object]]:
    skill_dir = repo_root / "skills" / "youtube-creator-skill"
    skill_md_raw = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    version, core_body = _strip_frontmatter(skill_md_raw)

    # Compute deterministic source hash over allowlisted canonical inputs
    hasher = hashlib.sha256()
    hasher.update(skill_md_raw.encode("utf-8"))
    for _, _, rel in ALLOWLISTED_SECTIONS:
        hasher.update((skill_dir / rel).read_bytes())
    for lic_rel in [
        "LICENSE",
        "LICENSES/mromidev-claude-animated-shorts-MIT.txt",
        "LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt",
    ]:
        hasher.update((repo_root / lic_rel).read_bytes())
    source_sha = hasher.hexdigest()

    hooks_data = json.loads((skill_dir / "assets" / "hooks.json").read_text(encoding="utf-8"))
    hook_lines = [f"- **{h['name']}** (`{h['id']}`): {h['shape']}" for h in hooks_data["hooks"]]

    parts: list[str] = [
        "# YouTube Creator Intelligence — Universal Self-Contained Prompt",
        "",
        f"- **Canonical Skill:** `youtube-creator-skill`",
        f"- **Version:** `{version}`",
        f"- **Canonical Source SHA-256:** `{source_sha}`",
        "- **License:** MIT (Free $0; full notices included in Appendix B)",
        "- **Use Mode:** Paste this entire file at the start of any chat (ChatGPT, Claude Chat, Gemini, DeepSeek, Grok, Qwen, Copilot, etc.) and follow with your YouTube request. No file links, Python runtime, or API keys are required.",
        "",
        "## Quick-Start Prompt Examples (Copy One Below After Pasting)",
        "- `Create a 45-second YouTube Short Action Pack about why a magnet slows down inside a copper pipe. No CTA.`",
        "- `Give me 6 TT-01 title options only for a video about common reshipping job scams.`",
        "- `Audit my retention drop from this pasted CSV and propose ONE experiment for my next upload.`",
        "",
        "---",
        "",
        "## SEC-00 — Core Operating Instructions",
        "",
        _neutralize_local_paths(core_body),
        "",
    ]

    for sec_id, sec_title, rel in ALLOWLISTED_SECTIONS:
        raw = (skill_dir / rel).read_text(encoding="utf-8").strip()
        # Demote top heading to avoid duplicate H1
        body_lines = raw.splitlines()
        if body_lines and body_lines[0].startswith("# "):
            body_lines = body_lines[1:]
        cleaned = _neutralize_local_paths("\n".join(body_lines).strip())
        parts.extend([
            "---",
            "",
            f"## {sec_id} — {sec_title}",
            "",
            cleaned,
            "",
        ])

    parts.extend([
        "---",
        "",
        "## APPENDIX A — 21 Attributed Hook Formula Bank (MIT)",
        "",
        "Adapted from `jakeschincariol/youtube-agent-skill` (`a2feb2104981a375ffd4f87ee04f4f5344ac43c6`, MIT). Use as a diverse option bank, not rigid boilerplate:",
        "",
        *hook_lines,
        "",
        "---",
        "",
        "## APPENDIX B — MIT License & Third-Party Notices (Mandatory for Redistribution)",
        "",
        "### Project License (`youtube-creator-skill`)",
        "```text",
        (repo_root / "LICENSE").read_text(encoding="utf-8").strip(),
        "```",
        "",
        "### Upstream Notice 1 — `mromidev/claude-animated-shorts` (commit `e3b817b6afc6cd413466d43f11ba31209e034bbf`)",
        "```text",
        (repo_root / "LICENSES" / "mromidev-claude-animated-shorts-MIT.txt").read_text(encoding="utf-8").strip(),
        "```",
        "",
        "### Upstream Notice 2 — `jakeschincariol/youtube-agent-skill` (commit `a2feb2104981a375ffd4f87ee04f4f5344ac43c6`)",
        "```text",
        (repo_root / "LICENSES" / "jakeschincariol-youtube-agent-skill-MIT.txt").read_text(encoding="utf-8").strip(),
        "```",
        "",
    ])

    output = "\n".join(parts).rstrip() + "\n"
    unresolved = REL_REF_RE.findall(output)
    if unresolved:
        raise RuntimeError(f"Unresolved local skill links found in generated universal prompt: {unresolved}")
    included_slugs = {Path(rel).stem.replace("-", " ") for _, _, rel in ALLOWLISTED_SECTIONS}
    mentioned_below = set(re.findall(r"the ([a-z ]+) section below", output))
    dangling_sections = sorted(m for m in mentioned_below if m not in included_slugs)
    if dangling_sections:
        raise RuntimeError(f"Dangling 'section below' references to omitted modules: {dangling_sections}")

    meta = {
        "version": version,
        "source_sha256": source_sha,
        "output_bytes": len(output.encode("utf-8")),
        "approx_tokens": len(output) // 4,
        "sections_included": len(ALLOWLISTED_SECTIONS) + 3,
        "unresolved_links": len(unresolved),
    }
    return output, meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build universal/UNIVERSAL_PROMPT.md deterministically.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--out", default=str(OUT_PATH))
    parser.add_argument("--check", action="store_true", help="Verify existing file matches generated output.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root)
    out_path = Path(args.out)
    content, meta = build_universal_prompt(repo_root)

    if args.check:
        if not out_path.is_file() or out_path.read_text(encoding="utf-8") != content:
            print("FAIL: universal/UNIVERSAL_PROMPT.md is out of date.", file=sys.stderr)
            return 1
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8", newline="\n")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"tool": "build_universal_prompt.py", "out": str(out_path), **meta}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
