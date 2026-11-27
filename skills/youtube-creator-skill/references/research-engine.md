# Research Engine

Turn a raw topic, niche, or question into a grounded evidence table and distinct original angles before writing a single word of script.

## 1. Inputs & Outputs
- **Inputs:** topic or niche, target audience & market, format (`SHORT` / `LONG`), creator goal, optional public URLs or creator-supplied notes.
- **Outputs (`RESEARCH.md` / inline brief):**
  1. Core audience question being answered.
  2. Structured Evidence Table (`evidence_id`, claim, source URL or `user_input`, publication/source date, retrieval date UTC, status).
  3. 3–10 differentiated creative angles (when angle exploration is requested).
  4. Recommended angle with clear rationale and linked `evidence_ids`.
  5. Open uncertainties and concrete next verification steps.

## 2. Source Priority & Evidence Discipline
1. **Primary & Official First:** Academic/institutional summaries, government/regulatory advisories (e.g., FTC/CPSC/official consumer warnings), manufacturer specs, official platform documentation, or verifiable historical archives over second-hand blogs or recycled viral posts.
2. **Corroborate Disputed Claims:** If a surprising number, historical quote, or causal mechanism is disputed, check at least two independent credible sources. Clearly state *"Source A reports X; Source B reports Y"* rather than picking the more sensational number.
3. **Time-Sensitive Data:** Always note the exact publication/source date and session retrieval date. Never treat a 2022 rule or platform metric as guaranteed current in 2026 without checking.
4. **Strict Anti-Fabrication Rules:**
   - Never invent citations, URLs, quotes, subscriber counts, video view counts, ad revenue, trend scores, or search volumes.
   - Never claim an unseen video transcript or webpage was read.
   - When `WEB` is unavailable: build strictly on `SUPPLIED_FACT` inputs or clearly labeled conditional/hypothetical premises, list exact research questions the creator must verify before recording, and mark pack status `DRAFT` (or `BLOCKED_MISSING_EVIDENCE` if verification is mandatory).

## 3. Sensitive Niche & Safety Boundaries
- **Finance / Investing / Tax:** Never promise guaranteed returns, risk-free savings, or personalized investment advice. Use verified numbers or explicitly labeled hypothetical arithmetic with transparent assumptions and downside risks.
- **Health / Medical:** Use educational framing backed by reputable medical/public-health sources; never prescribe individualized medical treatment or claim miracle cures.
- **Legal / Crime / Scams:** Cover scams strictly defensively (how the trap appears, red flags, verification steps, reporting channels). Never output operational playbooks, social-engineering scripts, or technical exploitation steps for committing fraud.
- **Real People & Organizations:** Never make unverified defamatory accusations. Distinguish confirmed public findings (e.g., court rulings, regulatory orders) from allegations.
