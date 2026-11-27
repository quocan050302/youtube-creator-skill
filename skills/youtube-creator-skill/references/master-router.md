# Master Router & State Machine

## 1. Lifecycle States

```text
INTAKE -> CAPABILITY_CHECK -> ROUTE -> RESEARCH_IF_NEEDED -> CREATE_OR_ANALYZE -> REVIEW -> DELIVER -> OPTIONAL_NEXT_EXPERIMENT
```

### State Transition Rules
- **INTAKE -> CAPABILITY_CHECK:** Parse user goal, format (`SHORT` or `LONG`), niche, output language, audience market, duration target, WPM preference, constraints (e.g., "no CTA", "title only", "faceless"), and attached/pasted inputs.
- **Unknowns & Clarifying Questions:**
  - If the task can proceed safely with reasonable defaults (e.g., English US, 45–60s Short or 8-min Long, conversational 160 WPM), **state the assumptions briefly and proceed immediately**.
  - Ask at most **1–2 targeted questions** only when missing facts or contradictory constraints would produce misleading output (for example: no web access and the user asks about a recent unprovided game patch, or a channel audit with zero metrics/URLs).
- **Non-Trigger Boundary:** If the user asks an unrelated question (e.g., debugging React CSS, writing SQL, booking flights), do **not** apply YouTube creator templates or force YouTube output formatting.

## 2. Canonical Intent Catalog (17 Intents)

| Intent ID | Primary Deliverable | Default Output Scope |
|---|---|---|
| `GENERATE` | Full or targeted Creator Action Pack from topic/premise | Compact pack in chat, or full folder when requested with `FILE_WRITE` |
| `AUDIT_SCRIPT` | Prioritized bottleneck + exact rewrite + why | Compact critique + clean rewritten script |
| `CHANNEL_AUDIT` | Cohort evidence, what works, top bottleneck, what NOT to change, 1 priority action | `AUDIT.md` / inline report |
| `COMPETITOR_RESEARCH` | Cohort-safe outlier ranking, structural pattern, adjacent original ideas | Outlier table + 1 testable hypothesis |
| `NICHE_DISCOVERY` | Audience questions, capacity fit, evergreen vs timely tradeoffs | 3–5 concrete positioning options |
| `TOPIC_RESEARCH` | Evidence table, 3–10 distinct angles, recommended angle, uncertainties | `RESEARCH.md` / inline brief |
| `TITLE_PACKAGE` | 5–10 variants (if asked), 1 selected + up to 2 backups, lint warnings | Title block only (stop here if title-only) |
| `HOOK_LAB` | 5 distinct options (when asked), top 2 ranked with rubric & failure-mode check | Hook comparison block |
| `THUMBNAIL_LAB` | Visual hierarchy brief + optional 0–3 word text + image prompt | `THUMBNAIL_PROMPT.txt` / inline brief |
| `EDIT_REVIEW` | Evidence-tagged Edit Decision List (priority, span, issue, fix, tradeoff) | `EDIT_DECISIONS.csv` / inline table |
| `ANALYTICS_DIAGNOSIS` | Metric validation, retention leaks/cliffs/slide, non-causal hypotheses | `ANALYTICS_REPORT.md` / inline report |
| `CONTENT_PLAN` | Exact requested day/slot calendar (7/14/30 or custom), workload & drop order | `CONTENT_PLAN.csv` + `.md` (+ scripts if asked) |
| `REPURPOSE` | Ranked standalone Short candidates from Long transcript + fresh opener | `REPURPOSE.md` / inline list |
| `SEO` | Search intent queries, front-loaded description, honest relevant tags | Upload metadata block |
| `COMMENTS` | Triage (Questions/Corrections/Praise/Bait), voice-matched replies, 1 pin pick | `COMMENTS.md` / inline table |
| `CHAPTERS` | Rule-validated timestamp block (`00:00`, >=3, >=10s) or non-timed outline | `CHAPTERS.txt` / inline block |
| `IMPROVE` | Evaluate prior experiment against fresh data -> `CONTINUE`/`ADJUST`/`INCONCLUSIVE` | Updated experiment log + next plan |

## 3. Multi-Intent Chaining & Conflict Resolution

When a user combines intents (e.g., *"Audit my channel and give me a 14-day Shorts plan"* or *"Diagnose this retention CSV, rewrite the opening hook, and update my next script"*):

1. **Order by dependency:**
   `CAPABILITY_CHECK` -> `RESEARCH`/`ANALYTICS_DIAGNOSIS`/`CHANNEL_AUDIT` -> `TOPIC_RESEARCH`/`COMPETITOR_RESEARCH` -> `CONTENT_PLAN`/`GENERATE`/`REPURPOSE` -> `TITLE_PACKAGE`/`HOOK_LAB`/`THUMBNAIL_LAB` -> `SEO`/`CHAPTERS` -> `REVIEW`.
2. **Pass findings downstream:** The top bottleneck identified in `CHANNEL_AUDIT` or `ANALYTICS_DIAGNOSIS` MUST explicitly shape the next `CONTENT_PLAN` or `GENERATE` output (e.g., if early 0–3s retention leaked on slow setups, every planned Short must open on immediate action).
3. **Never duplicate sections:** Present each decision once. Do not print the same script three times across chat sections.
4. **Conflict Handling:**
   - Explicit user constraint (e.g., *"no CTA"*, *"keep my exact topic"*, *"output only 1 clean paragraph"*) overrides default templates.
   - Safety, factual truthfulness, and copyright boundaries override user requests to fabricate data, impersonate creators, or provide operational scam instructions.

## 4. Narrow-Request Discipline

- **"Give me 5 titles for X" (`TITLE_PACKAGE` only):** Deliver titles, selected pick, rationale, and brief heuristic cautions. Do NOT append an unsolicited script, storyboard, or 14-day plan.
- **"Just the voiceover script, one clean block, no labels":** Output strictly clean spoken text suitable for direct recording/TTS. Put any critical factual caveat in a clearly separated footnote only if required for safety/truth.
- **"Keep my approved premise unchanged":** Preserve the user's core premise and facts; refine pacing, clarity, and structure without pivoting to a different story.
