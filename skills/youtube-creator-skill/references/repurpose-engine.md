# Long-to-Short Repurpose Engine

A good repurposed Short is **not** a random highlight clip — it is a self-contained micro-story that makes complete sense to a cold Shorts-feed viewer who never saw the long video.

## 1. Source Rights & Timestamp Honesty
- **Ownership Gate:** Assume repurposing applies only to transcripts/videos the creator owns or holds rights to adapt. Never provide tools or instructions for unauthorized downloading or re-uploading of third-party videos.
- **Timestamp Discipline:**
  - When a timestamped transcript (`.srt`, `.vtt`, `.json`) is supplied, quote exact source time spans (`start_s -> end_s`).
  - When only untimed prose/paragraphs are supplied, reference **paragraph/section numbers only** (`Paragraph 3–5`) — **never invent fake timecodes**.

## 2. Candidate Selection Criteria (Rank Top 3–5 Spans)
Scan the source transcript for ~20–55 second spans where ALL three hold:
1. **Standalone Context:** Understandable without needing the previous 4 minutes of setup (or fixable with a single newly recorded 1-sentence opener).
2. **Internal Turn:** Contains a clear claim/expectation followed by a complication, proof, contrast, or counterintuitive reveal.
3. **Clean Payoff Ending:** Ends on a crisp thought or consequence — never trails off mid-transition (*"so anyway, moving to point four..."*).
4. **No Out-of-Context Distortion:** Never slice a quote or claim so it misrepresents the original meaning or drops an essential caveat.

## 3. Required Output Per Selected Candidate (`REPURPOSE.md`)
For each ranked candidate:
- **Source Reference:** Exact `start_s -> end_s` (if timed) or paragraph range (if untimed).
- **Why It Stands Alone:** 1 sentence naming the internal turn and payoff.
- **Estimated Short Duration:** Actual span duration (if timed) or WPM-based estimate (labeled `ESTIMATED_WPM`).
- **Fresh Opening Line (`REWRITTEN_VOICE`):** Write a new 0–3s hook tailored for cold feed viewers (the long video's transitional sentence rarely works cold). Clearly distinguish **`ORIGINAL_EXCERPT`** vs. **`REWRITTEN_OPENER / BRIDGE`** so the creator knows what requires a fresh voiceover pickup vs. existing audio.
- **First-Frame / Opening Text Note:** Complementary 0–3 word visual anchor (if captions/text desired).
- **9:16 Vertical Crop Risk Check:** Note what horizontal `16:9` elements (side-by-side slides, small screen-share UI, wide two-person shots) may be cut off in `9:16` vertical framing and suggest a practical reframe/zoom/overlay fix.
- **Optional Natural Loop Point:** Suggest a seamless loop bridge back into Line 1 **only** when it feels organic — never force artificial looping that harms the ending punch.
