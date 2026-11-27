# Client Compatibility Matrix

This matrix explicitly separates **officially documented paths (`DOC_ONLY`)** from **live execution-tested environments (`PASS` / `NOT_RUN`)**. We never claim a client is execution-certified unless an actual session ran on that client.

> **Legend:**
> - `PASS`: Executed live in this environment with logged evidence.
> - `DOC_ONLY`: Install path verified against official vendor documentation; live runtime not installed on the current build host.
> - `NOT_RUN`: Not executed in this run (external client/service unavailable).
> - `BLOCKED`: Blocked by missing account/external access.

## 1. Native Agent Clients (Agent Skills Standard)

| Client | Version / Host OS | Install Method | Native Discovery | Text Mode | File R/W | Python Code | Web / Vision | Evidence / Notes | Status | Date |
|---|---|---|---|---|---|---|---|---|---|---|
| **Google Antigravity** | Windows 11 (Python 3.12.10) & macOS 14.4.1 ARM64 (Python 3.13.0) | Project `.agents/skills/youtube-creator-skill/` or `~/.gemini/config/skills/` | Verified (spec + fresh subagent load) | PASS | PASS | PASS | Web search / session-dependent | Fresh-context isolated customer ZIP runs + isolated CLI tests executed | **PASS** | 2026-11-27 |
| **OpenAI Codex** | Not installed on build host | Project `.agents/skills/youtube-creator-skill/` or `~/.agents/skills/` | Verified against official docs | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | `codex` CLI unavailable on host (`NOT_FOUND`); path matches official docs | **DOC_ONLY / NOT_RUN** | 2026-11-27 |
| **Claude Code** | Not installed on build host | Project `.claude/skills/youtube-creator-skill/` or `~/.claude/skills/` | Verified against official docs | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | `claude` CLI unavailable on host (`NOT_FOUND`); path matches official docs | **DOC_ONLY / NOT_RUN** | 2026-11-27 |

## 2. Universal Prompt Mode (Copy-Paste / File Upload)

`universal/UNIVERSAL_PROMPT.md` requires zero native skill discovery, zero local scripts, and zero relative file links.

| Runtime Category | Candidate Hosts | Prompt Parity Check | Zero-Tool Execution Test | Status | Notes |
|---|---|---|---|---|---|
| **Fresh Text-Only Agent Context (Antigravity isolated prompt test)** | Antigravity fresh subagent (no skill folder access, prompt pasted) | PASS | PASS (evaluated in `06_BEHAVIOR_EVAL.md`) | **PASS** | Verified zero unresolved paths, full MIT notices, narrow-request & safety compliance |
| **External Consumer Chat Apps** | ChatGPT, Claude Chat, Gemini Web, DeepSeek, Grok, Qwen, Copilot | Validated self-contained UTF-8 prompt (~68 KB / ~17k tokens) | NOT_RUN on external web UIs | **DOC_ONLY / NOT_RUN** | Model context & tool availability vary by user plan; text-only qualitative mode requires no tools |

## 3. Marketplace & Isolated Script Sandbox (Agensi)

| Target | Packaging Checks | Isolated Single-File Script Execution | Live Agensi Upload / Review | Status | Notes |
|---|---|---|---|---|---|
| **Agensi Packaging & Isolated Sandbox Simulation** | PASS (`<= 90` files, `<= 1 MB`, 1 `SKILL.md`, UTF-8 text only, zero bundled deps, logic `<= 20 KB`/script) | PASS (all 7 scripts copied individually to empty temp directories & run via fresh Python subprocess) | **BLOCKED / OWNER_MANUAL** (requires owner Agensi account & explicit publish review) | **LOCAL_PREFLIGHT_PASS / LIVE_UPLOAD_PENDING** | See `docs/MARKETPLACE_LISTING.md` for manual upload handover |

## Release Gate Transparency

Because external native clients (`codex`, `claude`), 3 distinct consumer web chats, and live Agensi upload were not executed live, this release is honestly versioned **`v1.0.0-rc.4`** (Release Candidate) rather than certified multi-client stable `v1.0.0`.
