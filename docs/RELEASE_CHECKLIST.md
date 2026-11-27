# Release Checklist & Quality Gates (G0–G10)

Never tag stable `v1.0.0` or advertise certified multi-client compatibility unless all mandatory gates pass with verifiable command logs. Use `-rc.N` consistently when external gates remain pending.

| Gate | Requirement | Automated Check / Evidence |
|---|---|---|
| **G0 — Scope & Provenance** | Target remote verified (`quocan050302/youtube-creator-skill`), upstream commits pinned, local audit documented cleanly | `01_SOURCE_INVENTORY.md`, `docs/provenance.json` |
| **G1 — MIT Compliance** | Verbatim upstream MIT texts in root, skill dir, both ZIPs, and `UNIVERSAL_PROMPT.md`; zero unauthorized media or private paths | `python tools/audit_licenses.py` |
| **G2 — Agent Skills Spec** | Single canonical `SKILL.md` (`youtube-creator-skill`), valid frontmatter, all links exist, `<= 250` lines target, standalone safe scripts | `python tools/validate_skill.py` |
| **G3 — Deterministic Code** | All unit tests + standalone empty-temp-dir subprocess tests pass for all 7 scripts | `python -m unittest discover -s tests -p "test_*.py" -v` |
| **G4 — Data Integrity** | Leave-one-out peer median, cohort isolation, null != 0, >100% retention allowed, CSV formula safety, regression fixtures pass | `tests/unit/test_outlier_analyzer.py`, `test_retention.py`, `test_validate_output.py` |
| **G5 — Creative & Behavioral** | >=30 frozen scenarios (>=10 holdout, >=10 niches), fresh-context agent eval runs scored honestly on 0–2 rubric (>=85%, zero critical fails) | `tools/run_evals.py`, `06_BEHAVIOR_EVAL.md` |
| **G6 — Compatibility** | Live native execution on Antigravity, Codex, Claude Code + 3 chat runtimes + isolated script sandbox (documented paths alone != PASS) | `docs/COMPATIBILITY.md`, `07_COMPATIBILITY_MATRIX.md` |
| **G7 — Security & Privacy** | Prompt injection isolation, no secrets/exfiltration, no network/subprocess in scripts, safe archive paths | `tests/integration/test_security_and_packaging.py` |
| **G8 — Output UX & Parity** | Creator Action Pack v1.0.0 schema, cross-file parity (`SCRIPT.txt`, `STORYBOARD.csv`, `TITLE_HOOKS.md`, JSON), exact calendar counts | `scripts/validate_output.py` on all `examples/*` |
| **G9 — Reproducible Packaging** | Byte-for-byte reproducible Agensi & Universal ZIPs, extracted skill validation, SHA-256 manifest, clean commit binding | `python tools/build_release.py --version <ver> --verify` |
| **G10 — Independent Review & Release** | Independent review evidence, remote GitHub Actions CI green on final SHA, owner approval for PR merge, tag, and Agensi upload | Remote CI run + Owner sign-off |

## Safe Rollback Procedure
Never use `git reset --hard` or `git push --force` on shared branches:
1. Revert a bad commit cleanly: `git revert <commit_sha>` and push normally.
2. Never overwrite or delete an already published release tag; ship a new patch version (`v1.0.1` or `v1.0.0-rc.2`).
