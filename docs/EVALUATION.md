# Evaluation & Quality Assurance Methodology

We separate verification into five honest, non-overlapping layers — never conflating a passing unit test or editorial rubric with real YouTube audience performance:

1. **Static Spec & License Compliance (`tools/validate_skill.py`, `tools/audit_licenses.py`):**
   Verifies `SKILL.md` frontmatter, reference integrity, 20 KB Agensi script logic ceiling, zero forbidden imports/sibling reads, byte-for-byte upstream MIT notice parity, and zero leaked private paths.
2. **Deterministic Unit & Integration Suite (`tests/unit/`, `tests/integration/`):**
   Tests all 7 standalone tools across edge cases (Unicode, BOM, European CSV decimals, leave-one-out peer medians, missing vs. zero values, valid `>100%` retention, non-finite rejection, CSV formula-injection neutralization, path-traversal guards, standalone empty-temp-dir subprocess execution, and byte-for-byte reproducible ZIP extraction).
3. **Baseline vs. Adapted Regression Comparison:**
   Compares our refactored scripts against verified Upstream B (`a2feb2104981a375ffd4f87ee04f4f5344ac43c6`) behaviors on identical fixtures to document deliberate improvements (e.g., removing candidate self-contamination in peer median, adding Shorts 0–3s windows, preserving 21 formula IDs).
4. **Frozen 36-Scenario Behavioral Eval Suite (`tests/evals/scenarios.json`):**
   Covers 10+ niches (science, history, scam awareness, finance, gaming, education, emotional/fiction, product demo, comedy, lifestyle), Shorts & Long-form, multilingual requests (English US, Vietnamese, Spanish), narrow-request discipline, missing-tool honesty, prompt-injection defense, and 12 held-out final-gate scenarios.
   - Editorial target: `>= 85%` across applicable 0–2 rubric dimensions with **zero `0` scores** on critical dimensions (factual accuracy/evidence, promise alignment, task completeness, uncertainty honesty, security).
   - **Honesty caveat:** Model rubric evaluation is editorial QA, not empirical YouTube growth prediction. Real A/B performance can only be measured after a creator publishes uploads and tracks post-publish analytics.
5. **Human / Independent Verification:**
   Automated checks cannot substitute for human creator judgment on tone, legal sign-off, or real-world audience fit.
