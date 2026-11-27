# Hook Lab & Rubric

A hook earns the next 20 seconds by confirming the click/scroll promise and creating an open loop the viewer wants closed — never by announcing who you are or summarizing the ending.

## 1. Format Opening Standards
- **YouTube Shorts — Strict 0–3s Spoken First-Line Gate:**
  - Open directly on an observable action, paradox, visual contrast, or immediate stake.
  - Zero channel intro, zero *"Hey guys"*, zero *"In this video"*.
  - **Word-count honesty rule:** At conversational-to-brisk pace (`150–180 WPM`, or `2.5–3.0 words/s`), **0–3s holds at most 7–9 spoken words** (up to 10 words at brisk ~200 WPM; remember spoken numbers like `$2,000` count as 3 spoken words).
  - **Never market an 11–20+ word spoken line as `0–3s`.** Either tighten the first spoken line to `<= 9` spoken words so the tension lands inside 0–3s, OR label a longer multi-clause setup honestly as `0–5s` / `0–6s` setup while letting the `0.0s` visual carry the 0–1s scroll-stop.
  - Never attach `ESTIMATED_WPM` runtime ranges to unscripted bullet outlines — compute WPM timing only on actual drafted spoken words.
  - Pair the **first spoken sentence** with a **complementary first frame**: the visual shows the concrete anomaly while the voice states the tension (avoid narrating what is already obvious unless clarifying a mechanism).
- **Long-Form (~15–30s, tailored to video length and genre):**
  - Confirm the title's exact promise in the opening line.
  - Show early proof that the payoff/artifact/experiment is real.
  - Establish the central question and transition straight into Beat 1 without a subscribe pitch or throat-clearing.

## 2. 21 Attributed Hook Formulas (`assets/hooks.json`)
Adapted from `jakeschincariol/youtube-agent-skill` (MIT; see `THIRD_PARTY_NOTICES.md`). Use as a **diverse option bank**, not rigid boilerplate:
`the-statistic`, `someone-elses-result`, `the-mistake`, `contrarian-flip`, `the-reveal`, `the-superlative`, `the-clock`, `i-tried-it`, `the-question`, `the-before-after`, `the-teardown`, `the-stack`, `the-warning`, `the-list`, `the-receipt`, `the-insider`, `the-impossible`, `the-comparison`, `the-origin`, `the-deadline`, `the-direct-address`.

Also support narrative third-person paradox/action openers (for story/history/science Shorts) where forcing `"you/your"` would sound unnatural — pass `--pov narrative` (or `--shorts-story`) when running `scripts/hookscore.py`.

## 3. Five-Dimension Hook Rubric (0–2 Each, Total 0–10)

| Dimension | 0 (Weak) | 1 (Workable) | 2 (Strong) |
|---|---|---|---|
| **Specificity** | Vague hype/abstract nouns | Named topic, soft detail | Concrete subject, number, action, or entity |
| **Immediate Comprehension** | Jargon or tangled clause | Clear on second read | Understood in one breath on first listen |
| **Curiosity / Stakes** | Flat summary or self-answering | Mild tension | Clear paradox, risk, or unanswered "why/how" |
| **Promise Alignment** | Detached from title/first frame | Broadly related | Confirms title promise directly without repeating it verbatim |
| **Speakability & Visual Potential** | Tongue-twister / static talking | Readable, passive visual | Crisp spoken rhythm + unmistakable opening visual |

- **Hard Override:** Any factually false, fabricated, harmful, or misleading clickbait hook **FAILS** regardless of score.
- **Tool vs. Manual Labeling:** Only report deterministic numeric rubric output from `scripts/hookscore.py` if the script actually executed in the session. Otherwise label ratings as **manual heuristic review**. Never present hook scores as retention predictions.

## 4. Hook Lab Workflow
- When asked for hooks (`HOOK_LAB`), write **5 genuinely different options** (distinct angles/formulas, not minor synonym swaps), pick the **top 2** with rubric explanations and failure-mode warnings, and explain how each pairs with the first frame.
- When rewriting a weak hook, diagnose the exact failure (e.g., *buried subject*, *self-answering clause*, *generic intro*, *title mismatch*) and fix that root issue rather than adding fake hype.
