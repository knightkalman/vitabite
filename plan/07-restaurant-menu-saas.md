# Step 7: Build the restaurant menu-planning SaaS

## Goal

Give restaurant teams a multi-user workspace to manage ingredients and menus, explore data-backed menu suggestions, and export useful menu information.

## Prerequisite

Complete [Step 6](./06-consumer-meal-planning-app.md). Reuse the food catalog and recommendation foundations; preserve the consumer experience and its access boundaries.

## Agent instructions

Implement the restaurant use case as a genuine organization-scoped product, not a cosmetic consumer-app variant. Enforce tenant isolation on the server for every read and write. Do not label generated menus as clinically validated or safe for an allergy unless the underlying data and review process support that exact claim.

## Scope

- Add organization/workspace creation and invitations or another explicit membership flow.
- Implement roles with least privilege (for example, owner/admin and editor) and server-enforced membership checks.
- Let a workspace manage menu items, recipes, ingredient substitutions, and menu versions using the shared catalog.
- Provide transparent nutrition estimates and allergen status with source traceability and clear unknowns.
- Support a practical export (such as printable or downloadable menu data) and preserve workspace separation.
- Add tests for role permissions, tenant isolation, menu versioning, and missing/uncertain catalog data.

## Acceptance criteria

- Restaurant users can manage menus in a workspace and export them.
- A user from one workspace cannot read or modify another workspace's data, including through direct API requests.
- Nutrition and allergen statements reflect source quality and never overstate certainty.
- Consumer functionality and existing checks continue to pass.
- The agent reports role model, security tests, and any operational prerequisites.

## Handoff

Finish before [Step 8](./08-food-brand-formulation.md). Step 8 may reuse organization and catalog primitives but must retain tenant boundaries.
