# Analytics Diagnosis Report — Synthetic Science Short (`45s`)

> **Label:** `FICTIONAL_OR_DEMO` synthetic dataset (not a real YouTube Studio export).

## 1. Recommended Action
Cut the mid-video channel follow/link-in-bio interruption (`0:12–0:16`) on your next comparable Short and move directly from the steel-bolt control drop into the falling magnet proof. **Do NOT remove the slow-motion cutaway around `0:28`**, which coincides with a `+49.5 pp` rewatch spike (`108.5%`).

## 2. Deterministic Findings (`scripts/retention.py`)
- **Observed Axis:** `0.0s – 45.0s` (`10` points, median step `5.0s`, max step `7.0s`).
- **Overview:** Start `100.0%` -> End `51.0%`; Max `108.5%` (`has_rewatch_above_100pct: true` — valid rewatch behavior, NOT clamped).
- **Early Opening Window (`SHORT`):**
  - `0.0s -> 3.0s`: `100.0% -> 84.0%` (**`-16.0 pp`**, slope `-5.333 pp/s`, exact observed point).
  - `0.0s -> 6.75s` (15% duration): `100.0% -> 81.75%` (**`-18.25 pp`**, linear between observed points `3.0s` and `8.0s`).
- **True Structural Cliff (Excluding Post-Rewatch Return):**
  - **`12.0s -> 16.0s`: `-18.0 pp`** (`79.0% -> 61.0%`, `-4.50 pp/s`, `2.82x` background median drop slope).
  - *Transcript excerpt (`possible_contributor_not_proven_cause`):* `"Now before we explain the physics, make sure you follow my channel and check out the link in my bio for more science."`
- **Post-Spike Return (NOT a Leak):**
  - **`28.0s -> 35.0s`: `-44.5 pp`** (`108.5% -> 64.0%`, `is_post_rewatch_spike_return: true`) immediately follows the **`22.0s -> 28.0s` `+49.5 pp` rewatch spike** (`59.0% -> 108.5%`) when the slow-motion magnet cutaway plays. Returning from `108.5%` to `64.0%` reflects viewers finishing their replay rather than abandoning the video prematurely.

## 3. Alternative Explanations & Limitations
- Without inspecting the actual video/audio file (`AUDIO/VIDEO` & `VISION` unavailable), we cannot prove whether the `12.0s–16.0s` drop was caused solely by the verbal CTA, a visual pacing lull, or an audio dip during that span.
- Shorts feed distribution also depends heavily on **`Stayed to watch vs. Swiped away`** and **`Engaged views`**, which were not supplied in this single-curve export. Do not evaluate Shorts distribution using Long-form Impressions CTR.
- Sample size is `n = 1` synthetic video; verify against your trailing 5–10 comparable Shorts cohort before changing your overall channel format.
