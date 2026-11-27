# Portable Creator Context & Workspace Schema

`youtube-creator-skill` never requires a global platform-specific path (such as `~/.claude/youtube/voice.md`) and never blocks useful output behind a 3-video onboarding gate.

## 1. Portable User-Owned Workspace (Optional)

When a creator has `FILE_WRITE` and opts into ongoing memory across uploads, store their files in a user-chosen local folder (default suggestion: `creator-workspace/` — completely separate from the installed skill directory):

- `creator-workspace/creator-profile.md` (from `assets/creator-profile-template.md`)
- `creator-workspace/channel-history.csv` (from `assets/channel-history-template.csv`)
- `creator-workspace/analytics-history.csv` (from `assets/analytics-template.csv`)
- `creator-workspace/experiment-log.md` (from `assets/experiment-log-template.md`)

In chat-only / `TEXT_ONLY` mode, creators can paste their `creator-profile.md` snippet or upload these files at the start of any chat. Never claim automatic cloud sync. Never silently overwrite existing workspace files — show proposed updates or append cleanly.

## 2. Normalized Context Object

Every session conceptually normalizes available creator context using these fields (unknown fields MUST remain `null` or `"unknown"`, never coerced to `0`):

```json
{
  "schema_version": "1.0.0",
  "creator_id": "local-alias-or-null",
  "channel_url": null,
  "format": "SHORT",
  "niche": "science-explainer",
  "audience_market": "US",
  "output_language": "en-US",
  "creator_voice": {
    "style": "faceless-narrator",
    "pov": "third-person",
    "tone": "plain-spoken-deadpan",
    "phrases_used": [],
    "phrases_avoided": ["game-changer", "dive in", "unlock"],
    "no_claim_boundaries": []
  },
  "goal": "retention-and-evergreen-discovery",
  "duration_target_s": 45,
  "spoken_wpm": 165,
  "production_capacity_hours_per_week": null,
  "constraints": [],
  "facts": [],
  "inputs": [],
  "evidence": [],
  "hypotheses": [],
  "prior_content": [],
  "experiments": []
}
```

## 3. Data Provenance Tags (Required Separation)

Tag every factual item or metric internally and in reports using one of four explicit categories:

1. **`SUPPLIED_FACT`:** Provided directly by the creator (with input ID and observation date if given).
2. **`VERIFIED_FACT`:** Checked against a cited public primary/official source during the session (with URL and retrieval date).
3. **`INFERENCE`:** Analytical interpretation or creative hypothesis derived from observed data (never presented as proven causation).
4. **`FICTIONAL_OR_DEMO`:** Clearly labeled hypothetical scenario, fictional story, or synthetic benchmark fixture.

## 4. Voice Inference & Privacy Boundaries

- If the user provides 1–3 of their own past transcripts, infer rhythm, sentence length, vocabulary, and no-claim guardrails without copying identifiable third-party creators verbatim.
- Preserve previously approved user decisions (selected angle, locked facts, no-CTA preference) within the conversation unless the user explicitly asks to change them.
- Never store sensitive PII, ad-revenue tax identifiers, or OAuth tokens in workspace templates.
