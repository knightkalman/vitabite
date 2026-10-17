# Step 6: Build the consumer meal-planning experience

## Goal

Deliver the first end-to-end consumer experience: manage preferences, review explainable meal suggestions, and keep a practical meal plan.

## Prerequisite

Complete [Step 5](./05-meal-recommendation-engine.md). Use the tested recommendation interface and existing identity, consent, and catalog models.

## Agent instructions

Build a usable, accessible consumer application around the existing baseline engine. Be explicit that the current version uses preferences and catalog data, not biomarker-derived personalization. Keep personal data scoped to the signed-in user and avoid unnecessary collection.

## Scope

- Provide an authenticated consumer dashboard and preference editor.
- Let users request, inspect, and save meal suggestions and organize them into a simple daily or weekly plan.
- Show ingredients, preparation steps where available, nutrient estimates with units, allergen information/unknowns, and recommendation explanations.
- Support editing and deletion of saved plans; provide clear empty, loading, validation, and error states.
- Add habit check-ins only if they can be implemented without implying a health outcome; make them optional and user-controlled.
- Add end-to-end or integration coverage for the principal consumer flow, including account boundaries.

## Acceptance criteria

- A user can sign in, set preferences, get explainable suggestions, and save/edit/delete a plan.
- Data is protected from access by other users and changes are persisted using the established architecture.
- Nutrition, allergen uncertainty, and medical limitations are clearly presented.
- The public website and existing automated checks continue to work.
- The agent reports the consumer flow, tests run, and remaining product limitations.

## Handoff

Finish before [Step 7](./07-restaurant-menu-saas.md). Step 7 adds an organization-facing product without weakening consumer data isolation.
