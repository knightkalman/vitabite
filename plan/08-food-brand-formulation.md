# Step 8: Add the food-brand formulation workspace

## Goal

Extend the platform for food manufacturers to explore and compare ingredient formulations with transparent nutrition and product constraints.

## Prerequisite

Complete [Step 7](./07-restaurant-menu-saas.md). Reuse the organization/membership, catalog, provenance, and access-control foundations.

## Agent instructions

Build a bounded formulation workflow using available, sourced catalog records. Treat generated formulations as exploratory drafts requiring qualified review, not as manufacturing instructions, regulatory approval, or validated health products. Do not fabricate nutrient, stability, safety, or health-effect data.

## Scope

- Add a workspace-scoped product/formulation model with version history and ingredient quantities.
- Calculate supported nutrient estimates from catalog values and show units, serving basis, provenance, and missing data.
- Allow users to compare versions and explore ingredient substitutions while making trade-offs and constraints visible.
- Represent allergens and unknowns prominently; ensure every export is labeled draft/unverified where appropriate.
- Add a basic export suitable for internal review and tests for calculations, version history, authorization, and uncertainty.

## Acceptance criteria

- A food-brand workspace can create, revise, compare, and export a formulation draft.
- Calculations preserve units and source links; unsupported properties are never invented.
- Drafts are clearly distinguished from approved/compliant products.
- Tenant isolation and earlier product flows remain intact.
- The agent reports calculation assumptions, tests, and required expert review before real-world manufacturing use.

## Handoff

Finish before [Step 9](./09-validation-and-product-analytics.md), which adds a responsible approach to validation and aggregate product metrics.
