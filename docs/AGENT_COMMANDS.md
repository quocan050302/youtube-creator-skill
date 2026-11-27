# Agent Commands & Natural Language Intents

Use **plain natural language** across every supported AI client. Slash syntax (such as `/youtube-creator-skill`) works only in runtimes that expose skill slash commands; natural language invocation (`"Use youtube-creator-skill to..."`) works everywhere.

## Supported Intents

| Intent | Example Natural-Language Prompt | What You Receive |
|---|---|---|
| `GENERATE` | "Use youtube-creator-skill to build a 45s Short pack on why copper slows a falling magnet. No CTA." | Recommended action + Title + Hook + Clean `SCRIPT.txt` + `STORYBOARD.csv` + `THUMBNAIL_PROMPT.txt` + Experiment |
| `TOPIC_RESEARCH` | "Use youtube-creator-skill to research 6 original Long-form angles on home battery backup." | Evidence table, differentiated angles, recommended angle, open verification questions |
| `NICHE_DISCOVERY` | "Use youtube-creator-skill to help me pick a faceless educational niche I can run in 5 hours/week." | 3–5 concrete positioning options + 3-video validation sprint |
| `COMPETITOR_RESEARCH` | "Use youtube-creator-skill to rank outliers in this competitor CSV by leave-one-out peer median." | Cohort-safe outlier ranking, lexical pattern summary, original adjacent ideas |
| `TITLE_PACKAGE` | "Use youtube-creator-skill to write 8 TT-01 title options only for my video about email tracking pixels." | Titles, primary winner + 2 backups, lint warnings (stops at titles) |
| `HOOK_LAB` | "Use youtube-creator-skill to write 5 distinct hooks for this video and pick the top 2." | 5 formula-diverse hooks, top 2 with 0–10 rubric & first-frame pairing |
| `THUMBNAIL_LAB` | "Use youtube-creator-skill to design a 16:9 thumbnail concept and image prompt for this title." | Focal hierarchy brief, optional 0–3 word text, copy-ready prompt (concept only) |
| `AUDIT_SCRIPT` | "Use youtube-creator-skill to audit this draft script for title-hook mismatch and rewrite the opening." | Exact bottleneck diagnosis + clean rewrite |
| `EDIT_REVIEW` | "Use youtube-creator-skill to generate an Edit Decision List from this `.srt` transcript." | Evidence-tagged gap/filler/restart candidates (`TRANSCRIPT_IMPLIED`) |
| `ANALYTICS_DIAGNOSIS` | "Use youtube-creator-skill to diagnose this YouTube Studio retention CSV and align it with my `.srt`." | Early-window `pp` delta, cliffs/spikes, possible transcript contributors, next test |
| `CHANNEL_AUDIT` | "Use youtube-creator-skill to audit my last 15 uploads from this CSV and give me ONE priority fix." | Cohort facts, what works, top bottleneck + alternative explanation, 1 priority action |
| `CONTENT_PLAN` | "Use youtube-creator-skill to plan 14 days of Shorts (1/day) for my science channel on 6 hours/week." | Complete 14-row calendar with workload check and P0/P1/P2 drop order |
| `REPURPOSE` | "Use youtube-creator-skill to extract 4 standalone Shorts from this long video transcript." | Ranked spans, fresh 0–3s openers, original vs rewritten labels, 9:16 crop notes |
| `SEO` | "Use youtube-creator-skill to write a front-loaded description and honest tags for this tutorial." | 3 target queries, above-the-fold description, 5–15 disambiguation tags |
| `COMMENTS` | "Use youtube-creator-skill to triage these 30 comments, draft replies in my voice, and pick 1 pin." | 4-pile count (Questions/Corrections/Praise/Bait), concise replies, 1 pin pick |
| `CHAPTERS` | "Use youtube-creator-skill to validate these timestamps against YouTube's chapter rules." | Validated `00:00` chapter block or exact rule errors |
| `IMPROVE` | "Use youtube-creator-skill to evaluate EXP-001 using these fresh 7-day analytics and update next week." | `CONTINUE`/`ADJUST`/`INCONCLUSIVE` decision + updated plan |

## Useful Constraint Modifiers (Strictly Enforced)
- `"Title only"` / `"Just the script, one clean block"`
- `"No CTA"` / `"No captions"`
- `"Write in Vietnamese"` / `"Target market: UK"` / `"Speaking rate: 150 WPM"`
- `"Keep my exact premise unchanged"`
