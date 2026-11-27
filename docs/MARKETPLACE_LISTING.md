# Agensi Marketplace Listing Handover (FREE $0)

> **Publication Status:** `NOT_PUBLISHED` (Owner Manual Review Required).
> Do not claim Agensi approval or invent a live listing URL until the owner
> uploads the verified package and Agensi completes external review (typically
> a few hours, up to 48 hours per Agensi Creator FAQ verified 2026-11-27).

---

## 1. Ready-to-Paste Listing Fields (English US)

- **Display Title:** `YouTube Creator Intelligence — Free AI Skill`
- **Canonical Skill Name (`SKILL.md`):** `youtube-creator-skill`
- **Pricing:** `FREE ($0)` *(per Agensi Creator FAQ, no payout method is required for free listings; open-source MIT skills are explicitly permitted when preserving license notices).*
- **Version:** `1.0.0-rc.1` *(bump to `1.0.0` once owner clears stable release gates)*
- **Suggested Category:** `Create -> Writing & Content` (or `Grow -> Social Media` depending on current Agensi UI dropdown)
- **Suggested Tags / Keywords:** `youtube`, `youtube-shorts`, `scriptwriting`, `retention-analysis`, `channel-audit`, `thumbnails`, `content-strategy`, `youtube-seo`, `open-source`
- **Short Summary (1–2 sentences):**
  > Turn a topic, script draft, competitor dataset, or YouTube Studio export into one evidence-backed creative decision and a ready-to-produce YouTube video plan. Write original Shorts and Long-form hooks, titles, scripts, thumbnail briefs, and diagnose retention from the data you provide — offline-first, MIT open source, zero required API keys.

### Long Description (Copy-Ready)

**What It Does**
`youtube-creator-skill` is a single unified AI skill built for global YouTube Shorts and Long-form creators. Instead of spitting out generic prompt walls or algorithm myths, it guides your agent through one evidence-backed workflow:

1. **Research & Competitor Outliers:** Build primary-source fact tables and rank competitor standouts using leave-one-out peer medians separated strictly by format (`SHORT` vs `LONG`) and age bucket.
2. **TT-01 Titles & 21-Formula Hook Lab:** Craft curiosity-gap titles without hype spam, compare non-redundant title + thumbnail pairings, and evaluate openings with a transparent 5-dimension heuristic rubric (including a third-person storytelling Shorts mode).
3. **KH-01 Multi-Niche Scripts & Visual Storyboards:** Write natural spoken voiceover scripts (`SCRIPT.txt`) across 10 niches (History, Science, Scam Awareness, Finance, Gaming, Education, Fiction, Product Demo, Comedy, Lifestyle), paired with WPM-estimated `STORYBOARD.csv` and `THUMBNAIL_PROMPT.txt` concepts.
4. **Analytics Truth & Retention Diagnosis:** Read YouTube Studio retention exports accurately — tracking percentage-point (`pp`) early drops and cliffs, preserving valid `>100%` rewatch/loop spikes, separating Shorts views vs. engaged views & stayed-to-watch, and aligning timestamps with your `.srt`/`.vtt` transcript as possible contributors.
5. **Audit, Capacity Calendars & Post-Publish Learning Loop:** Get ONE prioritized fix per channel audit (plus what NOT to break), build realistic 7/14/30-day calendars sized to your weekly hours, repurpose standalone Shorts from long transcripts, triage comments, and validate `00:00` chapters.

**What Is Included in This Package**
- 1 canonical `SKILL.md` router + 21 focused reference modules (`references/`)
- 7 optional standalone Python 3 stdlib scripts (`scripts/`) built for isolated single-file execution (zero third-party dependencies, zero network calls, zero sibling file reads)
- 8 templates & contracts (`assets/`, including `hooks.json` with 21 MIT-attributed formulas and `output-schema.json` v1.0.0)
- Complete MIT License & upstream third-party notices (`LICENSE`, `LICENSES/`, `THIRD_PARTY_NOTICES.md`)

**Dependencies & Privacy**
- **Zero API keys, zero accounts, zero paid subscriptions required.**
- Core text workflows need **no Python**. Optional deterministic scripts require only standard Python 3.10+.
- Nothing is auto-published to YouTube and no creator data is sent back to the author.

**Honest Limitations**
- Text, research, and analytics advisory only: does **not** render MP4 videos, synthesize voiceovers, generate PNG images, or upload to YouTube.
- Heuristic hook/title scores and outlier multiples are screening aids — never guaranteed CTR, views, or income.

**Open-Source Attribution (MIT)**
Licensed under MIT (`Copyright (c) 2026 quocan050302`). Adapts 21 hook formulas and standalone analysis scripts from `jakeschincariol/youtube-agent-skill` (MIT, `Copyright (c) 2026 Jake Schincariol`) and derives conceptual storytelling pacing guidelines from `mromidev/claude-animated-shorts` (MIT, `Copyright (c) 2026 Mr omi`). Full verbatim notices are bundled inside the package.

---

## 2. Example Before / After for Listing Preview

- **Before (Weak Draft):** `"INSANE MAGNET TRICK YOU WON'T BELIEVE!!"` + `"Hey guys, welcome back! Today I'll show you a crazy copper pipe experiment because eddy currents slow magnets down."`
- **After (`youtube-creator-skill` — verified live run `EV-01`):**
  - Title: `"Why a Copper Pipe Slows Falling Magnets"` (`title_linter.py`: `100/100`)
  - Thumbnail / First-Frame Text: `"INVISIBLE BRAKE"` (zero word duplication)
  - 0–3s Hook: `"Touch a magnet to a copper pipe—nothing sticks. Drop it inside, and why does it crawl down in slow motion?"` (`hookscore.py --pov narrative`: `9/10` heuristic rubric)
  - Clean `SCRIPT.txt` + 5-beat `STORYBOARD.csv` + `NEXT_EXPERIMENT.md` (zero CTA).

---

## 3. Owner Manual Upload Checklist (Agensi)

1. Confirm the clean build artifact exists and verify its SHA-256 against `dist/SHA256SUMS.txt`:
   - Upload **`dist/youtube-creator-skill-agensi-v<version>.zip`** ONLY (never the Universal ZIP or nested archive).
2. Confirm Agensi packaging preflight passed locally (`<= 1 MB`, `<= 90 files`, `1` `SKILL.md`, UTF-8 text/code only, zero bundled dependencies, all script logic `< 20 KB`).
3. Verify current Agensi Terms of Service do not conflict with MIT notice preservation (Agensi Creator FAQ verified 2026-11-27 confirms open-source skills may be listed free while following their license).
4. Submit on https://www.agensi.io/ (keep price at **`$0 FREE`**) and await external Agensi review.
5. Once live, load your own listing via Agensi MCP (free, does not count as a use per FAQ) to confirm live delivery, then add the verified listing URL to `README.md`.

---

## 4. Organic Growth Pack — 3 Original Pinterest Pin Concepts

*(Manual publication by owner only; replace `<VERIFIED_GITHUB_OR_AGENSI_URL>` only after public release is live.)*

| Pin # | Visual Concept (2:3 Vertical Infographic) | Headline Copy | Description Copy | CTA Link Placeholder |
|---|---|---|---|---|
| **Pin 1 — Before/After Hook** | Split card: red top half showing bloated `"Hey guys welcome back..."` intro vs. clean green bottom half showing crisp 15-word 0–3s paradox hook + `NOT MAGNETIC` first frame | **Stop Losing Viewers in the First 3 Seconds** | Free MIT open-source AI skill for YouTube creators. Rewrites weak intros into crisp hooks using 21 attributed formulas and a transparent 5-point rubric — no API key needed. | `<VERIFIED_GITHUB_OR_AGENSI_URL>` |
| **Pin 2 — Title + Thumbnail Pairing** | Minimal visual diagram showing Title (`Why Copper Stops a Falling Magnet`) + Thumbnail (`NOT MAGNETIC`) connected by `"1 Promise, 0 Repeated Words"` | **Why Half of YouTube Thumbnails Waste Your Click** | Stop repeating your title text on your thumbnail. Run our free open-source YouTube title & thumbnail linter offline in Python or any AI chat. | `<VERIFIED_GITHUB_OR_AGENSI_URL>` |
| **Pin 3 — Retention Cliff Fix** | Clean synthetic retention curve graphic highlighting a `-14 pp` drop at `0:12` aligned to a `"possible contributor"` script line + `"1 Controlled Next Test"` callout | **Read Your YouTube Retention Graph Without Guessing** | Separate Shorts stayed-to-watch from Long-form CTR, keep valid >100% rewatch spikes intact, and turn one retention cliff into your next upload experiment. Free MIT AI skill. | `<VERIFIED_GITHUB_OR_AGENSI_URL>` |

### Manual Metrics Tracking (Zero User Telemetry)
Track public growth metrics manually on a weekly sheet (source + observation window):
- GitHub stars, forks, and Release ZIP download counts (via GitHub Insights / Releases API).
- Agensi listing views, uses, follows, and user reviews (from Agensi Creator dashboard once live).
- Pinterest outbound clicks (from Pinterest Analytics if pins are published).
