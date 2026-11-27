#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 quocan050302
"""Bounded parallel QA gate runner with real command capture and fail-closed reporting."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent


def _resolve_workers() -> int:
    cpu = os.cpu_count() or 1
    cap = min(4, cpu)
    env_val = os.environ.get("YT_WORKERS")
    if env_val:
        try:
            return max(1, min(cap, int(env_val)))
        except ValueError:
            return 1
    return cap


def _tree_hash(repo_root: Path) -> str:
    h = hashlib.sha256()
    for folder in ["skills", "tools", "tests", "docs", "examples", "LICENSES"]:
        base = repo_root / folder
        if not base.is_dir():
            continue
        for fp in sorted(base.rglob("*")):
            if fp.is_file() and "__pycache__" not in fp.parts:
                h.update(fp.relative_to(repo_root).as_posix().encode("utf-8"))
                h.update(fp.read_bytes())
    for top in ["LICENSE", "THIRD_PARTY_NOTICES.md", "README.md"]:
        p = repo_root / top
        if p.is_file():
            h.update(top.encode("utf-8"))
            h.update(p.read_bytes())
    return h.hexdigest()


def capture_result(task: dict[str, Any], repo_root: Path, logs_dir: Path, tree_sha: str) -> dict[str, Any]:
    tid = task["test_id"]
    cmd = task["command"]
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=task.get("timeout_s", 120),
        check=False,
    )
    dur_ms = round((time.perf_counter() - t0) * 1000, 1)
    stdout_path = logs_dir / f"{tid}.stdout.log"
    stderr_path = logs_dir / f"{tid}.stderr.log"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    status = "PASS" if proc.returncode == 0 else "FAIL"
    return {
        "test_id": tid,
        "gate": task["gate"],
        "required": task.get("required", True),
        "command": cmd,
        "started_at": started,
        "duration_ms": dur_ms,
        "exit_code": proc.returncode,
        "status": status,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "python_version": sys.version.split()[0],
        "tree_hash": tree_sha,
    }


def run_tasks_bounded(tasks: list[dict[str, Any]], repo_root: Path, logs_dir: Path, workers: int) -> list[dict[str, Any]]:
    logs_dir.mkdir(parents=True, exist_ok=True)
    tree_sha = _tree_hash(repo_root)
    results_by_id: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        fut_map = {ex.submit(capture_result, t, repo_root, logs_dir, tree_sha): t["test_id"] for t in tasks}
        for fut in concurrent.futures.as_completed(fut_map):
            res = fut.result()
            results_by_id[res["test_id"]] = res
    # Stable deterministic order matching input task list
    return [results_by_id[t["test_id"]] for t in tasks]


def aggregate_gates(results: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0, "NOT_RUN": 0}
    required_failures: list[str] = []
    for r in results:
        st = r["status"]
        counts[st] = counts.get(st, 0) + 1
        if r.get("required", True) and st != "PASS":
            required_failures.append(r["test_id"])
    return {
        "overall_status": "PASS" if not required_failures else "FAIL",
        "counts": counts,
        "required_failures": required_failures,
        "results": results,
    }


def write_report(report: dict[str, Any], out_json: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded deterministic QA suite (fail closed).")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--version", default="1.0.0-rc.3")
    parser.add_argument("--run-dir", default=None, help="Directory to store qa-results.json and logs/.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root)
    workers = _resolve_workers()
    out_base = Path(args.run_dir) if args.run_dir else (repo_root / ".cache" / "qa-last")
    logs_dir = out_base / "logs"

    py = sys.executable
    # Stage 1: Independent read-only checks (bounded parallel)
    stage1_tasks = [
        {"test_id": "validate_skill", "gate": "G2", "command": [py, "tools/validate_skill.py"]},
        {"test_id": "audit_licenses", "gate": "G1", "command": [py, "tools/audit_licenses.py"]},
        {"test_id": "unit_and_integration_tests", "gate": "G3_G4_G7_G8", "command": [py, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]},
    ]
    stage1_res = run_tasks_bounded(stage1_tasks, repo_root, logs_dir, workers)

    # Stage 2: Deterministic release build & universal prompt parity check (sequential to avoid file contention)
    stage2_tasks = [
        {"test_id": "build_release_repro", "gate": "G9", "command": [py, "tools/build_release.py", "--version", args.version, "--verify"]},
        {"test_id": "check_universal_prompt_parity", "gate": "G6", "command": [py, "tools/build_universal_prompt.py", "--check"]},
        {"test_id": "re_audit_licenses_after_build", "gate": "G1", "command": [py, "tools/audit_licenses.py"]},
    ]
    stage2_res = run_tasks_bounded(stage2_tasks, repo_root, logs_dir, workers=1)

    all_res = stage1_res + stage2_res
    agg = aggregate_gates(all_res)
    agg["workers_used"] = workers
    agg["version"] = args.version
    agg["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_report(agg, out_base / "qa-results.json")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(agg, indent=2, ensure_ascii=False))
    return 0 if agg["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
