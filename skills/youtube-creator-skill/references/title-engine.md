# Title Engine — TT-01 Title Curiosity Gate

The title's job is to state a clear, truthful promise and open a meaningful curiosity gap — working **with** the thumbnail or opening frame, never duplicating it.

When `CODE` is available, run `scripts/title_linter.py` to check character counts, mobile truncation risk, vague hype words, caps spam, and title-vs-thumbnail word overlap. Remember: all length thresholds and scores are **heuristics**, not official YouTube algorithm rules or CTR guarantees.

## 1. TT-01 Core Rules
1. **Default Language & Adaptation:** Natural English (US) by default; seamlessly localize idiom, word order, and character economy when another language/market is requested.
2. **Format-Aware Length (Flexible Heuristics):**
   - **Shorts:** ~5–8 words preferred for rapid scanability on mobile feeds (flexible preference, not a hard cutoff).
   - **Long-form:** Adapted to promise clarity and search intent; keep the core subject inside the first ~40 characters (mobile home feed caution) and avoid burying the point past ~60 characters (desktop search caution; YouTube hard limit is 100 characters).
3. **Concrete Subject + Action + Tension:** Anchor on a tangible noun, observable event, paradox, surprising contrast, or measurable consequence.
4. **Preserve a Truthful Curiosity Gap:** Do not give away the entire punchline in the title unless explanatory/how-to search intent specifically benefits from naming the solution upfront.
5. **Strict Anti-Spam & Anti-Clickbait Gate:**
   - Reject vague hype adjectives (*amazing, insane, mind-blowing, revolutionary, ultimate, game-changer*) and insider jargon unless explained.
   - Avoid ALL-CAPS shouting (>2 capitalized words) and emoji/exclamation clutter.
   - Verify **100% factual alignment** between the title promise, opening hook, and script payoff. Zero false clickbait.

## 2. Proven Title Archetypes (Rotate — Never Monotone)
- **The Paradox / Event:** *"The X That Y"*, *"Why X Stopped Y"*
- **Mechanism / Cause:** *"How X Defeated Y"*, *"Why X Fails Under Y"*
- **Experiment / Stakes:** *"What Happens If You X?"*, *"I Tested X for [Real Period]"*
- **Diagnostic / Practical:** *"Why Your X Breaks at Y"*, *"How to Fix X Without Y"*
- **Contrast / Comparison:** *"X vs. Y: What Actually Holds Up"*

## 3. Deliverable Discipline
- When asked for titles (`TITLE_PACKAGE`), generate **5–10 varied candidates**, select **1 primary pick** plus **up to 2 distinct backups** with concrete reasons (curiosity gap, clarity, promise match), and surface any lint warnings.
- **Stop at the requested deliverable:** If the user asked only for titles, do not append an unrequested script or full Creator Action Pack.
- Never promise a specific CTR percentage.
