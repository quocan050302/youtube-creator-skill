# Competitor Research & Cohort-Safe Outlier Analysis

Raw view counts measure channel size, not idea strength. A 100k-view video on a channel whose peers average 20k is a meaningful signal; a 100k-view video on a 5M-subscriber channel may be below baseline.

When `CODE` is available, run `scripts/outlier_analyzer.py` on user-supplied or lawfully collected public metadata. Never scrape private accounts, bypass authentication, or violate platform terms.

## 1. Required Input Fields & Cleaning Rules
Each row should include: `channel_id` (or `channel` label), `video_id` (or canonical `url`), `title`, `format` (`SHORT` or `LONG`), `published_at`, `observed_at` (or common `as_of`), `views`, `duration_s`, plus optional public metadata.

Enforce these strict hygiene rules:
1. **Separate Formats Always:** Never pool `SHORT` and `LONG` videos into the same baseline median. View definitions, feed mechanics, and watch patterns differ fundamentally.
2. **Deduplicate First:** Deduplicate by `video_id` or canonical URL before computing medians. Record dropped duplicates.
3. **Exclude Invalid / Missing Rows Honestly:** Missing or non-positive/unparseable `views` are **excluded with a logged reason** — NEVER coerced to `0`.
4. **Comparable Age Buckets:** Group videos within the same channel + format + age bucket relative to `observed_at` / `as_of` (default buckets: `0-7d`, `8-30d`, `31-90d`, `91-365d`, `365d+`; configurable). Flag snapshot mismatches if `observed_at` dates differ widely. Never compare a 2-day-old upload directly against a 2-year-old evergreen video without explicit caveat.

## 2. Leave-One-Out Peer Baseline Math
For each eligible candidate video `i` inside its `(channel, format, age_bucket)` cohort:
- Let `peers` = all OTHER eligible videos in the same cohort (**excluding candidate `i`** so an extreme hit does not contaminate its own baseline).
- **Minimum Peer Threshold:** Target >= 5 peers; allow >= 4 peers as an **exploratory** baseline (`low_sample_warning`). Fewer than 4 peers -> `INSUFFICIENT_PEERS` (do **not** compute outlier ratio).
- Compute `peer_median = median(peer_views)`. Require `peer_median > 0` (avoid division by zero).
- `outlier_ratio = candidate_views / peer_median`.
- Optional `views_per_day` must be explicitly labeled **`naive_proxy_only`** (never treated as equivalent to a true decay trajectory).
- Sort descending by `outlier_ratio` with deterministic tie-breaker `(views desc, video_id asc)`.
- Screening cutoff (e.g., `>= 2.0x`) is a configurable research filter, **never** a causal guarantee.

## 3. Ethical Pattern Extraction (No Cloning)
1. **Separate Observed vs. Unobserved:** If you only have titles and view counts, you observed **packaging features**, NOT hook retention, editing pace, or traffic sources. State that explicitly. Never claim title formula correlation proves why the video got views.
2. **Abstract Structural Patterns Only:** Extract the underlying tension, contrast, mechanism, or framing pattern — NEVER copy a competitor's script, proprietary characters, branding, or shot-for-shot sequence.
3. **Actionable Creator Translation:** Propose 2–4 original adjacent topics sized to the creator's actual capacity and voice, ending with **one testable hypothesis**.
4. **Weak Data Honesty:** If the sample is sparse (< 4 peers per cohort) or mixed, report `INSUFFICIENT_DATA` and never declare a niche "trending" or "saturated".
