# Quick Start — YouTube Creator Intelligence

Get your first production-ready Creator Action Pack or analytics diagnosis in under 60 seconds.

## 1. Pick Your Setup Path

- **Have Antigravity, Claude Code, or Codex?** Copy `skills/youtube-creator-skill/` into `.agents/skills/youtube-creator-skill/` (Antigravity / Codex) or `.claude/skills/youtube-creator-skill/` (Claude Code).
- **Using ChatGPT, Claude Chat, Gemini, DeepSeek, Grok, Qwen, or Copilot?** Copy-paste [`universal/UNIVERSAL_PROMPT.md`](../universal/UNIVERSAL_PROMPT.md) into a new chat.

## 2. Five Copy-Ready Starter Prompts

1. **Generate a YouTube Short Pack:**
   > "Use youtube-creator-skill to create a 45-second YouTube Short pack about why airplane windows have a tiny pinhole. Default English (US), faceless narrator, no CTA."
2. **Titles Only (Narrow Request):**
   > "Use youtube-creator-skill to give me 7 TT-01 title ideas only for a Long-form tutorial on fixing audio echo in a small bedroom."
3. **Hook Rewrite:**
   > "Use youtube-creator-skill to rewrite this opening hook and show me the top 2 options: 'Hey guys welcome back! Today I am going to show you an insane budgeting tip that saves money.'"
4. **Retention CSV Diagnosis:**
   > "Use youtube-creator-skill to diagnose this Short's YouTube Studio retention CSV (duration 48s) and give me ONE prioritized experiment for my next upload." *(attach or paste CSV)*
5. **14-Day Capacity-Aware Plan:**
   > "Use youtube-creator-skill to build a 14-day Shorts content calendar (1 Short/day) for a personal finance awareness channel in English (US). I have 6 hours/week."

## 3. Optional Offline Python Tools (When Code Execution Is Available)

Run any helper script directly with Python 3.10+ (zero `pip install` needed):

```bash
python skills/youtube-creator-skill/scripts/hookscore.py --shorts-story --hook "Copper isn't magnetic, yet it stops a falling magnet in midair."
python skills/youtube-creator-skill/scripts/title_linter.py --format SHORT --title "Why Copper Stops a Falling Magnet" --thumb "NOT MAGNETIC"
python skills/youtube-creator-skill/scripts/outlier_analyzer.py competitors.json --min 2.0 --as-of 2026-11-27
python skills/youtube-creator-skill/scripts/retention.py retention.csv --format SHORT --duration 45 --transcript captions.srt
python skills/youtube-creator-skill/scripts/transcript_analyzer.py captions.srt --floor 0.45
python skills/youtube-creator-skill/scripts/chapters.py --validate chapters.txt --duration 540
python skills/youtube-creator-skill/scripts/validate_output.py creator-pack.json
```
