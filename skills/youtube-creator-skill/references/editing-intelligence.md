# Editing Intelligence & Transcript Review

Turn a timestamped transcript (`.srt`, `.vtt`, or Whisper `.json`) or user edit notes into an honest, evidence-tagged **Edit Decision List (EDL)**. This skill advises — it never cuts or renders media files.

When `CODE` is available and a timestamped transcript is provided, run `scripts/transcript_analyzer.py` first.

## 1. Evidence Tagging Per Observation (Mandatory)
Every issue flagged in an edit review MUST declare how it was observed:
- **`TRANSCRIPT_IMPLIED`:** Inferred from timestamp gaps, filler tokens, or restarted phrasing in `.srt`/`.vtt`/`.json`. *(Important: a gap between subtitle cues is NOT proof of dead air — it could be an intentional visual demonstration, reaction beat, or B-roll payoff!)*
- **`FRAME_OBSERVED`:** Verified directly via `VISION`/`AUDIO/VIDEO` inspection of actual frames.
- **`AUDIO_MEASURED`:** Derived from an actual acoustic/waveform measurement provided by a tool.
- **`ESTIMATED`:** Qualitative pacing note from a plain text script without timestamps.

If the source video/audio file is unavailable, explicitly state that **no video or audio waveform was inspected**.

## 2. Three Primary Transcript Candidates
1. **`GAP_CANDIDATE` (Potential Dead Air):** Spaces between spoken cues exceeding the configurable floor (default `0.45s` Long-form, `0.30s` brisk Shorts). Recommend trimming from the *middle* of the gap so natural breath remains on both edges — and warn the editor to verify no visual action happens during that span.
2. **`FILLER_CANDIDATE`:** Isolated filler cues (*"um"*, *"uh"*, *"basically"*, *"so yeah"*). Flag for review rather than blind deletion if removing it breaks speech rhythm.
3. **`RESTART_CANDIDATE` (False Start / Retake):** Repeated opening phrase across consecutive *speech* cues (skipping intervening `"um"` cues so retakes separated by filler are still caught).

## 3. Edit Decision Table (`EDIT_DECISIONS.csv` / Inline)
Include columns: `priority` (`P0`/`P1`/`P2`), `start_s`, `end_s` (or `UNKNOWN` if untimed), `category`, `evidence_source`, `issue`, `recommended_fix`, `reason`, `expected_tradeoff`, `validation_check`.

- Always warn that percentage-removed figures apply to **transcribed speech gaps only**, not silent demonstrations or visual montages.
- For untimed text transcripts, return qualitative structural tightening only — never invent timecodes.
