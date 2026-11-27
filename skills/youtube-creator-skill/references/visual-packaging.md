# Visual Packaging, Thumbnail Lab & Storyboard Engine

Title, thumbnail (or Shorts first frame), and first spoken line form **one single promise delivered across complementary surfaces**.

## 1. Thumbnail & Shorts First-Frame Strategy
- **Format Reality Check:**
  - **Long-form (`16:9`):** Custom thumbnail carries major browse/search selection weight alongside the title.
  - **Shorts (`9:16`):** Feed viewers see the **opening frame in motion** before any static cover matters, and custom Shorts frame/cover options vary by YouTube device/client. Verify current YouTube Studio capabilities rather than assuming custom thumbnail upload behavior or claiming algorithm weights.
- **Zero-Duplication Rule:** If the title says *"Why Copper Stops a Falling Magnet"*, the thumbnail text should NOT say *"COPPER STOPS MAGNET"*. Use either zero text (if the visual contrast speaks alone) or **1–3 complementary words** (e.g., *"NOT MAGNETIC"* or *"ZERO CONTACT"* — heuristic guideline, not mandatory).
- **Visual Brief Requirements (`THUMBNAIL_PROMPT.txt`):**
  1. **Single Focal Subject & Action:** One unmistakably readable moment at phone feed size.
  2. **Crop, Framing & Aspect Ratio:** Explicit `16:9` (Long) or `9:16` (Short first frame/cover).
  3. **Lighting, Contrast & Background Simplicity:** High subject-background separation; avoid busy text, cluttered collages, unrelated stock faces, or trademarked third-party logos.
  4. **Prop / Scale & Emotion (if human/character):** Readable expression or clear physical scale cue.
  5. **Mobile Safe Area:** Keep crucial visual details and optional short text clear of Shorts UI chrome (right-side action buttons, bottom caption/title bar) and Long-form bottom-right duration badge.
  6. **Image Prompt Honesty:** Write a clean image-generation/shoot brief in English (or user language). Explicitly state **`CONCEPT_ONLY — no image file generated`** unless an actual image tool ran. Never depict fake/misleading "after" results.
  7. **Rights Safety:** Plan around original creator footage, props, or lawful assets — never replicate a competitor's distinctive thumbnail composition or branding.

## 2. First-Frame Discipline
- Start immediately on an observable anomaly, visual contrast, demonstration, or concrete problem — avoid black fade-ins, 3-second logos, or static talking-head intros unless purposefully motivated.
- Ensure the opening visual and opening spoken sentence **reinforce different parts of the same promise**.

## 3. Beat-to-Visual Storyboard Planning (`STORYBOARD.csv`)
- Align visual beats to **semantic units** in the script (not arbitrary 1-second jump cuts).
- Specify concrete A-roll/B-roll, live demo, simple diagram, camera/framing intent (wide establish -> medium action -> tight proof), justified transitions (cut on thought shift; dissolve on time/place jump), optional minimal overlay text (respect `"no captions"` strictly), and optional sound-cue intent (e.g., impact hit, silence drop, subtle rhythm bed).
- Respect creator constraints (faceless, desk setup, solo creator, zero 3D render dependency).
- **Timing Honesty:** Label timestamps `ESTIMATED_WPM` unless real audio word timings exist (`MEASURED_AUDIO`). Never promise frame-exact sync without actual audio timings.
