# Known Limitations & Honest Boundaries

1. **No Media Production or Editing Execution:**
   This skill outputs text, tables, JSON contracts, and visual/audio concepts only. It does **not** render MP4 videos, synthesize TTS audio, generate PNG thumbnails (unless your agent separately invokes an image tool), or cut footage in an NLE.
2. **No YouTube Account Access or Auto-Publishing:**
   Nothing is ever uploaded, renamed, pinned, or commented automatically on YouTube. Every workflow ends in human-reviewed copy-ready deliverables.
3. **Heuristics Are Not Performance Predictors:**
   - `hookscore.py` and `title_linter.py` check lexical clarity, length cautions, vague hype, and word overlap. High scores do **not** guarantee high CTR or viral reach.
   - `outlier_analyzer.py` identifies historical relative standouts within same-channel cohorts; correlation in title wording does **not** prove causation.
4. **Retention & Transcript Limits:**
   - A retention drop shows *when* viewers left, not *why*. Without inspecting video and audio, transcript alignment is strictly a **possible contributor**.
   - A gap in `.srt`/`.vtt` captions (`transcript_analyzer.py`) does **not** prove silent dead air; always check footage for silent demos or visual payoffs before cutting.
5. **Estimated Duration vs. Measured Audio:**
   Duration numbers without an audio file (`ESTIMATED_WPM`) depend on your real speaking speed and pauses. Always verify critical Short lengths by reading aloud with a timer.
6. **Offline Knowledge & Web Availability:**
   Without an active `WEB` tool, time-sensitive facts (recent patch notes, current platform policy details, live competitor stats) cannot be verified automatically and are marked `UNVERIFIED` / `DRAFT`.
7. **Validator Scope:**
   `scripts/validate_output.py` validates our defined structural, numeric, evidence-reference, and cross-file subset of `creator-pack.json` v1.0.0 in stdlib Python — it is not a full JSON Schema Draft 2020-12 engine and does not replace human editorial review.
8. **Release Candidate Scope (`v1.0.0-rc.1`):**
   Multi-client native certification across external desktop/CLI agents (`codex`, `claude`), 3 external web chats, and live Agensi marketplace review remain pending external verification (see `docs/COMPATIBILITY.md`).
