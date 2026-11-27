# YouTube Creator Intelligence (`youtube-creator-skill`)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Price: Free $0](https://img.shields.io/badge/Price-Free%20%240-blue.svg)](LICENSE)
[![Status: v1.0.0-rc.2](https://img.shields.io/badge/Release-v1.0.0--rc.2-orange.svg)](CHANGELOG.md)
[![CI](https://github.com/quocan050302/youtube-creator-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/quocan050302/youtube-creator-skill/actions/workflows/ci.yml)

**Turn a topic, script draft, competitor dataset, or YouTube Studio export into one evidence-backed creative decision and a ready-to-produce Creator Action Pack — then read real post-upload analytics to improve your next video.**

Built as a free, open-source, offline-first **YouTube AI agent skill** for global **Shorts** and **Long-form** creators. Zero required API keys, zero accounts, zero telemetry, and zero paid tool dependencies.

---

## Who It Is For

- **Solo & Faceless YouTube Shorts Creators:** Research surprising angles, sharpen 0–3s hooks, write clean voiceover scripts (`SCRIPT.txt`), and align beat-by-beat visual plans (`STORYBOARD.csv`).
- **Long-Form Educators, Storytellers & Reviewers:** Build structured chapter arcs, pair non-redundant titles + thumbnails, turn raw transcripts into Edit Decision Lists, and repurpose standalone Shorts.
- **Data-Driven Channel Owners:** Diagnose YouTube Studio audience retention curves, analyze cohort-safe competitor outliers (leave-one-out peer medians), and run a disciplined one-variable-at-a-time experiment loop.

---

## 30-Second Quick Start

### Path 1 — Native AI Agent (Antigravity, Claude Code, Codex)

Clone the repo and copy the single canonical skill folder into your project:

```bash
git clone https://github.com/quocan050302/youtube-creator-skill.git
# Antigravity / Codex (project-local):
mkdir -p .agents/skills && cp -r youtube-creator-skill/skills/youtube-creator-skill .agents/skills/
# Claude Code (project-local):
mkdir -p .claude/skills && cp -r youtube-creator-skill/skills/youtube-creator-skill .claude/skills/
```

Windows PowerShell:

```powershell
git clone https://github.com/quocan050302/youtube-creator-skill.git
New-Item -ItemType Directory -Force -Path ".agents\skills" | Out-Null
Copy-Item -Recurse "youtube-creator-skill\skills\youtube-creator-skill" ".agents\skills\youtube-creator-skill"
```

Then ask in plain language:
> *"Use youtube-creator-skill to build a 40-second YouTube Short pack explaining why a magnet falls slowly inside a copper pipe. No CTA."*

### Path 2 — Any Chat Interface (Zero Install)

Open [`universal/UNIVERSAL_PROMPT.md`](universal/UNIVERSAL_PROMPT.md), copy-paste it into a new chat (ChatGPT, Claude Chat, Gemini, DeepSeek, Grok, Qwen, Copilot, etc.), and follow with your prompt or pasted CSV/transcript.

### Path 3 — Agensi Marketplace

A clean single-skill Agensi package is built from the exact same canonical source (`tools/build_release.py`). See [`docs/INSTALL.md`](docs/INSTALL.md) and [`docs/MARKETPLACE_LISTING.md`](docs/MARKETPLACE_LISTING.md) for current distribution details.

---

## Concrete Before / After Example

**Creator Input (Weak Draft):**
- Title: `AMAZING MAGNET TRICK YOU MUST SEE!!`
- Opening Line: `Hey guys, welcome back to my channel! Today we are going to look at a really crazy science experiment with copper and a magnet because eddy currents slow it down.`

**What `youtube-creator-skill` Changes & Why (Verified Live Native Run — `EV-01`):**
- **TT-01 Title:** `Why a Copper Pipe Slows Falling Magnets` *(7 words, 39 chars, concrete visual paradox, accurate physics without overclaiming a full stop; `title_linter.py` score `100/100`)*
- **Thumbnail / First-Frame Text (Non-Redundant):** `INVISIBLE BRAKE` *(2 words, zero repeated words from title — `COMPLEMENTARY_LEXICAL`)*
- **0–3s First Spoken Line:** `Copper isn't magnetic—why does it slow falling magnets?` *(9 spoken words, ~3.0s at 180 WPM, `hookscore.py --pov narrative` `fits_3s_first_line: true`, zero channel intro, no self-answering "because")*
- **Clean `SCRIPT.txt` + `STORYBOARD.csv` + `NEXT_EXPERIMENT.md`:** Ready to record (107 spoken words, `ESTIMATED_WPM`), with verified physics mechanism (Lenz's law / eddy currents) cleanly separated from the everyday water-paddle analogy and zero CTA.

See all three complete, schema-validated original demo packs in [`examples/`](examples/):
1. [`examples/01-science-short-copper-magnet/`](examples/01-science-short-copper-magnet/) — Science Short full Creator Action Pack
2. [`examples/02-scam-awareness-reshipping/`](examples/02-scam-awareness-reshipping/) — Defensive Scam Awareness Short Pack
3. [`examples/03-analytics-retention-audit/`](examples/03-analytics-retention-audit/) — Synthetic Retention Curve + Transcript Audit Pack

---

## Core Capabilities (17 Intents + 7 Optional Offline Scripts)

| Workflow Area | What It Does | Optional Stdlib Python Tool (`scripts/`) |
|---|---|---|
| **Research & Competitor Outliers** | Primary-source evidence tables, cohort-safe leave-one-out peer medians (never mixes Shorts & Long-form, never turns missing views into `0`) | `outlier_analyzer.py` |
| **TT-01 Titles & Hook Lab** | Curiosity-gap titles, 21 attributed hook formulas (`assets/hooks.json`), 5-dimension rubric, POV-neutral Shorts mode | `title_linter.py`, `hookscore.py` |
| **KH-01 Storytelling & Visual Plan** | 10 niche narrative modes (History, Science, Scam Awareness, Finance, Gaming, Education, Fiction, Product Demo, Comedy, Lifestyle), WPM-based timing, `SCRIPT.txt` + `STORYBOARD.csv` + `THUMBNAIL_PROMPT.txt` | `validate_output.py` |
| **Retention & Channel Audit** | Shorts views vs. engaged views & stayed-to-watch clarity, percentage-point (`pp`) retention drops, valid >100% rewatch handling, 1-priority-fix audit + Continuous Learning Loop | `retention.py` |
| **Edit Review, Planning, Repurpose, SEO** | Evidence-tagged transcript EDL, exact-count 7/14/30-day capacity calendars, Long-to-Short extraction, honest SEO, comment triage, validated `00:00` chapters | `transcript_analyzer.py`, `chapters.py` |

Every script in `skills/youtube-creator-skill/scripts/` uses **Python 3 standard library only**, runs standalone in an isolated temp folder with zero sibling imports, accepts `stdin` or file input, emits structured JSON to `stdout`, and makes **zero network calls**.

---

## What This Skill Does NOT Do (Honest Boundaries)

- **No video/audio/image rendering:** Does not require or run Remotion, CapCut, FFmpeg, Node.js, or GPUs. Thumbnail prompts are concepts only.
- **No automated YouTube publishing or scraping:** Never logs into your YouTube account, never posts videos or comments, and never asks for OAuth tokens or API keys.
- **No guaranteed CTR, views, or income:** Heuristic hook/title scores and outlier ratios are editorial screening tools — never performance predictions or algorithm folklore ("1K jail", "shadowban").
- **No hidden telemetry or paywalls:** 100% MIT open source and free ($0). Your local `creator-workspace/` stays on your machine.

---

## Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Installation Guide (Windows, macOS, Linux, Native & Universal)](docs/INSTALL.md)
- [Client Compatibility Matrix (Documented vs. Tested)](docs/COMPATIBILITY.md)
- [Natural Language Prompts & Intents](docs/AGENT_COMMANDS.md)
- [Evaluation & Quality Benchmarks](docs/EVALUATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Known Limitations](docs/LIMITATIONS.md)
- [Source Provenance Ledger](docs/PROVENANCE.md) | [Third-Party Notices](THIRD_PARTY_NOTICES.md)
- [Security Policy](SECURITY.md) | [Contributing Guide](CONTRIBUTING.md)

---

## Credits & License

Licensed under the **MIT License** ([`LICENSE`](LICENSE)).

Portions of the 21 hook formulas, optional standalone Python tools, and conceptual storytelling guidelines are adapted from or inspired by these MIT-licensed open-source projects (complete verbatim notices preserved in [`LICENSES/`](LICENSES/) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)):
- [`jakeschincariol/youtube-agent-skill`](https://github.com/jakeschincariol/youtube-agent-skill) (`a2feb2104981a375ffd4f87ee04f4f5344ac43c6`) — Copyright (c) 2026 Jake Schincariol (MIT)
- [`mromidev/claude-animated-shorts`](https://github.com/mromidev/claude-animated-shorts) (`e3b817b6afc6cd413466d43f11ba31209e034bbf`) — Copyright (c) 2026 Mr omi (MIT)

Neither upstream author endorses or is affiliated with this project. YouTube is a trademark of Google LLC; this project is an independent open-source tool and is not affiliated with YouTube, Google, Anthropic, or OpenAI.

---

If `youtube-creator-skill` helps you sharpen your next video or diagnose a retention leak, feel free to star the repository or open an issue with suggestions.
