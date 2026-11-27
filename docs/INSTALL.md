# Installation, Update & Uninstall Guide

`youtube-creator-skill` ships as **one canonical skill** with **three access paths**.
Project-local installation is recommended so you never modify global settings unexpectedly.

> **Important Distinction:** Native skill installation applies only to coding/agent runtimes that read `SKILL.md` directories. Standard web chatbots do **not** install native skills — use Path 2 (`UNIVERSAL_PROMPT.md`) for chat interfaces.

---

## Path 1 — Native Agent Installation (Verified Official Paths as of 2026-11-27)

| Client | Project-Local Path (Recommended) | Global User Path (Optional) | Official Docs Source |
|---|---|---|---|
| **Google Antigravity** | `<project>/.agents/skills/youtube-creator-skill/` | `~/.gemini/config/skills/youtube-creator-skill/` | https://antigravity.google/docs/skills |
| **OpenAI Codex** | `<project>/.agents/skills/youtube-creator-skill/` | `~/.agents/skills/youtube-creator-skill/` | https://developers.openai.com/plugins/concepts/skills |
| **Claude Code** | `<project>/.claude/skills/youtube-creator-skill/` | `~/.claude/skills/youtube-creator-skill/` | https://code.claude.com/docs/en/skills |

*(Legacy note: Antigravity also reads `.agent/skills/` for backward compatibility; `.agents/skills/` is the canonical cross-agent path.)*

### macOS / Linux (Project-Local)

```bash
git clone "https://github.com/quocan050302/youtube-creator-skill.git"
# Antigravity or Codex:
mkdir -p ".agents/skills"
cp -R "youtube-creator-skill/skills/youtube-creator-skill" ".agents/skills/youtube-creator-skill"

# Claude Code:
mkdir -p ".claude/skills"
cp -R "youtube-creator-skill/skills/youtube-creator-skill" ".claude/skills/youtube-creator-skill"
```

### Windows PowerShell (Project-Local)

```powershell
git clone "https://github.com/quocan050302/youtube-creator-skill.git"
# Antigravity or Codex:
New-Item -ItemType Directory -Force -Path ".agents\skills" | Out-Null
Copy-Item -Recurse -Force "youtube-creator-skill\skills\youtube-creator-skill" ".agents\skills\youtube-creator-skill"

# Claude Code:
New-Item -ItemType Directory -Force -Path ".claude\skills" | Out-Null
Copy-Item -Recurse -Force "youtube-creator-skill\skills\youtube-creator-skill" ".claude\skills\youtube-creator-skill"
```

### Verify Installation & Version

Check that `SKILL.md` exists inside the target folder and check its `version:` field:

```bash
head -n 10 ".agents/skills/youtube-creator-skill/SKILL.md"
```

Reload or start a new agent session, then test discovery with natural language:
> `"Use youtube-creator-skill to audit this Short script and check hook alignment."`

### Update or Uninstall

- **Update:** Replace the copied `youtube-creator-skill/` folder with the newer version from Git or a verified release ZIP. Never store personal creator files inside the skill directory — keep personal memory in a separate `creator-workspace/` folder so updates never erase your data.
- **Uninstall:** Simply delete `.agents/skills/youtube-creator-skill` (or `.claude/skills/youtube-creator-skill`).

---

## Path 2 — Universal Prompt Mode (ChatGPT, Claude Chat, Gemini, DeepSeek, Grok, Qwen, Copilot)

No install, CLI, or Python required:
1. Open [`universal/UNIVERSAL_PROMPT.md`](../universal/UNIVERSAL_PROMPT.md) (or extract it from the GitHub Universal ZIP).
2. Paste the entire document into a fresh chat (or attach/upload it as a context file).
3. Send your YouTube request right below it.

---

## Path 3 — Agensi Marketplace

Agensi delivers skills to connected agents via its MCP workflow rather than direct buyer ZIP downloads. Once published on Agensi, connect your agent to Agensi MCP and load the free listing. For direct ZIP downloads, always use GitHub Releases.

---

## Optional Python Runtime Check

Core text workflows need **no Python**. To run the 7 optional deterministic scripts in `scripts/`, verify Python 3.10+:

```bash
# macOS / Linux (use python3 if `python` is not aliased):
python3 --version
python3 ".agents/skills/youtube-creator-skill/scripts/hookscore.py" --help

# Windows:
python --version
python ".agents/skills/youtube-creator-skill/scripts/hookscore.py" --help
```
