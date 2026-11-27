# Analytics Truth Model & Retention Curve Diagnosis

Read YouTube Studio data with statistical integrity. Never mix incompatible metrics, never turn missing data into zero, and never replace real cohort evidence with algorithm folklore.

When `CODE` is available and a retention CSV is supplied, run `scripts/retention.py` (optionally with `--transcript` if timestamped captions exist).

## 1. Data Ingestion & Validation Rules
Before drawing any conclusion from YouTube Studio exports, CSVs, screenshots, or pasted notes:
1. **Parse Safely:** Handle UTF-8 BOM, comma or semicolon delimiters, quoted fields with embedded newlines, locale number formats, percent signs, and duplicate rows.
2. **Explicit Units & Scope:** Confirm observation date range, format (`SHORT` vs `LONG`), video duration, and metric definitions. Reject `NaN`, `Infinity`, negative counts, `duration_s <= 0`, or ambiguous axes safely with clear error reasons.
3. **Unknown Is `null`, Never `0`:** Missing CTR, missing impressions, or unreported engaged views remain unknown — never replace missing metrics with `0`.
4. **Do NOT Clamp Valid >100% Retention or APV:** Viewers rewatching a moment or looping a Short legitimately produce retention curves or Average Percentage Viewed (APV) above `100%`. Explain what >100% indicates (rewatch/loop intensity) instead of treating it as an error.
5. **Enforce Bounded Rates Where Definitional:** Impressions CTR and stayed-to-watch selection rates must stay within `[0%, 100%]`.
6. **Proper Rate Aggregation:** When summarizing multiple videos over the same compatible period and format, sum numerators and sum denominators first (`sum(clicks)/sum(impressions)`) rather than taking an unweighted mean of percentages across wildly unequal denominators. Never invent missing denominators.

## 2. Official Format & Metric Separation (YouTube Definitions)
- **YouTube Shorts (Note March 31, 2025 View Definition Update):**
  - **Views:** Counted when a Short starts to play or replay (no minimum watch-time threshold).
  - **Engaged views:** Counted when a viewer watches past the initial play threshold (used for YouTube Partner Program eligibility and historical comparability before March 31, 2025). Always clarify which metric is reported and avoid comparing pre-update raw views directly against post-update raw views without noting the definition change.
  - **Feed Selection (`Shown in feed` -> `Stayed to watch` vs `Swiped away`):** Primary opening-frame/hook signal for Shorts feed traffic. **Impressions CTR does NOT explain Shorts-feed distribution.**
  - **Watch Depth:** Average View Duration (AVD) and Average Percentage Viewed (APV, often >100% on strong rewatches/loops).
- **YouTube Long-Form:**
  - **Impressions & Impressions CTR** (varies heavily by traffic source: Home vs Suggested vs Search — segment when available).
  - **AVD, APV, Audience Retention Curve, Returning Viewers.**

## 3. Folklore Rejection (Strict Rule)
- **Never** diagnose a video as a failure or identify a root cause solely from raw view counts (e.g., *"stuck at 1,000 views"*).
- **Never** state *"1K jail"*, *"shadowban"*, or secret *"YouTube testing buckets"* as official platform mechanisms.
- **Never** impose universal magic thresholds (such as claiming *"under 25% loss in 30s is always healthy"* across every format, niche, and duration). Compare against **the creator's own comparable cohort baseline** (same format, similar duration, comparable age window).

## 4. Retention Curve Analysis Protocol (`scripts/retention.py`)
1. **Axis Verification:** Support seconds or explicit normalized percent (`0–100%` + verified `duration_s`). Require monotonic ascending x (sort and flag if unsorted; document duplicate x handling). Never extrapolate beyond observed range or fabricate 1-second timestamps from coarse exports.
2. **Format-Aware Early Window:**
   - **Shorts:** Inspect opening `0–3s` (and `10–20%` duration where sample granularity permits).
   - **Long-form:** Inspect opening `0–15s` and `0–30s` (when video length and sample density permit).
3. **Percentage Points (pp) vs. Relative Change:**
   - A move from `100%` to `80%` is **`-20 percentage points (-20 pp)`** (and `-20%` relative to `100%`).
   - A move from `50%` to `40%` is **`-10 percentage points (-10 pp)`** (`-20%` relative to `50%`). Always report **pp** and exact observed interval `[t0, t1]` plus local slope (`pp/s`).
4. **Cliff Detection & Non-Causal Interpretation:**
   - Flag cliff candidates using both absolute drop (pp) and local slope relative to adjacent/background slope.
   - Recognize natural end-of-video drop-offs (outro/sign-off) and rewatch spikes (`+pp`).
   - Map cliffs to transcript intervals **only** when a valid timestamped transcript is supplied. Frame transcript lines strictly as **`possible contributor`**, never proven cause. Without a transcript, never guess or invent spoken lines.
   - Without video/audio inspection, cannot prove whether a drop came from writing vs. editing vs. audio quality — present competing hypotheses and propose **one controlled next test**.
