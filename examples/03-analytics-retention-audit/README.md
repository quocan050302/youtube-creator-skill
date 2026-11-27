# Demo 3 — Synthetic Shorts Retention & Mid-Video Leak Diagnosis Pack

> **Data Provenance:** 100% synthetic labeled dataset (`FICTIONAL_OR_DEMO`) created to demonstrate honest YouTube Shorts retention curve analysis (`retention.py`) with valid `>100%` rewatch handling and non-causal transcript alignment.

- **Status:** `READY_FOR_CREATOR_REVIEW`
- **Mode:** `ANALYTICS_DIAGNOSIS`
- **Format:** `SHORT` (`45s`)
- **Tool Executed:** `scripts/retention.py` (Python 3.12 stdlib, offline)

## Included Files
- `synthetic_retention.csv` — synthetic 10-point retention export (`0s..45s`, includes a valid `108.5%` rewatch spike at `28s`)
- `synthetic_transcript.srt` — synthetic timestamped captions
- `ANALYTICS_REPORT.md` — full non-causal diagnosis & cohort separation
- `NEXT_EXPERIMENT.md` — single controlled next-upload hypothesis
- `creator-pack.json` — schema-validated v1.0.0 output contract
