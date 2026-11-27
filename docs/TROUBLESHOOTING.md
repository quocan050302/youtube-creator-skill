# Troubleshooting

## 1. My agent did not automatically trigger `youtube-creator-skill`
- Confirm the directory structure is exact: `<skills-root>/youtube-creator-skill/SKILL.md` (with uppercase `SKILL.md` and lowercase kebab-case folder name).
- Restart or start a new chat session after copying the skill folder.
- Mention the skill name explicitly in your prompt: `"Use youtube-creator-skill to..."`.
- Run `python tools/validate_skill.py` from the repository root to verify frontmatter syntax.

## 2. Python script exits with code `2` ("Invalid input")
Exit code `2` is intentional validation feedback — read `stderr` for the exact cause:
- **`missing_or_invalid_format` (`outlier_analyzer.py`):** Each row must specify `format` (`SHORT` or `LONG`) so Shorts and Long-form baselines are never mixed.
- **`missing_published_or_observed_date` (`outlier_analyzer.py`):** Supply `published_at` and `--as-of YYYY-MM-DD` (or pass `--allow-missing-dates` to group under `age_unknown` with a comparability warning).
- **`duration_s is required when x-axis is normalized percentage` (`retention.py`):** YouTube Studio retention exports often use `0–100%` on the x-axis. Pass `--duration <seconds>` so timestamps map accurately to seconds.
- **`Ambiguous retention y-axis unit` (`retention.py`):** Pass `--rate-unit percent` or `--rate-unit ratio` explicitly.
- **`Input exceeds max allowed bytes`:** Default safety limit is 10 MB; pass `--max-bytes` only if inspecting a larger local file you trust.

## 3. Windows encoding or garbled non-English characters (Vietnamese, Spanish, CJK)
- All bundled scripts open files as `utf-8-sig` and reconfigure `stdout` to UTF-8.
- In Windows PowerShell, if piping output to another tool, set `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`.

## 4. "No web access" or "No vision capability" warnings
- This is honest fallback behavior, not a crash. Paste the facts, transcript, or CSV directly in chat and the skill will run completely offline.
- Never trust an assistant that claims it watched your video or checked live competitor views when no web/vision tool is connected.

## 5. Agensi upload says "no SKILL.md" or "too many files"
- Always upload `dist/youtube-creator-skill-agensi-v<version>.zip` (never the raw repo archive or Universal ZIP, and never a ZIP nested inside another ZIP).
- Verify your archive cleanly with `python tools/build_release.py --version 1.0.0-rc.1 --verify`.
