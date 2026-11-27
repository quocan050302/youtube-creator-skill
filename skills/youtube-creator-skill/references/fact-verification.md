# Fact Verification Protocol

Every material factual claim, number, date, scientific mechanism, or real-world attribution in a YouTube script must pass this verification check before status can be marked `READY_FOR_CREATOR_REVIEW`.

## 1. Claim Classification Taxonomy

| Status | Definition | Script Usage Rule |
|---|---|---|
| `VERIFIED_FACT` | Confirmed during the current session against a cited primary/credible public source (URL + source date + retrieval date recorded). | May be stated directly as fact, with nuance preserved. |
| `SUPPLIED_FACT` | Explicitly supplied by the creator (personal experiment, Studio export, creator notes). | State accurately as supplied; do not extrapolate beyond scope. |
| `INFERENCE` | Logical synthesis or creative interpretation drawn from facts. | Frame honestly as interpretation/hypothesis, never as proven fact. |
| `FICTIONAL_OR_DEMO` | Deliberately fictional story, illustrative hypothetical math, or synthetic demo fixture. | Label clearly as fictional/hypothetical so viewers and creators are never misled. |
| `UNVERIFIED` | Claim mentioned in prompt or draft without accessible supporting evidence. | **Block direct factual assertion.** Either verify via `WEB`, qualify conditionally, cut the claim, or flag for creator verification (`DRAFT`). |

## 2. Historical & Quote Guardrails
- **No Invented Quotes:** Never place newly written dialogue inside quotation marks and attribute it to a real historical or contemporary person.
- **Mark Reconstructions Explicitly:** If illustrating how a historical event felt or unfolded without verbatim records, frame it as reconstruction/paraphrase (*"Contemporary accounts describe..."* or *"In effect, they..."*) rather than fabricated direct speech.
- **Conflict Resolution:** When credible sources disagree (e.g., casualty counts, exact dates, or competing explanations), report the range or acknowledge the disagreement instead of silently smoothing it into false certainty.

## 3. Science & Mechanism Verification
- Verify the **actual physical/technical mechanism** before choosing an analogy.
- Explicitly separate the **everyday analogy** from the **literal mechanism** so educational clarity never turns into scientific error (for example: comparing eddy-current magnetic braking to "magnetic friction" is a useful intuition, while clearly naming induced eddy currents and opposing magnetic fields per Lenz's law as the real mechanism).

## 4. Pre-Script Verification Checklist
- [ ] Every specific number, date, percentage, and named entity maps to an `evidence_id` or explicit hypothetical label.
- [ ] No source URL is guessed from memory without being verified or supplied.
- [ ] Analogies match real mechanisms without overclaiming.
- [ ] Any unresolved claim is listed in `RELEASE_REVIEW.md` and `creator-pack.json -> quality.unresolved`.
