# Step 5: Implement explainable meal recommendations

## Goal

Generate safe, useful meal suggestions from user-selected preferences and the traceable food catalog, with a clear path to future biomarker-informed personalization.

## Prerequisite

Complete [Step 4](./04-nutrition-data-catalog.md). Use only catalog data with known provenance and account/profile functionality already implemented.

## Agent instructions

Implement a transparent baseline recommendation engine, not an opaque model or medical decision system. User preferences and dietary restrictions can guide results; biomarker-driven recommendations must remain disabled until a separately reviewed, validated model and suitable consent exist. Explain why each result was selected and expose unknown or incomplete food data.

## Scope

- Accept validated meal constraints such as dietary pattern, excluded ingredients, declared allergies, preparation time, and meal type.
- Generate ranked meal/recipe suggestions using deterministic, testable rules; expose the factors that affected ranking.
- Enforce hard exclusions, and do not describe an unverified ingredient as safe for an allergy.
- Show nutrient estimates only when supported by catalog data; retain units, serving basis, and source references.
- Handle insufficient catalog coverage gracefully and clearly, rather than inventing recommendations or nutrient values.
- Add tests for constraints, allergen uncertainty, ranking explanations, and missing-data behavior.

## Safety

- Do not diagnose, treat, or prevent disease, prescribe supplements, or guarantee longevity or biological-age outcomes.
- Provide a clear way to seek professional advice for medical nutrition needs; do not suggest the product replaces a clinician.
- Do not use biomarkers or infer disease risk in this baseline engine.

## Acceptance criteria

- Recommendations are reproducible for the same inputs and catalog state.
- Hard exclusions are honored; unknown allergen status is never presented as safe.
- Each recommendation can be inspected and traced to catalog data.
- Existing website, identity, and catalog behavior remains intact.
- The agent reports the algorithm's limits and verification results.

## Handoff

Finish before [Step 6](./06-consumer-meal-planning-app.md), which will expose these recommendations to consumers.
