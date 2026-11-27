# Contributing to YouTube Creator Intelligence

Thank you for helping improve `youtube-creator-skill`! This project is 100% free
and open source under the MIT License.

## Ground Rules

1. **Keep Core Offline & Dependency-Free:**
   Text-mode workflows must require zero external tools, zero API keys, and zero
   paid subscriptions. Optional scripts under `skills/youtube-creator-skill/scripts/`
   must use Python 3 standard library only and run standalone as single files
   (no sibling imports or relative file reads).
2. **Evidence Over Folklore:**
   Never claim guaranteed CTR, views, revenue, or unverified YouTube algorithm
   internals. Label heuristic scores honestly as heuristics.
3. **Rights & Privacy First:**
   - Do not commit private YouTube Studio exports, real personal analytics, API
     keys, or copyrighted third-party scripts/images/frames.
   - Any third-party code or data contribution must be MIT-compatible and
     documented in `THIRD_PARTY_NOTICES.md` and `docs/provenance.json`.
4. **Single Source of Truth:**
   Edit canonical files in `skills/youtube-creator-skill/`. Do not hand-edit
   generated outputs like `universal/UNIVERSAL_PROMPT.md` or built ZIPs in
   `dist/`; regenerate them using the scripts in `tools/`.

## Running Checks Locally

Requires Python 3.10+.

```bash
# 1. Run deterministic unit, integration, security, and standalone CLI tests
python -m unittest discover -s tests -p "test_*.py" -v

# 2. Validate SKILL.md frontmatter, links, and line/token budgets
python tools/validate_skill.py

# 3. Verify MIT license texts, notices, and provenance ledger
python tools/audit_licenses.py

# 4. Regenerate the self-contained universal prompt
python tools/build_universal_prompt.py

# 5. Build and verify reproducible distribution archives
python tools/build_release.py --version 1.0.0-rc.1 --verify
```

## Proposing Changes

1. Fork the repository and create a topic branch from `main`.
2. Add or update tests in `tests/` for any new logic or bug fix.
3. Run the full verification suite (`python tools/run_qa.py`).
4. Open a pull request describing what changed, why it helps creators, and what
   checks you ran.
