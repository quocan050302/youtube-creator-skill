#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Validate canonical SKILL.md against Agent Skills spec and Agensi guidelines."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILL_DIR = REPO_ROOT / "skills" / "youtube-creator-skill"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_LINK_RE = re.compile(r"`((?:references|scripts|assets)/[A-Za-z0-9_.\-/]+)`")
BARE_REF_MD_RE = re.compile(r"`([a-z0-9\-]+\.md)`")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    errors: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, ["SKILL.md must begin with '---' YAML frontmatter delimiter."]
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, text, ["SKILL.md YAML frontmatter missing closing '---' delimiter."]

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    data: dict[str, Any] = {}
    cur_map: str | None = None
    for raw in fm_lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw.startswith("  ") and cur_map is not None:
            if ":" not in raw:
                errors.append(f"Malformed nested frontmatter line: {raw!r}")
                continue
            k, v = raw.strip().split(":", 1)
            data[cur_map][k.strip()] = v.strip().strip('"').strip("'")
            continue
        cur_map = None
        if ":" not in raw:
            errors.append(f"Malformed frontmatter line: {raw!r}")
            continue
        k, v = raw.split(":", 1)
        key = k.strip()
        val = v.strip()
        if not val:
            data[key] = {}
            cur_map = key
        else:
            data[key] = val.strip('"').strip("'")
    return data, body, errors


def validate_skill_dir(skill_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not skill_dir.is_dir():
        return {"valid": False, "errors": [f"Skill directory not found: {skill_dir}"], "warnings": []}

    skill_mds = sorted(skill_dir.rglob("SKILL.md"))
    if len(skill_mds) != 1 or skill_mds[0] != skill_dir / "SKILL.md":
        errors.append(f"Expected exactly 1 canonical SKILL.md at root; found {[str(p.relative_to(skill_dir)) for p in skill_mds]}")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return {"valid": False, "errors": errors or ["Missing SKILL.md"], "warnings": warnings}

    raw = skill_md.read_text(encoding="utf-8")
    fm, body, fm_errors = parse_frontmatter(raw)
    errors.extend(fm_errors)

    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not isinstance(name, str) or not name:
        errors.append("Frontmatter missing required 'name'.")
    else:
        if len(name) > 64:
            errors.append(f"Frontmatter name exceeds 64 chars ({len(name)}).")
        if not NAME_RE.match(name):
            errors.append(f"Frontmatter name must be lowercase kebab-case: {name!r}")
        if name != skill_dir.name:
            errors.append(f"Frontmatter name ({name!r}) must match directory name ({skill_dir.name!r}).")

    if not isinstance(desc, str) or not desc:
        errors.append("Frontmatter missing required 'description'.")
    elif len(desc) > 1024:
        errors.append(f"Frontmatter description exceeds 1024 chars ({len(desc)}).")

    if "allowed-tools" in fm:
        warnings.append("allowed-tools present in frontmatter; avoid broad preauthorization.")

    line_count = len(raw.splitlines())
    approx_tokens = len(raw) // 4
    if line_count > 500:
        errors.append(f"SKILL.md exceeds 500-line ceiling ({line_count} lines).")
    elif line_count > 250:
        warnings.append(f"SKILL.md exceeds 250-line target ({line_count} lines).")
    if approx_tokens > 5000:
        errors.append(f"SKILL.md exceeds ~5000 token ceiling (~{approx_tokens} tokens).")

    # Verify all referenced files exist (both explicit paths and bare lowercase .md refs in SKILL.md routing table)
    referenced = set(REF_LINK_RE.findall(body))
    for bare in BARE_REF_MD_RE.findall(body):
        if bare not in {"skill.md", "readme.md"}:
            referenced.add(f"references/{bare}")
    referenced_sorted = sorted(referenced)
    for rel in referenced_sorted:
        if not (skill_dir / rel).is_file():
            errors.append(f"Broken reference in SKILL.md: {rel}")

    # Check scripts for standalone safety (no sibling imports / no network / no subprocess)
    banned_script_patterns = [
        (re.compile(r"\bimport\s+(urllib|requests|httpx|socket|subprocess)\b"), "banned_network_or_subprocess_import"),
        (re.compile(r"\bfrom\s+(urllib\.request|http\.client|subprocess)\s+import\b"), "banned_network_or_subprocess_import"),
        (re.compile(r"\b(eval|exec)\s*\("), "banned_eval_or_exec"),
        (re.compile(r"os\.path\.dirname\(__file__\)|Path\(__file__\)"), "sibling_relative_file_lookup"),
    ]
    script_stats: list[dict[str, Any]] = []
    for sp in sorted((skill_dir / "scripts").glob("*.py")):
        src = sp.read_text(encoding="utf-8")
        # Strip embedded static formula block from logic byte count per Agensi guideline
        logic_src = re.sub(r"EMBEDDED_FORMULAS\s*:[\s\S]*?\n\]\n", "", src)
        logic_bytes = len(logic_src.encode("utf-8"))
        total_bytes = len(src.encode("utf-8"))
        script_stats.append({"script": sp.name, "total_bytes": total_bytes, "logic_bytes": logic_bytes})
        # Internal project ceiling: 32 KiB (adjusted from 24 KiB in v1.0.0-rc.4 so standalone retention.py keeps full unit-precedence & CSV/JSON validation intact without cutting checks; Agensi platform limit is 5 MB agent / 50 MB web).
        if logic_bytes > 32 * 1024:
            warnings.append(f"Script {sp.name} logic size ({logic_bytes} B) exceeds 32 KiB internal project ceiling.")
        for pat, code in banned_script_patterns:
            if pat.search(src):
                errors.append(f"Script {sp.name} failed static safety check: {code}")

    # Check if official skills-ref CLI is available
    skills_ref_status = "NOT_RUN_UNAVAILABLE"
    skills_ref_bin = shutil.which("skills-ref")
    if skills_ref_bin:
        proc = subprocess.run([skills_ref_bin, "validate", str(skill_dir)], capture_output=True, text=True)
        skills_ref_status = "PASS" if proc.returncode == 0 else f"FAIL ({proc.stderr.strip() or proc.stdout.strip()})"
        if proc.returncode != 0:
            errors.append(f"Official skills-ref validator failed: {skills_ref_status}")

    return {
        "tool": "validate_skill.py",
        "skill_dir": str(skill_dir),
        "valid": len(errors) == 0,
        "frontmatter": fm,
        "line_count": line_count,
        "approx_tokens": approx_tokens,
        "references_checked": len(referenced),
        "scripts_checked": script_stats,
        "official_skills_ref": skills_ref_status,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate canonical Agent Skill directory.")
    parser.add_argument("skill_dir", nargs="?", default=str(DEFAULT_SKILL_DIR))
    args = parser.parse_args(argv)
    report = validate_skill_dir(Path(args.skill_dir))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
