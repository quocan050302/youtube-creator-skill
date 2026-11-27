# Channel Audit & Continuous Learning Loop

A useful channel audit avoids listing 20 disconnected complaints. It isolates comparable cohort evidence, names what is already working (so the creator does not break it), identifies **one highest-leverage bottleneck**, and turns it into a measurable next experiment.

## 1. Channel Audit Procedure (`AUDIT.md`)
1. **Inventory Received vs. Missing Data:** Explicitly list what the creator supplied (titles, thumbnails, Shorts/Long analytics CSV, retention curves, transcripts, capacity) and what is missing.
   - If only raw view counts or a bare URL (without `WEB`) are provided, deliver a **Preliminary Audit** (`DRAFT` / `BLOCKED_MISSING_EVIDENCE`) and ask for the **smallest useful export** (e.g., last 10 videos with format, duration, publish date, stayed-to-watch or CTR, and APV/AVD). Never diagnose distribution solely from views.
2. **Build Comparable Cohorts:** Partition the creator's recent uploads by **format** (`SHORT` vs `LONG`) and **comparable age window** (avoid comparing a 2-day upload against a 9-month video). Compute within-channel medians so every observation is anchored to the creator's own baseline.
3. **Audit in High-Signal Order (Using Only Available Evidence):**
   - **Topic & Packaging Clarity:** Do recent titles promise distinct concrete outcomes, or repeat the same vague pattern? (Run `scripts/title_linter.py` if `CODE` is available.)
   - **Thumbnails / First Frames:** Visually inspect **only if `VISION` is available**; otherwise critique textual concepts honestly.
   - **Opening Hook & Early Retention:** Check transcripts (`scripts/hookscore.py`) and early retention windows (`scripts/retention.py`) if provided.
   - **Pacing & Payoff:** Check middle retention slide/cliffs and whether titles match actual video delivery.
   - **Sustainable Rhythm:** Evaluate consistency relative to the creator's actual weekly hours — never demand unsustainable daily uploads.
4. **Mandatory Audit Output Structure:**
   - **Data Received & Missing** (no fabricated 100-point vanity score)
   - **Observed Facts** (within-channel cohort metrics & patterns)
   - **What Is Already Working (Do NOT Break This)** (specific, concrete elements)
   - **Top Bottleneck** (evidence, confidence `LOW`/`MEDIUM`/`HIGH`, and **at least one alternative explanation**)
   - **What NOT to Change Yet** (protect focus and isolate variables)
   - **ONE Priority Action for the Next Upload** (+ 2–3 optional follow-up ideas only if helpful)

## 2. Continuous Learning Loop (`IMPROVE` Mode)
Use the creator's portable workspace (`creator-workspace/experiment-log.md`, `channel-history.csv`, `analytics-history.csv`):
1. **Isolate One Major Variable When Feasible:** Test one meaningful shift (e.g., opening first frame on physical action vs. title card) across comparable format, topic pillar, and observation window (e.g., first 7 days).
2. **Evaluate Against Prior Baseline:** Compare actual post-upload metrics against the pre-committed hypothesis and control cohort. Note confounders honestly (topic novelty, weekend timing, audio issue, Shorts view-definition changes).
3. **Render Honest Decision:**
   - **`CONTINUE`:** Clear directional improvement across comparable cohort without major confounders -> promote into creator playbook.
   - **`ADJUST`:** Clear shortfall or unintended tradeoff (e.g., higher stayed-to-watch but worse APV due to overpromised hook) -> modify hypothesis.
   - **`INCONCLUSIVE`:** Sample size too small (e.g., 1–2 uploads with high variance) or major confounders -> extend test or hold before overreacting.
4. **Strict Anti-Manipulation Rules:**
   - Never claim a sequential upload comparison is a randomized A/B test unless YouTube Test & Compare actually ran.
   - Never recommend blindly deleting/reuploading videos, buying engagement, sub-for-sub, or view manipulation.
   - Never claim the AI skill "auto-learns in the cloud" — learning happens transparently through the creator's own saved files and new verified uploads.
