# Titles, First-Frame Text & Hook Analysis

## TT-01 Titles
- **Selected Title:** `Why Reshipping Jobs Leave You Liable` *(36 chars, 6 words — crisp stakes, fits cleanly inside mobile & desktop truncation heuristics, zero hype spam)*
- **Backup 1:** `The Remote Shipping Job That's a Trap` *(37 chars, 7 words)*
- **Backup 2:** `Why Home Package Jobs Put You at Risk` *(37 chars, 8 words)*

### Non-Redundant First-Frame / Cover Text
- **Selected Text:** `DON'T RELABEL` *(2 words, zero lexical overlap with Selected Title)*
- **`scripts/title_linter.py` (`--format SHORT`) Result:** `heuristic_score_0_to_100: 100`, `warnings: []`, `thumbnail_comparison: COMPLEMENTARY_LEXICAL` (`shared_tokens: []`).

## Opening Hook (0–3s Direct Warning)
- **Selected Hook:** `If a work-from-home job pays you to inspect and reship packages, stop before you sign anything.`
- **Alternative Hook:** `Legitimate retailers never pay strangers to relabel packages from their living room—here is the trap.`
- **`scripts/hookscore.py` (`--pov direct --title "Why Reshipping Jobs Leave You Liable"`) Result:**
  - `rubric_total: 8/10` (`specificity: 0`, `immediate_comprehension: 2`, `curiosity_stakes: 2`, `promise_alignment: 2`, `speakability_visual: 2`)
  - `formula_name: The Warning` | `heuristic_band: WORKABLE` (`legacy_verdict_0_to_100: 55`, `reasons: []`)

> **Heuristic Limitation:** `title_linter.py` and `hookscore.py` are lexical heuristics only and never predict CTR or viewer retention.
