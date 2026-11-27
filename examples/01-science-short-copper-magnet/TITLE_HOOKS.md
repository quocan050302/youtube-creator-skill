# Titles, First-Frame Text & Hook Analysis

## TT-01 Titles
- **Selected Title:** `Why a Copper Pipe Slows Falling Magnets` *(39 chars, 7 words — concrete paradox, truthful physics wording without overclaiming a full stop, zero hype words, fits cleanly inside ~40-char mobile & ~60-char desktop heuristics)*
- **Backup 1:** `How Copper Brakes a Falling Magnet Mid-Air` *(42 chars, 7 words)*
- **Backup 2:** `Why Falling Magnets Float Inside Copper Pipes` *(45 chars, 7 words)*

### Non-Redundant First-Frame / Cover Text
- **Selected Text:** `INVISIBLE BRAKE` *(2 words, zero lexical overlap with Selected Title)*
- **`scripts/title_linter.py` (`--format SHORT`) Result:** `heuristic_score_0_to_100: 100`, `warnings: []`, `thumbnail_comparison: COMPLEMENTARY_LEXICAL` (`shared_tokens: []`).

## Opening Hook (0–3s Visual Anomaly + Paradox)
- **Selected Hook:** `Touch a magnet to a copper pipe—nothing sticks. Drop it inside, and why does it crawl down in slow motion?`
- **Alternative Hook:** `Copper isn't magnetic, yet drop a magnet down a copper pipe and gravity seems to slow to a crawl.`
- **`scripts/hookscore.py` (`--pov narrative --title "Why a Copper Pipe Slows Falling Magnets"`) Result:**
  - `rubric_total: 9/10` (`specificity: 1`, `immediate_comprehension: 2`, `curiosity_stakes: 2`, `promise_alignment: 2`, `speakability_visual: 2`)
  - `formula_name: The Question` | `heuristic_band: WORKABLE` (`legacy_verdict_0_to_100: 56`, `reasons: []`)

> **Heuristic Limitation:** `title_linter.py` and `hookscore.py` are deterministic lexical heuristics only — they check clarity, overlap, and hype terms, and NEVER predict CTR, views, or viewer retention.
