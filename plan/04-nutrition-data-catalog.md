# Step 4: Create the nutrition and food data catalog

## Goal

Build a traceable, testable food and nutrient catalog that can power meal recommendations, restaurant menus, and later food formulations.

## Prerequisite

Complete [Step 3](./03-identity-consent-and-profile.md). Use its authorization and privacy practices wherever catalog data is private or user-specific.

## Agent instructions

Inspect the current data model and choose a representation that preserves units, provenance, and uncertainty. Do not populate the catalog with invented nutrition facts presented as authoritative. Start with clearly labeled sample data or a documented, appropriately licensed source. Keep source attribution and licensing information with imported data.

## Scope

- Model foods and ingredients, nutrient values with units, serving basis, source/provenance, and update/version metadata.
- Represent allergens and dietary attributes explicitly; unknown must not be treated as absence.
- Provide validated read/search interfaces and administrative import/update mechanisms appropriate to the architecture.
- Include a small, clearly labeled demo catalog so development and later steps can be exercised without real user data.
- Add tests for units, missing/unknown values, provenance, allergen handling, and invalid imports.

## Acceptance criteria

- Nutrient values are never detached from their units, serving basis, and source.
- Allergen unknowns are surfaced safely and are not reported as allergen-free.
- Demo data is clearly identified and not represented as clinically authoritative.
- Catalog access and modification follow the repository's security conventions.
- Existing functionality and relevant tests continue to pass; the agent reports data-source and licensing assumptions.

## Handoff

Finish before [Step 5](./05-meal-recommendation-engine.md). Recommendations must use this catalog and preserve its provenance and uncertainty.
