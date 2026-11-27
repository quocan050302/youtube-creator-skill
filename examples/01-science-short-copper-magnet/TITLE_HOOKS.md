# Titles, First-Frame Text & Hook Analysis

## TT-01 Titles
- **Selected Title:** `Why a Copper Pipe Slows Falling Magnets` *(39 chars, 7 words — concrete paradox, truthful physics wording without overclaiming a full stop, zero hype words, fits cleanly inside ~40-char mobile & ~60-char desktop heuristics)*
- **Backup 1:** `How Copper Brakes a Falling Magnet Mid-Air` *(42 chars, 7 words)*
- **Backup 2:** `Why Falling Magnets Float Inside Copper Pipes` *(45 chars, 7 words)*

### Non-Redundant First-Frame / Cover Text
- **Selected Text:** `INVISIBLE BRAKE` *(2 words, zero lexical overlap with Selected Title)*
- **`scripts/title_linter.py` (`--format SHORT`) Result:** `heuristic_score_0_to_100: 100`, `warnings: []`, `thumbnail_comparison: COMPLEMENTARY_LEXICAL` (`shared_tokens: []`).

## Opening Hook (0–3s Brisk First Spoken Line)
- **Selected First Spoken Line:** `Copper isn't magnetic—why does it slow falling magnets?` *(9 spoken words; ~3.0s at brisk 180 WPM, ~3.6s at conversational 150 WPM)*
- **Alternative 0–3s Hook (Conversational):** `Drop a magnet through copper—it crawls.` *(7 spoken words; ~2.8s at 150 WPM)*
- **`scripts/hookscore.py` (`--shorts-story --title "Why a Copper Pipe Slows Falling Magnets"`) Result:**
  - `word_count: 9` | `fits_3s_at_180_wpm: true` (`est_spoken_sec_180_wpm: 3.0s`), `fits_3s_at_150_wpm: false` (`est_spoken_sec_150_wpm: 3.6s`)
  - `formula_name: The Question` (lexical heuristic only)

> **Heuristic Limitation:** `title_linter.py` and `hookscore.py` are deterministic lexical heuristics only — they check clarity, word-count timing, overlap, and hype terms, and NEVER predict CTR, views, or viewer retention.
