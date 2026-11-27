# Third-Party Notices

`youtube-creator-skill` (YouTube Creator Intelligence) is distributed under the
MIT License (`LICENSE`). Portions of its reference formulas, conceptual
storytelling structures, and optional Python utilities are adapted from or
inspired by the MIT-licensed open-source repositories below. Neither upstream
author endorses, sponsors, or is affiliated with this project.

---

## 1. `jakeschincariol/youtube-agent-skill`

- **Repository:** https://github.com/jakeschincariol/youtube-agent-skill
- **Pinned Commit Audited:** `a2feb2104981a375ffd4f87ee04f4f5344ac43c6`
- **License:** MIT License
- **Upstream Copyright Notice:** `Copyright (c) 2026 Jake Schincariol`
- **Verbatim Upstream License File:** [`LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt`](LICENSES/jakeschincariol-youtube-agent-skill-MIT.txt) (SHA-256: `857c8d5276809c8196b3cd7cb3300324768bfc562b2b6281b06d6865058e186c`, Git blob: `ac31f09aba721de8d139c7bef3d5024421426472`)
- **Reused / Adapted Material:**
  - `skills/yt-script/hooks.json` -> adapted into `skills/youtube-creator-skill/assets/hooks.json` (all 21 formula IDs preserved with provenance metadata; also embedded as self-contained lookup tables in `hookscore.py` and `outlier_analyzer.py` for isolated single-file execution).
  - `skills/yt-script/hookscore.py` -> heavily refactored into `skills/youtube-creator-skill/scripts/hookscore.py` (standalone zero-sibling execution, stdin/file CLI, POV-neutral Shorts story mode, transparent heuristic breakdown, strict input validation).
  - `skills/yt-package/title.py` -> heavily refactored into `skills/youtube-creator-skill/scripts/title_linter.py` (Unicode-safe tokenization, multi-thumbnail comparison, non-prescriptive number advice, heuristic truncation cautions).
  - `skills/yt-viral/swipe.py` -> heavily refactored into `skills/youtube-creator-skill/scripts/outlier_analyzer.py` (leave-one-out peer median, format & age cohort separation, deduplication, missing-value exclusion instead of zero coercion, stable tie-breaking).
  - `skills/yt-retention/retention.py` -> heavily refactored into `skills/youtube-creator-skill/scripts/retention.py` (standalone transcript alignment, configurable Shorts/Long early windows, percentage-point vs relative delta clarity, valid >100% loop/rewatch support, non-causal framing).
  - `skills/yt-edit/deadair.py` -> heavily refactored into `skills/youtube-creator-skill/scripts/transcript_analyzer.py` (SRT/VTT/JSON validation, overlap & non-monotonic checks, explicit distinction between transcript gaps and measured audio silence).
  - `skills/yt-chapters/chapters.py` -> heavily refactored into `skills/youtube-creator-skill/scripts/chapters.py` (standalone parser, chapter validation mode + draft boundary mode, `00:00` formatting, current YouTube rules).
  - Conceptual workflow inspiration from `skills/yt-*/SKILL.md` and `templates/voice.md` unified into a single canonical skill (`skills/youtube-creator-skill/SKILL.md` and `references/*.md`), removing Claude-specific paths and mandatory 3-video onboarding gates.
- **Explicitly Excluded:**
  - `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json` (platform-specific plugin wrapper not reused as architecture).

---

## 2. `mromidev/claude-animated-shorts`

- **Repository:** https://github.com/mromidev/claude-animated-shorts
- **Pinned Commit Audited:** `e3b817b6afc6cd413466d43f11ba31209e034bbf`
- **License:** MIT License
- **Upstream Copyright Notice:** `Copyright (c) 2026 Mr omi`
- **Verbatim Upstream License File:** [`LICENSES/mromidev-claude-animated-shorts-MIT.txt`](LICENSES/mromidev-claude-animated-shorts-MIT.txt) (SHA-256: `0c88b6c1afe23ba94a2326eb289868fa4bb24edfd6994ad0c6bb7f2f2ed517e2`, Git blob: `4b9fa4c5f3a33ee73c5f96437252b6191a04cba6`)
- **Derived Conceptual Principles (No Code or Assets Copied):**
  - Abstract narrative pacing principles inspired by `SKILL.md` and `references/STYLE_BIBLE.md` (surprising observable premise, escalating beats, deadpan contrast, everyday analogy for technical/physical mechanisms, consequence and callback payoff, non-redundant visual-vs-narration pairing, and beat-to-visual/audio cue planning).
  - Historical sample metrics noted in `STYLE_BIBLE.md` (20-Short observation study, ~3.5-4.1 words/s) are attributed strictly as an upstream historical study note, never as a universal default or original measurement by this repository.
- **Explicitly Excluded (Zero Redistribution):**
  - `references/frames/*`, `references/sheets/*`, `references/reports/*` (private visual study frames/sheets/reports with third-party media).
  - `templates/SCRIPT_example.md` (verbatim script text excluded; all examples in this repository are newly written original works).
  - `templates/bridge/*`, `templates/audio/*.py`, `templates/scripts/*`, `templates/sandbox_index_example.tsx` (Remotion/Three.js rendering code, character rigs, and Python audio DSP synthesis excluded).

---

## 3. Original Contributions

All new canonical skill specifications, unified router architecture, TT-01 title curiosity gate, KH-01 multi-niche storytelling modes, analytics truth model, Creator Action Pack contract (`creator-pack.json`, `validate_output.py`), release/QA/audit tooling, documentation, test fixtures, and original demo packs are authored newly for this repository under the MIT License (`Copyright (c) 2026 quocan050302`).
