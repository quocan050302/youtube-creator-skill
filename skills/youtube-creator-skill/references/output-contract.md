# Creator Action Pack & Output Contract (v1.0.0)

Every output must help a creator make **one clear creative decision** and immediately move into production — not drown them in ten repetitive filler documents.

## 1. Default Chat UX (Compact Mode)

Unless the user asks for a full multi-file pack, keep chat delivery tight and scannable:

1. **Recommended Action** (2–3 sentences: what to make or fix next, and why).
2. **Copy-Ready Deliverable** (exact scope requested: e.g., Title + Hook + Clean Script + First Frame + Visual Beats, or just Titles if title-only).
3. **Evidence & Limitations** (what is verified, what is estimated, what capabilities were unavailable).
4. **Next Experiment** (one falsifiable hypothesis to test on the next upload).

**Strict Narrow-Mode Rules:**
- Title-only request -> return Title options + selected winner + lint notes only.
- Script-only / single-line request -> return pure spoken text only (no headings, no `[ON SCREEN]`, no unrequested CTA).
- No-CTA or No-Captions request -> enforce strictly across script, storyboard, and upload text.

## 2. Full Creator Action Pack (File Output or Labeled Inline Fallback)

When executing a full `GENERATE` or integrated workflow:
- With `FILE_WRITE`: write to a dedicated new folder (`creator-output/<run_id>/` or user-specified folder). Never overwrite existing files silently.
- Without `FILE_WRITE`: emit the exact same files as cleanly labeled Markdown/code blocks inline; never claim files were saved to disk.

### Core Pack Files (`GENERATE` Mode)

| Filename | Purpose & Strict Contract |
|---|---|
| `README.md` | Quick usage guide, pack status (`DRAFT`, `READY_FOR_CREATOR_REVIEW`, or `BLOCKED_MISSING_EVIDENCE`), and exact list of generated files. |
| `CREATOR_BRIEF.md` | Goal, niche, format, audience/market, constraints, recommended angle, and rationale. |
| `RESEARCH.md` | Claim-to-evidence table (`evidence_id`, claim, source URL or user input, source date, retrieved date, status) — or explicit declaration that no web research was performed. |
| `TITLE_HOOKS.md` | Selected title + up to 2 backups, hook options + top 2, first-frame rationale, and heuristic scoring basis/limitations. |
| `SCRIPT.txt` | **Pure spoken voiceover text only.** No Markdown headings, no `[ON SCREEN]` markers, no beat labels, no unrequested CTA. |
| `STORYBOARD.csv` | Columns: `beat_id,start_s,end_s,timing_basis,narration_excerpt,visual_action,shot_intent,overlay_text,audio_cue,source_ref`. Monotonic non-negative intervals aligned to script duration estimate. |
| `THUMBNAIL_PROMPT.txt` | Image concept, focal hierarchy, crop/aspect ratio (`9:16` Short cover/first frame, `16:9` Long thumbnail), lighting/contrast, optional 0–3 word text, exclusions. Explicitly states **concept/prompt only (not a generated image)**. |
| `UPLOAD_PACKAGE.md` | Front-loaded description, honest relevant tags/keywords, optional chapters (Long-form with real timestamps only), optional CTA, and platform cautions. |
| `RELEASE_REVIEW.md` | Quality gate checklist, verified vs unknown claims, unresolved blockers, and explicit reminder that nothing has been uploaded or performance-guaranteed. |
| `NEXT_EXPERIMENT.md` | One testable hypothesis, target metric, comparable cohort/window, confounders, and `CONTINUE`/`ADJUST`/`INCONCLUSIVE` decision rule. |
| `creator-pack.json` | Machine-readable JSON conforming to `assets/output-schema.json` (`schema_version: "1.0.0"`). |

### Mode-Specific Files (Emit Only When Applicable — Zero Dummy Placeholders)
- `AUDIT.md` (`CHANNEL_AUDIT` / `AUDIT_SCRIPT`)
- `ANALYTICS_REPORT.md` (`ANALYTICS_DIAGNOSIS`)
- `CONTENT_PLAN.csv` + `CONTENT_PLAN.md` (+ optional `videos/<day>-<slug>/SCRIPT.txt` when full scripts are requested for multi-day calendars)
- `REPURPOSE.md` (`REPURPOSE`)
- `EDIT_DECISIONS.csv` (`EDIT_REVIEW`)
- `COMMENTS.md` (`COMMENTS`)
- `CHAPTERS.txt` (`CHAPTERS`)

Omit inapplicable files and record the omitted files + reasons in `README.md` / `creator-pack.json`.

## 3. Cross-File Parity & Security Invariants

1. **Exact Selected Consistency:** `SCRIPT.txt`, `creator-pack.json -> script.text`, and `STORYBOARD.csv` narration excerpts must correspond to the *selected* script. `TITLE_HOOKS.md` selected title must match `creator-pack.json -> title.selected`.
2. **Evidence Integrity:** Every `evidence_id` referenced in `recommendation`, `storyboard`, or `RESEARCH.md` must exist in `creator-pack.json -> evidence[]`. Never invent placeholder URLs (`https://example.com/...` as fake citations).
3. **Timing Honesty:** Set `timing_basis` to `"MEASURED_AUDIO"` only when real audio/STT word timings exist; otherwise set `"ESTIMATED_WPM"` with explicit `wpm_basis` and `word_count`.
4. **Status Discipline:** Never label a pack `PUBLISH_READY` when material factual claims remain unverified or required evidence is missing — use `DRAFT` or `BLOCKED_MISSING_EVIDENCE`.
5. **CSV Formula Injection Escaping:** In any exported `.csv`, prefix any **text** cell whose stripped value begins with `=`, `+`, `-`, `@`, `\t`, or `\r` with a leading single quote `'`. Keep legitimate numeric columns (e.g., `start_s`, `end_s`, `views`) as pure finite numbers without string prefixes.
6. **Optional Downstream Integration:** `creator-pack.json` is an open, tool-agnostic JSON schema usable with any editor, script teleprompter, or production pipeline (including optional external renderers) without any required dependency.
