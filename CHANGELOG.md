# Changelog

All notable changes to `youtube-creator-skill` (YouTube Creator Intelligence)
will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
