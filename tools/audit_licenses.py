#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Audit MIT licenses, byte parity of upstream notices, SPDX headers, and provenance ledger."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_UPSTREAM_LICENSES = {
    "LICENSES/mromidev-claude-animated-shorts-MIT.txt": {
        "sha256": "0c88b6c1afe23ba94a2326eb289868fa4bb24edfd6994ad0c6bb7f2f2ed517e2",
        "copyright": "Copyright (c) 2026 Mr omi",
    },
    "LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt": {
        "sha256": "857c8d5276809c8196b3cd7cb3300324768bfc562b2b6281b06d6865058e186c",
        "copyright": "Copyright (c) 2026 Jake Schincariol",
    },
}

REQUIRED_MIRROR_FILES = [
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "LICENSES/mromidev-claude-animated-shorts-MIT.txt",
    "LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt",
]

DISALLOWED_PUBLIC_PATTERNS = [
    "C:\\Users\\",
    "C:/Users/",
    "/Users/",
    "QuocAn",
    "DaKhoaIvyHealth",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_license_audit(repo_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked_hashes: dict[str, str] = {}

    # 1. Root LICENSE & THIRD_PARTY_NOTICES.md
    root_lic = repo_root / "LICENSE"
    if not root_lic.is_file():
        errors.append("Missing root LICENSE file.")
    else:
        txt = root_lic.read_text(encoding="utf-8")
        if "MIT License" not in txt or "Permission is hereby granted, free of charge" not in txt:
            errors.append("Root LICENSE missing full MIT license text.")
        checked_hashes["LICENSE"] = _sha256(root_lic)

    tpn = repo_root / "THIRD_PARTY_NOTICES.md"
    if not tpn.is_file():
        errors.append("Missing THIRD_PARTY_NOTICES.md.")
    else:
        tpn_txt = tpn.read_text(encoding="utf-8")
        for req_str in [
            "e3b817b6afc6cd413466d43f11ba31209e034bbf",
            "a2feb2104981a375ffd4f87ee04f4f5344ac43c6",
            "Copyright (c) 2026 Mr omi",
            "Copyright (c) 2026 Jake Schincariol",
        ]:
            if req_str not in tpn_txt:
                errors.append(f"THIRD_PARTY_NOTICES.md missing required attribution string: {req_str}")
        checked_hashes["THIRD_PARTY_NOTICES.md"] = _sha256(tpn)

    # 2. Upstream verbatim MIT license byte-for-byte SHA-256 verification
    for rel, expected in EXPECTED_UPSTREAM_LICENSES.items():
        p = repo_root / rel
        if not p.is_file():
            errors.append(f"Missing verbatim upstream license file: {rel}")
            continue
        actual_hash = _sha256(p)
        checked_hashes[rel] = actual_hash
        if actual_hash != expected["sha256"]:
            errors.append(f"Byte parity mismatch on {rel}: expected {expected['sha256']}, got {actual_hash}")
        if expected["copyright"] not in p.read_text(encoding="utf-8"):
            errors.append(f"Missing upstream copyright line in {rel}: {expected['copyright']}")

    # 3. Canonical skill folder mirror parity
    skill_root = repo_root / "skills" / "youtube-creator-skill"
    for rel in REQUIRED_MIRROR_FILES:
        src = repo_root / rel
        dst = skill_root / rel
        if not dst.is_file():
            errors.append(f"Skill directory missing mirrored notice file: skills/youtube-creator-skill/{rel}")
        elif src.is_file() and _sha256(src) != _sha256(dst):
            errors.append(f"Mirror hash drift between root {rel} and skills/youtube-creator-skill/{rel}")

    # 4. Machine-readable provenance ledger check
    prov_path = repo_root / "docs" / "provenance.json"
    if not prov_path.is_file():
        errors.append("Missing docs/provenance.json.")
    else:
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
        entries = prov.get("entries", [])
        if not entries:
            errors.append("docs/provenance.json contains zero entries.")
        for idx, e in enumerate(entries):
            if e.get("disposition") == "UNKNOWN" or e.get("redistribution_status") == "UNKNOWN":
                errors.append(f"Provenance entry {idx} has UNKNOWN disposition/redistribution status (hard blocker).")
            dest = e.get("destination_path")
            if e.get("disposition") in {"COPY", "MODIFY", "DERIVE"} and dest:
                if not (repo_root / dest).exists():
                    errors.append(f"Provenance destination missing on disk: {dest}")

    # 5. Adapted Python scripts SPDX & upstream attribution header check
    scripts_dir = skill_root / "scripts"
    for sp in sorted(scripts_dir.glob("*.py")):
        head = "\n".join(sp.read_text(encoding="utf-8").splitlines()[:12])
        if "SPDX-License-Identifier: MIT" not in head:
            errors.append(f"Script missing SPDX-License-Identifier: MIT header: {sp.name}")

    # 6. Universal prompt notice check (if generated)
    uni_path = repo_root / "universal" / "UNIVERSAL_PROMPT.md"
    if uni_path.is_file():
        uni_txt = uni_path.read_text(encoding="utf-8")
        for req_str in [
            "Copyright (c) 2026 quocan050302",
            "Copyright (c) 2026 Mr omi",
            "Copyright (c) 2026 Jake Schincariol",
            "THE SOFTWARE IS PROVIDED \"AS IS\"",
        ]:
            if req_str not in uni_txt:
                errors.append(f"universal/UNIVERSAL_PROMPT.md missing required MIT notice text: {req_str}")
    else:
        warnings.append("universal/UNIVERSAL_PROMPT.md not generated yet.")

    # 7. Public leak check (private local paths must not appear in public repo files)
    scan_dirs = ["skills", "docs", "universal", "examples", "tools", ".github"]
    scan_files = [repo_root / f for f in ["README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md"] if (repo_root / f).is_file()]
    for sd in scan_dirs:
        pdir = repo_root / sd
        if pdir.is_dir():
            for fp in pdir.rglob("*"):
                if fp.is_file() and fp.suffix.lower() in {".md", ".py", ".json", ".txt", ".csv", ".yml", ".yaml"}:
                    if fp.name == "audit_licenses.py":
                        continue
                    scan_files.append(fp)

    for fp in scan_files:
        content = fp.read_text(encoding="utf-8", errors="replace")
        for pat in DISALLOWED_PUBLIC_PATTERNS:
            if pat in content:
                errors.append(f"Private/local path string {pat!r} leaked into public file: {fp.relative_to(repo_root)}")

    return {
        "tool": "audit_licenses.py",
        "valid": len(errors) == 0,
        "checked_hashes": checked_hashes,
        "errors": errors,
        "warnings": warnings,
        "note": "Automated MIT/provenance verification only; final legal sign-off remains owner responsibility.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit MIT licenses and provenance ledger.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    report = run_license_audit(Path(args.repo_root))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
