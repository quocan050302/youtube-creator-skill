# Capacity-Aware Content Planning Engine

A content plan that ignores the creator's real weekly hours fails by Day 4. Build realistic, varied, non-duplicate schedules grounded in actual capacity and prior audit findings.

## 1. Required Planning Inputs & Smart Defaults
- **Horizon & Volume:** 7, 14, 30 days, or custom count; exact slots/day or uploads/week requested.
  - **Completeness Rule:** If the user explicitly asks for *"a 14-day plan (1 Short/day)"*, deliver **all 14 rows** — never truncate at Day 5 with *"repeat similar pattern"*. If they explicitly ask for *"full scripts for all 14 days"*, deliver all 14 complete scripts (or cleanly indexed per-video files when `FILE_WRITE` is available). If they do not request full scripts, deliver detailed outlines clearly labeled `script_status: OUTLINE`.
  - **Capacity Warning:** If the requested frequency exceeds the creator's stated hours (e.g., 30 Long videos on 4 hours/week), still honor the requested structure OR clearly label the workload mismatch and include a **Priority / Drop Order (`P0`/`P1`/`P2`)** showing which rows to drop first in a busy week. Never force daily posting when capacity is low.
- **Dates & Posting Times:**
  - Use real calendar dates **only** when the user supplies a start date and timezone; otherwise label `Day 1 .. Day N`.
  - Base posting times strictly on supplied channel audience analytics or mark as `"TEST_SLOT — no universal best posting time"`.
- **Format Respect:** Do **not** force a Long-form anchor video onto a Shorts-only creator. For hybrid (`MIXED`) creators, anchor + derivative Shorts can reduce production load naturally.

## 2. Mandatory Fields Per Plan Row (`CONTENT_PLAN.csv` / `.md`)
Every planned slot includes:
1. `day` (and optional verified `date`)
2. `slot` & `format` (`SHORT` / `LONG`)
3. `pillar` (balanced rotation across 2–4 pillars)
4. `angle` (semantically unique — deduplicate across the entire plan AND against creator's `channel-history.csv`)
5. `target_viewer`
6. `title` (passes TT-01 curiosity gate)
7. `hook` (varied hook formulas — avoid repeating the same opener back-to-back)
8. `first_frame` (concrete opening visual aligned with title + hook)
9. `script_status` (`FULL_SCRIPT` or `OUTLINE`, matching user request)
10. `thumbnail_brief` (focal hierarchy + optional 0–3 word text)
11. `duration_target_s`
12. `evidence_status` (`VERIFIED_FACT`, `SUPPLIED_FACT`, `NEEDS_VERIFICATION`, `FICTIONAL_OR_DEMO`)
13. `kpi_hypothesis` (tied directly to upstream `CHANNEL_AUDIT` findings when chained)
14. `est_hours` (coarse realistic estimate, labeled estimate)
15. `priority` (`P0` must-ship / `P1` core / `P2` drop-first if short on time)

## 3. Plan-Level Quality Validation
- Cross-check every row for **title / first-frame / hook / payoff alignment**.
- Confirm zero invented search-volume or traffic-demand numbers.
- Sum estimated weekly hours and compare explicitly against the creator's stated weekly capacity.
