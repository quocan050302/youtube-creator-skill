#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Deterministic reproducible release builder for Agensi and Universal ZIP packages.

Enforces explicit allowlist, safe POSIX paths, zero symlinks, fixed ZIP timestamps,
byte-for-byte reproducibility verification, Agensi limits check, and clean extraction
smoke tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)
AGENSI_MAX_BYTES = 1 * 1024 * 1024       # Strict project target <= 1 MB (platform limit 50 MB web / 5 MB agent)
AGENSI_MAX_FILES = 90                     # Strict project target <= 90 files (platform limit 100 agent / 200 delivered)
AGENSI_MAX_CHARS = 6_000_000              # Agensi agent delivery character cap
BANNED_EXTS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".app", ".dmg", ".msi", ".deb",
    ".rpm", ".wasm", ".class", ".jar", ".war", ".zip", ".tar", ".gz", ".7z",
    ".mp4", ".mov", ".wav", ".mp3", ".png", ".jpg", ".jpeg", ".gif", ".pdf",
    ".pyc", ".pyo",
}
TEXT_EXTS = {".md", ".txt", ".py", ".json", ".csv", ".yml", ".yaml", ".srt"}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _safe_arcname(arcname: str) -> str:
    norm = arcname.replace("\\", "/")
    if norm.startswith("/") or ":" in norm or ".." in norm.split("/"):
        raise ValueError(f"Unsafe archive entry path: {arcname!r}")
    return norm


def _collect_skill_entries(repo_root: Path) -> list[tuple[str, Path]]:
    skill_dir = repo_root / "skills" / "youtube-creator-skill"
    entries: list[tuple[str, Path]] = []
    allowed_top = {
        "SKILL.md", "LICENSE", "THIRD_PARTY_NOTICES.md",
        "LICENSES", "references", "scripts", "assets",
    }
    for item in sorted(skill_dir.rglob("*")):
        if item.is_symlink():
            raise ValueError(f"Symlink disallowed in package: {item}")
        if item.is_dir():
            continue
        rel = item.relative_to(skill_dir)
        if "__pycache__" in rel.parts or rel.parts[0] not in allowed_top:
            continue
        ext = item.suffix.lower()
        if ext in BANNED_EXTS or (ext and ext not in TEXT_EXTS):
            raise ValueError(f"Non-text or banned file type in Agensi skill tree: {rel}")
        arc = _safe_arcname(f"youtube-creator-skill/{rel.as_posix()}")
        entries.append((arc, item))
    entries.sort(key=lambda x: x[0])
    return entries


def _write_deterministic_zip(zip_path: Path, items: list[tuple[str, bytes]]) -> dict[str, Any]:
    seen_ci: set[str] = set()
    sorted_items = sorted(items, key=lambda x: x[0])
    total_uncompressed = 0
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for arcname, raw_bytes in sorted_items:
            arc = _safe_arcname(arcname)
            if arc.lower() in seen_ci:
                raise ValueError(f"Case-insensitive duplicate ZIP entry: {arc}")
            seen_ci.add(arc.lower())
            # Validate UTF-8 decodability for all shipped text entries
            raw_bytes.decode("utf-8")
            zi = zipfile.ZipInfo(filename=arc, date_time=FIXED_ZIP_TIME)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3  # Unix
            zi.external_attr = (0o100644) << 16
            zf.writestr(zi, raw_bytes)
            total_uncompressed += len(raw_bytes)

    return {
        "path": str(zip_path),
        "filename": zip_path.name,
        "size_bytes": zip_path.stat().st_size,
        "uncompressed_bytes": total_uncompressed,
        "file_count": len(sorted_items),
        "sha256": _sha256_file(zip_path),
        "entries": [arc for arc, _ in sorted_items],
    }


def _start_here_text(version: str) -> bytes:
    content = f"""# Start Here — YouTube Creator Intelligence (`v{version}`)

Welcome! This free MIT-licensed package gives you **three ways** to use `youtube-creator-skill`,
with zero API keys, zero accounts, and zero required paid tools.

## Option 1 — Native AI Coding Agents (Recommended if you use Antigravity, Claude Code, or Codex)
Copy the `youtube-creator-skill/` folder into your project (recommended project-local install):
- **Antigravity / Codex:** `<your-project>/.agents/skills/youtube-creator-skill/`
- **Claude Code:** `<your-project>/.claude/skills/youtube-creator-skill/`

Then ask naturally:
> "Use youtube-creator-skill to create a 45-second YouTube Short pack on [your topic]."

See `docs/INSTALL.md` for Windows PowerShell and macOS/Linux commands plus global paths.

## Option 2 — Any Chat Interface (ChatGPT, Claude Chat, Gemini, DeepSeek, Grok, Qwen, Copilot)
Open `UNIVERSAL_PROMPT.md`, paste it into a new chat (or upload it as context), and type your request.
No local install or Python environment is required.

## Option 3 — Agensi Marketplace
If your agent is connected via Agensi MCP, load the free listing directly from Agensi.
(Agensi delivers skill files to your agent through MCP rather than direct ZIP download; this GitHub
Universal ZIP is the official direct-download distribution.)

## Licensing & Boundaries
- Licensed under MIT (`LICENSE`, `LICENSES/`, `THIRD_PARTY_NOTICES.md`).
- Advisory & creation only: nothing is auto-uploaded to YouTube, and no views/CTR are guaranteed.
"""
    return content.encode("utf-8")


def _release_notes_text(version: str, commit_sha: str, agensi_meta: dict[str, Any], uni_meta: dict[str, Any], prompt_sha: str) -> str:
    is_rc = "-rc." in version
    status_label = "Release Candidate (RC)" if is_rc else "Release"
    return f"""# Release Notes — YouTube Creator Intelligence `v{version}`

- **Status:** {status_label}
- **Source Commit:** `{commit_sha}`
- **License:** MIT (Free $0 — see `LICENSE`, `LICENSES/`, and `THIRD_PARTY_NOTICES.md`)

## Included Distributions

1. **`{agensi_meta['filename']}`** (Agensi Marketplace Package)
   - Files: `{agensi_meta['file_count']}` (1 canonical `SKILL.md`, UTF-8 text/code only, zero bundled dependencies)
   - Size: `{agensi_meta['size_bytes']:,}` bytes
   - SHA-256: `{agensi_meta['sha256']}`
2. **`{uni_meta['filename']}`** (Universal Direct-Download Package)
   - Includes the exact same canonical `youtube-creator-skill/` folder plus `START_HERE.md`, `UNIVERSAL_PROMPT.md`, `docs/`, `examples/`, and full MIT notices.
   - Files: `{uni_meta['file_count']}`
   - Size: `{uni_meta['size_bytes']:,}` bytes
   - SHA-256: `{uni_meta['sha256']}`
3. **`UNIVERSAL_PROMPT.md`** (Standalone Copy-Paste Prompt)
   - SHA-256: `{prompt_sha}`

## Verified Scope
- 17 YouTube creator intents across Shorts and Long-form (research, competitor cohort analysis, TT-01 titles, 21-formula Hook Lab, KH-01 10-niche scripts, visual packaging, transcript edit review, retention curve diagnosis, channel audit, 7/14/30-day planning, repurposing, SEO/comments/chapters, continuous learning loop).
- 7 optional standalone Python 3 stdlib tools tested in isolated temp directories with zero sibling imports.
- Offline-first: works with zero API keys, zero accounts, and zero external dependencies.

## Known Limitations
- Text, research, and analytics advisory only: does not render video/audio/images or auto-publish to YouTube.
- Heuristic hook/title scores and outlier ratios are screening signals, not CTR or view guarantees.
- Multi-client native certification across external desktop/CLI clients (`codex`, `claude`) and external Agensi marketplace review remain tracked separately in `docs/COMPATIBILITY.md` and release evidence.
"""


def _verify_extracted_agensi(zip_path: Path, repo_root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="yt_verify_agensi_") as td:
        td_path = Path(td)
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            if sum(1 for n in names if n.endswith("/SKILL.md") or n == "SKILL.md") != 1:
                raise AssertionError("Agensi ZIP must contain exactly ONE SKILL.md")
            if not all(n.startswith("youtube-creator-skill/") for n in names):
                raise AssertionError("Agensi ZIP must use a single enclosing youtube-creator-skill/ folder")
            total_chars = 0
            for info in zf.infolist():
                _safe_arcname(info.filename)
                total_chars += len(zf.read(info.filename).decode("utf-8"))
            if len(names) > AGENSI_MAX_FILES:
                raise AssertionError(f"Agensi file count {len(names)} exceeds target {AGENSI_MAX_FILES}")
            if zip_path.stat().st_size > AGENSI_MAX_BYTES:
                raise AssertionError(f"Agensi ZIP size {zip_path.stat().st_size} exceeds target {AGENSI_MAX_BYTES}")
            if total_chars > AGENSI_MAX_CHARS:
                raise AssertionError(f"Agensi char count {total_chars} exceeds cap {AGENSI_MAX_CHARS}")
            zf.extractall(td_path)

        extracted_skill = td_path / "youtube-creator-skill"
        # Verify notices parity inside extracted skill
        for rel in [
            "LICENSE",
            "THIRD_PARTY_NOTICES.md",
            "LICENSES/mromidev-claude-animated-shorts-MIT.txt",
            "LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt",
        ]:
            if _sha256_file(extracted_skill / rel) != _sha256_file(repo_root / rel):
                raise AssertionError(f"Notice mismatch in extracted Agensi ZIP: {rel}")

        # Run validate_skill.py against extracted skill directory
        val = subprocess.run(
            [sys.executable, str(repo_root / "tools" / "validate_skill.py"), str(extracted_skill)],
            capture_output=True, text=True, check=False,
        )
        if val.returncode != 0:
            raise AssertionError(f"validate_skill failed on extracted Agensi ZIP: {val.stdout} {val.stderr}")

        # Smoke test one script copied to an empty isolated temp dir (Agensi execution model)
        with tempfile.TemporaryDirectory(prefix="yt_iso_smoke_") as iso:
            iso_script = Path(iso) / "hookscore.py"
            shutil.copyfile(extracted_skill / "scripts" / "hookscore.py", iso_script)
            proc = subprocess.run(
                [sys.executable, str(iso_script), "--shorts-story", "--hook", "Drop a magnet through a copper pipe and gravity seems to break."],
                cwd=iso, capture_output=True, text=True, check=False,
            )
            if proc.returncode != 0:
                raise AssertionError(f"Isolated temp-file smoke test failed: {proc.stderr}")
            parsed = json.loads(proc.stdout)
            if parsed.get("formulas_count") != 21:
                raise AssertionError("Isolated hookscore.py did not report 21 formulas")

        return {"verified": True, "extracted_files": len(names), "total_chars": total_chars}


def build_release(repo_root: Path, version: str, out_dir: Path, verify_repro: bool = True) -> dict[str, Any]:
    # Sync notices into canonical skill folder deterministically first
    skill_dir = repo_root / "skills" / "youtube-creator-skill"
    for rel in [
        "LICENSE",
        "THIRD_PARTY_NOTICES.md",
        "LICENSES/mromidev-claude-animated-shorts-MIT.txt",
        "LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt",
    ]:
        dst = skill_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((repo_root / rel).read_bytes())

    # Ensure UNIVERSAL_PROMPT.md is freshly generated
    gen = subprocess.run(
        [sys.executable, str(repo_root / "tools" / "build_universal_prompt.py"), "--repo-root", str(repo_root), "--out", str(repo_root / "universal" / "UNIVERSAL_PROMPT.md")],
        capture_output=True, text=True, check=False,
    )
    if gen.returncode != 0:
        raise RuntimeError(f"build_universal_prompt.py failed: {gen.stderr}")

    skill_entries = _collect_skill_entries(repo_root)
    agensi_items = [(arc, path.read_bytes()) for arc, path in skill_entries]

    # Build Universal ZIP allowlist
    uni_items: list[tuple[str, bytes]] = list(agensi_items)
    uni_items.append(("START_HERE.md", _start_here_text(version)))
    uni_prompt_bytes = (repo_root / "universal" / "UNIVERSAL_PROMPT.md").read_bytes()
    uni_items.append(("UNIVERSAL_PROMPT.md", uni_prompt_bytes))
    for root_rel in [
        "LICENSE",
        "THIRD_PARTY_NOTICES.md",
        "LICENSES/mromidev-claude-animated-shorts-MIT.txt",
        "LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt",
        "docs/INSTALL.md",
        "docs/COMPATIBILITY.md",
        "docs/TROUBLESHOOTING.md",
        "docs/LIMITATIONS.md",
    ]:
        p = repo_root / root_rel
        if p.is_file():
            uni_items.append((root_rel, p.read_bytes()))

    examples_dir = repo_root / "examples"
    if examples_dir.is_dir():
        for ex in sorted(examples_dir.rglob("*")):
            if ex.is_file() and ex.suffix.lower() in TEXT_EXTS:
                rel = ex.relative_to(repo_root).as_posix()
                uni_items.append((rel, ex.read_bytes()))

    out_dir.mkdir(parents=True, exist_ok=True)
    agensi_zip = out_dir / f"youtube-creator-skill-agensi-v{version}.zip"
    uni_zip = out_dir / f"youtube-creator-skill-universal-v{version}.zip"
    prompt_copy = out_dir / "UNIVERSAL_PROMPT.md"
    prompt_copy.write_bytes(uni_prompt_bytes)

    agensi_meta = _write_deterministic_zip(agensi_zip, agensi_items)
    uni_meta = _write_deterministic_zip(uni_zip, uni_items)

    repro_verified = False
    if verify_repro:
        with tempfile.TemporaryDirectory(prefix="yt_repro_") as td:
            a2 = _write_deterministic_zip(Path(td) / "a2.zip", agensi_items)
            u2 = _write_deterministic_zip(Path(td) / "u2.zip", uni_items)
            if a2["sha256"] != agensi_meta["sha256"] or u2["sha256"] != uni_meta["sha256"]:
                raise RuntimeError("Reproducibility check FAILED: independent build hashes diverged.")
            repro_verified = True

    extract_check = _verify_extracted_agensi(agensi_zip, repo_root)

    # Determine git HEAD commit if committed
    commit_proc = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "HEAD"], capture_output=True, text=True)
    commit_sha = commit_proc.stdout.strip() if commit_proc.returncode == 0 else "UNCOMMITTED_WORKING_TREE"
    dirty_proc = subprocess.run(["git", "-C", str(repo_root), "status", "--porcelain"], capture_output=True, text=True)
    is_dirty = bool(dirty_proc.stdout.strip()) if dirty_proc.returncode == 0 else True

    prompt_sha = _sha256_bytes(uni_prompt_bytes)
    checksums_lines = [
        f"{agensi_meta['sha256']}  {agensi_meta['filename']}",
        f"{uni_meta['sha256']}  {uni_meta['filename']}",
        f"{prompt_sha}  UNIVERSAL_PROMPT.md",
    ]
    (out_dir / "SHA256SUMS.txt").write_text("\n".join(checksums_lines) + "\n", encoding="utf-8", newline="\n")

    notes = _release_notes_text(version, commit_sha, agensi_meta, uni_meta, prompt_sha)
    (out_dir / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8", newline="\n")

    manifest = {
        "schema_version": "1.0.0",
        "project": "youtube-creator-skill",
        "version": version,
        "release_type": "RELEASE_CANDIDATE" if "-rc." in version else "STABLE",
        "source_commit": commit_sha,
        "working_tree_dirty": is_dirty,
        "reproducible_verified": repro_verified,
        "agensi_extraction_verified": extract_check,
        "artifacts": {
            "agensi_zip": agensi_meta,
            "universal_zip": uni_meta,
            "universal_prompt": {
                "filename": "UNIVERSAL_PROMPT.md",
                "size_bytes": len(uni_prompt_bytes),
                "sha256": prompt_sha,
            },
        },
    }
    (out_dir / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build deterministic Agensi and Universal release packages.")
    parser.add_argument("--version", default="1.0.0-rc.2")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "dist"))
    parser.add_argument("--verify", action="store_true", help="Verify byte-for-byte reproducibility via second build.")
    args = parser.parse_args(argv)

    manifest = build_release(Path(args.repo_root), args.version, Path(args.out_dir), verify_repro=args.verify)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
