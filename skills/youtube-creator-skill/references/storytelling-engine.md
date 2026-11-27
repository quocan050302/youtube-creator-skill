# Storytelling & Script Engine — KH-01

Write scripts meant to be **spoken aloud by a human** and **watched**, not read like essays or corporate newsletters.

*(Conceptual pacing principles for surprising-premise escalation, deadpan contrast, everyday analogies, and callback payoffs are informed in part by `mromidev/claude-animated-shorts` (MIT) and `jakeschincariol/youtube-agent-skill` (MIT); see `THIRD_PARTY_NOTICES.md`. The upstream `STYLE_BIBLE.md` observation of 20 Shorts averaging ~3.5–4.1 words/s is cited solely as an upstream historical sample — never as an original measurement or mandatory universal speed.)*

## 1. KH-01 Ten Niche Narrative Modes (Plus Generic Intent)

Select the mode that fits the creator's material — never force every topic into one rigid template:

- **Mode A — True Story / History:** Paradox or concrete action -> concise setting (year/place/stakes) -> 2–4 escalating observable events -> turning point / snap -> mechanism & consequence -> callback/ironic payoff. *(Mark historical reconstructions explicitly; zero invented quotes.)*
- **Mode B — Science / Experiment:** Counterintuitive observable event -> clean control/comparison -> mystery beat -> literal mechanism paired with an accurate everyday analogy -> practical implication/payoff. *(Do not fabricate human drama where physics/biology carries the tension.)*
- **Mode C — Scam Awareness (Defensive Only):** Appealing real-world setup -> subtle anomaly/red flag -> defensive reveal of how the trap works -> real consequence -> concrete recognition & prevention rule. *(Never provide operational fraud instructions.)*
- **Mode D — Finance / Business:** Relatable financial friction -> verified case or explicitly labeled hypothetical numbers -> underlying mechanism -> transparent math & limitations -> one practical takeaway. *(Zero guaranteed profits or personalized financial directives.)*
- **Mode E — Gaming:** Clear setup/rule/challenge -> escalating complication -> mechanical discovery or decision -> resolution/payoff. *(Never fabricate unverified patch notes or claim unseen gameplay footage.)*
- **Mode F — Educational / Tutorial:** Concrete outcome upfront -> step-by-step demonstration with proof -> common failure trap -> verified result -> one memorable takeaway.
- **Mode G — Emotional / Inspirational:** Human tension -> expectation -> complication -> quiet realization -> earned emotional resolution. *(Explicitly distinguish fictional stories from verified real accounts; no invented miracle claims.)*
- **Mode H — Reviews / Product Demo:** Specific real-world problem -> demonstrable test/comparison -> honest limitation/tradeoff -> who it fits (and who should skip) -> clear verdict (+ optional CTA only if requested).
- **Mode I — Comedy / Entertainment:** Relatable or absurd premise -> escalating contrast -> natural rule-of-three escalation (only when organic) -> crisp punchline/callback. *(Humor never overrides truthfulness on factual premises.)*
- **Mode J — Lifestyle / Food / Travel:** Sensory/practical premise -> clear progression with real constraints -> credible result and context. *(Avoid generic trend filler.)*
- **Generic Mode:** For niches outside A–J, use `Promise -> Context -> Escalating Proof/Beats -> Turn -> Payoff`.

## 2. Format Architecture (Shorts vs. Long-Form)
- **Shorts (typically 25–60s):** Hook immediately -> every beat introduces new information, contrast, or escalation -> visual proof or turn near midpoint -> payoff resolving the exact opening loop. Keep any CTA minimal and include it **only** if requested (never weaken the final punchline).
- **Long-Form (typically 4–20+ min):** Opening confirmation & proof of payoff -> distinct chapters/segments with earned transitions -> address counter-arguments or edge cases -> deeper demonstration/evidence -> concise takeaway (recap only if it adds clarity).

## 3. Spoken Voice & Language Craft
- **POV Flexibility:** Choose 1st, 2nd, or 3rd person from the creator's brief/style; do not mechanically open every script with *"Imagine..."* or *"You see..."*.
- **Plain Spoken Rhythm:** Natural contractions (*it's, doesn't, won't*), concrete nouns and active verbs, varied sentence lengths (mix punchy 5–8 word beats with 14–18 word explanations). Strip filler (*"basically"*, *"let's dive right in"*, *"in today's video"*).
- **Visual-Narration Balance:** Avoid redundantly narrating obvious on-screen motion, while still naming key details when viewers need explanation to understand *why* something matters.
- **Multilingual Adaptation:** When writing in Vietnamese, Spanish, Japanese, or another language, write natively for spoken cadence and local phrasing rather than stiff literal translation from English.

## 4. Duration & WPM Estimation Contract
- Formula: `target_words ≈ (duration_target_s - planned_pause_s) * (chosen_wpm / 60)`.
- **Default English WPM Ranges (choose by style/creator preference):**
  - Conversational / tutorial / analytical: **145–175 WPM** (~2.4–2.9 words/s).
  - Brisk / energetic Shorts narration: **180–220 WPM** (~3.0–3.7 words/s).
  - Never default blindly to 222 WPM for every speaker. For non-English languages (especially syllable- or character-based scripts), use language-appropriate spoken rate estimates and note the estimation basis rather than equating tokens with English words.
- **Honest Timing:** Report estimated duration range with exact `word_count` and `wpm_basis` (`timing_basis: "ESTIMATED_WPM"`). Claim exact seconds (`MEASURED_AUDIO`) **only** when real audio or word-level timestamps exist. If draft length misses target, trim filler or deepen substance — never pad with fluff.

## 5. Clean Script Separation Rule
- **`SCRIPT.txt` (or "just the script" chat output):** Strictly pure spoken words. Zero `[ON SCREEN]` cues, zero `[BEAT 1]` headers, zero Markdown formatting, zero unrequested CTAs.
- Put beat labels, visual actions, overlays, and estimated timestamps exclusively in `STORYBOARD.csv` or an optional annotated companion block.
