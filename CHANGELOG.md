# Changelog

All notable changes to `youtube-creator-skill` (YouTube Creator Intelligence)
will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-rc.4] - 2026-11-27

**Status:** Release Candidate Micro-Fix (`FINAL MICRO-FIX — RETENTION UNIT PRECEDENCE`; external multi-client certification and owner publication approval remain pending).

### Fixed
- **`scripts/retention.py` Unit Precedence (`parse_curve`, `normalize_time`, `normalize_rate`):** Enforced strict unit precedence order **`CLI explicit > explicit CSV header / JSON key > warned inference`**, returning exit code `2` on ambiguous or contradictory units/keys.
  - Preserved CSV `retention_pct` small values (e.g., `1, 0.8, 0.5`) in percent without multiplying by `100` (while explicit `--rate-unit ratio` or `retention_ratio` scales `x100`).
  - Propagated explicit JSON x/y keys across object lists, `{"points": [...]}`, and columnar array objects so JSON `time_s = [0, 50, 100]` (`duration=120`) retains `[0.0, 100.0]s` and JSON `pct = [0, 20, 40]` (`duration=200`) converts to `[0.0, 80.0]s`.
  - Rejected conflicting/mixed JSON keys, contradictory headers (`seconds_pct`, `retention_pct_ratio`), header-vs-`%` mismatches, and ambiguous unitless axes cleanly with exit code `2`.

## [1.0.0-rc.3] - 2026-11-27

**Status:** Release Candidate Hotfix (`YT-01.R1.A6.HOTFIX` — Final Data Integrity; external multi-client certification and owner publication approval remain pending).

### Fixed
- **FIX-01 — `scripts/retention.py` CSV Column Integrity (`parse_curve`):** Replaced generic numeric-cell scanning with strict header-based column resolution (supporting reordered columns, rejecting ambiguous headers, and enforcing exact 2-column positional parsing for headerless CSVs). When either resolved x/time or y/retention cell is missing, `NaN`, or `Infinity`, the entire row is skipped (`rows_skipped` incremented) instead of shifting into adjacent columns such as `views`.
- **FIX-02 — `scripts/retention.py` Axis Detection (`normalize_time`):** Restricted `auto` percent-axis detection strictly to the resolved x/time column header (`x_header`) and x-cell `%` markers so `percent` inside the y-column header (e.g., `time_s,retention_percent`) never misclassifies a seconds axis as normalized percentage.
- **FIX-03 — `scripts/retention.py` Transcript JSON Parser (`_load_transcript_text`):** Checked `isinstance(data, list)` before calling `.get()`, cleanly supporting top-level JSON cue arrays, `{"segments": [...]}` objects, and `{"words": [...]}` objects while raising clear `ValueError` diagnostics on malformed structures instead of `AttributeError`.
- **FIX-04 — Hook Timing Precision & Format Consistency (`scripts/hookscore.py`, `SKILL.md`, `references/hook-engine.md`):** Separated `fits_3s_at_150_wpm` (`<= 7` words = `2.8s`; `9` words = `3.6s`), `fits_3s_at_180_wpm` (`<= 9` words = `3.0s`), and `fits_3s_at_200_wpm` (`<= 10` words); added `--format {SHORT,LONG}` so Shorts `0–3s` timing gates apply consistently to both `direct` and `narrative` Shorts without being applied mechanically to Long-form openings.

## [1.0.0-rc.2] - 2026-11-27

**Status:** Release Candidate (remediation pass from YT-01.T1 independent acceptance test; external multi-client certification and owner publication approval remain pending).

### Fixed & Hardened
- **Release Workflow Security & Reliability (`.github/workflows/release.yml`):** Eliminated direct `${{ inputs.version }}` bash shell interpolation, added strict semver validation, pinned `target_sha` verification, stable external-gate guard against unverified non-RC tags, and added explicit `--repo` + `--target` flags in `publish-github-release`.
- **0–3s Shorts Spoken Hook Gate (`SKILL.md`, `references/hook-engine.md`, `scripts/hookscore.py`, `examples/01-science-short-copper-magnet/`):** Added explicit `est_spoken_sec_150_wpm`, `est_spoken_sec_180_wpm`, and `fits_3s_first_line` checks in `hookscore.py` with rubric capping on >10-word Shorts openers; updated shipped Demo 01 first spoken line to an authentic 8-word `0–3s` opener.
- **Creator-Facing Copy Cleanliness (`SKILL.md`, `references/output-contract.md`, `references/quality-gates.md`):** Restricted internal QA/schema enums and editing reminders from leaking into `Recommended Action` or pasteable upload/prompt blocks, and enforced fictional-dataset framing hygiene.
- **Standalone Script Hardening:**
  - `scripts/retention.py`: Exposed `dropped_invalid_rows` and emitted explicit warnings whenever `NaN`/non-numeric rows are skipped as missing.
  - `scripts/hookscore.py` & `scripts/title_linter.py`: Fail closed (`exit 2`) on malformed `.json` files instead of silently scoring broken JSON text.
  - `scripts/validate_output.py` & `scripts/chapters.py --validate`: Return exit code `1` when `"valid": false` (exit `0` only on valid input, exit `2` on IO/syntax errors).
- **Universal Prompt & Spec Validator Parity:** Expanded `tools/build_universal_prompt.py` to bundle all 21 canonical references with an automated guard against dangling `"section below"` mentions; updated `tools/validate_skill.py` to check bare `.md` routing-table links; added `python3` macOS/Linux commands to `docs/INSTALL.md` and synced test paths in `docs/RELEASE_CHECKLIST.md`.

## [1.0.0-rc.1] - 2026-11-27

**Status:** Release Candidate (pending external multi-client native certification
on Codex/Claude Code, remote CI green run, and owner publication approval).

### Added
- **Canonical Agent Skill (`skills/youtube-creator-skill/SKILL.md`):**
  Single-source-of-truth router supporting 17 creator intents across Shorts and
  Long-form, capability auto-detection (`TEXT_ONLY`, `FILE_READ`, `FILE_WRITE`,
  `WEB`, `CODE`, `VISION`, `AUDIO/VIDEO`, `MCP`), and compact/full output UX.
- **21 Modular Reference Guides (`references/`):**
  Covers master routing, capability matrix, portable creator profile, research
  and fact verification, cohort-safe competitor outlier analysis, topic strategy,
  TT-01 Title Curiosity Gate, Hook Lab (21 attributed formulas + heuristic rubric),
  KH-01 10-niche Storytelling & Script Engine, humor & analogy guardrails, visual
  packaging & edit intelligence, analytics truth model (Shorts views vs engaged
  views, retention curve analysis), channel audit & continuous learning loop,
  capacity-aware content planning, Long-to-Short repurposing, SEO/comments/chapters,
  quality gates, and output contract.
- **7 Standalone Stdlib Python Tools (`scripts/`):**
  `hookscore.py`, `title_linter.py`, `outlier_analyzer.py`, `retention.py`,
  `transcript_analyzer.py`, `chapters.py`, and `validate_output.py` — zero
  third-party dependencies, zero sibling-file imports (isolated temp-file ready
  for Agensi), stdin/file CLI, structured JSON output, and strict error codes.
- **Templates & Assets (`assets/`):**
  Attributed `hooks.json` (21 formulas), `output-schema.json` (v1.0.0), portable
  `creator-profile-template.md`, CSV templates for storyboards, analytics,
  channel history, and content plans, plus `experiment-log-template.md`.
- **Universal Prompt Distribution (`universal/UNIVERSAL_PROMPT.md`):**
  Deterministically generated self-contained prompt with embedded MIT notices
  for text-only chat interfaces.
- **Build, Audit & QA Tooling (`tools/`):**
  `build_universal_prompt.py`, `build_release.py` (deterministic reproducible
  Agensi + Universal ZIPs), `validate_skill.py`, `audit_licenses.py`,
  `run_qa.py`, and `run_evals.py`.
- **Compliance & Provenance:**
  Root `LICENSE` (MIT), verbatim upstream MIT texts in `LICENSES/`,
  `THIRD_PARTY_NOTICES.md`, `docs/PROVENANCE.md`, and machine-readable
  `docs/provenance.json`.
- **Original Demo Packs & Documentation (`examples/`, `docs/`):**
  Three original rights-cleared demos (Magnet/Copper Science Short, Reshipping
  Scam Awareness Short, Synthetic Shorts/Long Retention & Audit Pack), full
  install/compatibility/troubleshooting/limitations guides, and Agensi listing
  handover pack.
