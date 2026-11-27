# Source Provenance & Clean-Room Ledger

This document records the exact upstream commits, license files, derivations,
and exclusions audited before implementing `youtube-creator-skill`. All entries
match the machine-readable ledger in [`docs/provenance.json`](provenance.json).

## Upstream Sources Audited

| Source ID | Repository | Pinned Commit | License | Verbatim Notice File |
|---|---|---|---|---|
| `upstream-a` | https://github.com/mromidev/claude-animated-shorts | `e3b817b6afc6cd413466d43f11ba31209e034bbf` | MIT (`Copyright (c) 2026 Mr omi`) | `LICENSES/mromidev-claude-animated-shorts-MIT.txt` |
| `upstream-b` | https://github.com/jakeschincariol/youtube-agent-skill | `a2feb2104981a375ffd4f87ee04f4f5344ac43c6` | MIT (`Copyright (c) 2026 Jake Schincariol`) | `LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt` |
| `original` | https://github.com/quocan050302/youtube-creator-skill | Current repo | MIT (`Copyright (c) 2026 quocan050302`) | `LICENSE` |

## File & Concept Disposition Table

| Source ID | Source Path | Disposition | Destination Path | Redistribution Status | Summary & Rationale |
|---|---|---|---|---|---|
| `upstream-a` | `LICENSE` | `COPY` | `LICENSES/mromidev-claude-animated-shorts-MIT.txt` | `CLEARED_MIT` | Exact byte-faithful upstream MIT license text (`git show HEAD:LICENSE`). |
| `upstream-a` | `SKILL.md` | `DERIVE` | `skills/youtube-creator-skill/references/storytelling-engine.md`, `visual-packaging.md` | `CLEARED_CONCEPTUAL` | Derived abstract narrative escalation, deadpan contrast, everyday analogy, consequence/callback, and beat-to-visual planning principles. No rendering pipeline or bridge specifics copied. |
| `upstream-a` | `references/STYLE_BIBLE.md` | `DERIVE` | `skills/youtube-creator-skill/references/storytelling-engine.md` | `CLEARED_CONCEPTUAL` | Derived general storytelling pacing mechanics; attributed historical 20-Short observation study explicitly as upstream historical note rather than universal rule or original measurement. |
| `upstream-a` | `templates/bridge/story.ts`, `templates/audio/cues.md` | `DERIVE` | `skills/youtube-creator-skill/references/visual-packaging.md` | `CLEARED_CONCEPTUAL` | Extracted abstract beat-to-visual and optional sound-cue intent concepts only; zero TypeScript/Remotion/audio DSP code copied. |
| `upstream-a` | `templates/SCRIPT_example.md` | `EXCLUDE` | *(none)* | `EXCLUDED_BY_POLICY` | Inspected internally for abstract beat arc only; verbatim bridge story text excluded in favor of newly authored original demos. |
| `upstream-a` | `references/frames/*`, `references/sheets/*`, `references/reports/*` | `EXCLUDE` | *(none)* | `EXCLUDED_THIRD_PARTY_MEDIA` | Private third-party visual study frames, contact sheets, and reports strictly excluded from checkout and distribution. |
| `upstream-a` | `templates/bridge/*` (except abstract read), `templates/audio/*.py`, `templates/scripts/*` | `EXCLUDE` | *(none)* | `EXCLUDED_OUT_OF_SCOPE` | Three.js/Remotion rendering engine, character rigs, and audio synthesis DSP excluded; this skill is text-and-analytics only. |
| `upstream-b` | `LICENSE` | `COPY` | `LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt` | `CLEARED_MIT` | Exact byte-faithful upstream MIT license text (`git show HEAD:LICENSE`). |
| `upstream-b` | `skills/yt-script/hooks.json` | `MODIFY` | `skills/youtube-creator-skill/assets/hooks.json` | `CLEARED_MIT` | Preserved all 21 upstream hook formula IDs, shapes, examples, failure modes, and regex patterns with explicit MIT provenance metadata and embedded parity copies inside standalone scripts. |
| `upstream-b` | `skills/yt-script/hookscore.py` | `MODIFY` | `skills/youtube-creator-skill/scripts/hookscore.py` | `CLEARED_MIT` | Refactored for standalone isolated execution (zero sibling file reads), stdin/file CLI, POV-neutral Shorts story mode, input bounds, and explicit heuristic rubric limitations. |
| `upstream-b` | `skills/yt-package/title.py` | `MODIFY` | `skills/youtube-creator-skill/scripts/title_linter.py` | `CLEARED_MIT` | Refactored with Unicode tokenization, multi-thumbnail comparison, non-prescriptive concrete-detail advice, and explicit heuristic truncation caveats. |
| `upstream-b` | `skills/yt-viral/swipe.py` | `MODIFY` | `skills/youtube-creator-skill/scripts/outlier_analyzer.py` | `CLEARED_MIT` | Refactored with leave-one-out peer median, format & age cohort partitioning, URL/ID deduplication, null-safe missing handling, and embedded 21-formula classification. |
| `upstream-b` | `skills/yt-retention/retention.py` | `MODIFY` | `skills/youtube-creator-skill/scripts/retention.py` | `CLEARED_MIT` | Refactored for zero sibling imports, configurable Shorts/Long early windows, percentage-point delta reporting, valid >100% loop support, robust cliff detection, and non-causal transcript alignment. |
| `upstream-b` | `skills/yt-edit/deadair.py` | `MODIFY` | `skills/youtube-creator-skill/scripts/transcript_analyzer.py` | `CLEARED_MIT` | Refactored with strict SRT/VTT/JSON validation, overlap checks, stdin support, and explicit distinction between transcript gaps and verified audio silence. |
| `upstream-b` | `skills/yt-chapters/chapters.py` | `MODIFY` | `skills/youtube-creator-skill/scripts/chapters.py` | `CLEARED_MIT` | Refactored for zero sibling imports, `00:00` compliance, direct chapter validation mode, and YouTube official chapter rule checks (start `00:00`, >=3 chapters, >=10s each, ascending). |
| `upstream-b` | `skills/yt-*/SKILL.md`, `templates/voice.md` | `DERIVE` | `skills/youtube-creator-skill/SKILL.md`, `references/*.md`, `assets/creator-profile-template.md` | `CLEARED_MIT` | Unified 11 separate skills into one canonical router skill; removed Claude-specific global paths and mandatory 3-video prerequisites. |
| `upstream-b` | `.claude-plugin/*` | `EXCLUDE` | *(none)* | `EXCLUDED_ARCHITECTURE` | Claude-specific plugin wrapper excluded in favor of cross-client Agent Skills standard. |
| `local-audit` | Local installed skill environments | `EXCLUDE` | *(none)* | `EXCLUDED_PRIVATE_LOCAL` | Local installed plugins were audited read-only for compatibility context; no private local files, paths, or rendering presets were imported into this public repository. All cross-platform UTF-8, POV-neutral hook, multi-thumbnail, and Shorts-window features were cleanly implemented in the new MIT codebase. |

## Official Specifications Checked (2026-11-27)

| Specification | URL | Verification Status |
|---|---|---|
| Agent Skills Open Specification | https://agentskills.io/specification | Verified live HTTP 200 (2026-11-27) |
| Agensi Packaging Docs | https://www.agensi.io/docs/packaging | Verified live HTTP 200 (2026-11-27) |
| Agensi Creator FAQ | https://www.agensi.io/docs/creator-faq | Verified live HTTP 200 (2026-11-27) |
| OSI MIT License | https://opensource.org/license/mit | Verified live HTTP 200 (2026-11-27) |
| Google Antigravity Skills Docs | https://antigravity.google/docs/skills | Verified via official docs search (2026-11-27) |
| Claude Code Skills Docs | https://code.claude.com/docs/en/skills | Verified via official docs search (2026-11-27) |
| OpenAI Codex Skills Docs | https://developers.openai.com/plugins/concepts/skills | Verified via official docs search (2026-11-27) |
| YouTube Help (Chapters & Shorts Views / Engaged Views) | https://support.google.com/youtube/ | Verified via official docs search (2026-11-27) |
