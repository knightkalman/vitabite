# Step 10: Prepare for launch and measured expansion

## Goal

Harden the product for a controlled Vienna launch and establish a safe, evidence-based path toward new markets, integrations, and sustainable operations.

## Prerequisite

Complete [Step 9](./09-validation-and-product-analytics.md). Base launch decisions on implemented and tested capabilities. Do not treat the presentation's revenue or growth targets as achieved results.

## Agent instructions

Assess the current implementation and address concrete launch-readiness gaps in a staged, reversible way. Do not turn on real clinic, insurer, payment, or health-data integrations without a defined partner, data contract, security review, and required approvals. Avoid claiming regulatory compliance based solely on software changes.

## Scope

- Add production-readiness checks and operational documentation: configuration, migrations, backups/recovery expectations, monitoring, error reporting, and incident response.
- Add rate limits and abuse protections to exposed endpoints appropriate to the stack, with tests where practical.
- If subscriptions or billing are implemented, use a reputable provider's test mode first; clearly handle webhook verification, idempotency, cancellations, and failed payments. Otherwise document billing as not implemented.
- Add localization foundations for Vienna-first launch and record requirements for future Germany, Switzerland, and Nordics expansion (language, units, food labeling, privacy, and market review).
- Document a pilot checklist for restaurant onboarding, data quality, staff feedback, support, and success criteria; keep targets distinct from measured results.
- Add a launch/rollback checklist and verify production build and critical user journeys.
- List integration prerequisites and explicitly defer any partner integration lacking authorization, specifications, or required review.

## Acceptance criteria

- A responsible Vienna pilot can be operated using documented deployment, monitoring, support, and rollback steps.
- Critical user and organization data remains protected under production configuration.
- No test-mode or unavailable integration is represented as live.
- Metrics and expansion statements distinguish estimates, targets, and measured results.
- The agent reports launch blockers, operational risks, checks performed, and remaining approvals or integrations.

## Completion

This step completes the initial implementation sequence. Treat international expansion, biomarker-driven personalization, clinical studies, and insurer/clinic integrations as gated follow-on work requiring the appropriate evidence, partners, privacy review, and qualified oversight.
