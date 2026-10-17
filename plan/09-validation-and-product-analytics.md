# Step 9: Establish clinical validation and responsible analytics

## Goal

Prepare a scientifically and ethically responsible path for evaluating VitaBite's product and provide privacy-preserving operational analytics without overstating health outcomes.

## Prerequisite

Complete [Step 8](./08-food-brand-formulation.md). Review the product's actual data flows and capabilities before introducing any study-related or analytics collection.

## Agent instructions

Separate product analytics from clinical research. Implement only appropriate operational metrics and the technical groundwork needed for review; do not start a human-subject study, collect new biomarker data, or claim clinical validation. A study requires qualified clinical, ethics, privacy, and legal review and must not be improvised in software.

## Scope

- Define a concise analytics event and metric catalog for product operations, such as activation, plan saves, restaurant retention, and subscription revenue where billing data exists.
- Aggregate or minimize data; exclude direct identifiers and sensitive health values from analytics events.
- Implement opt-in/consent gates for non-essential analytics where applicable, and provide documented retention and deletion behavior.
- Add internal dashboards or reports only for metrics the product can actually calculate, with clear definitions and cohort limitations.
- Document a proposed study-readiness checklist covering a research question, protocol, endpoints, consent, data minimization, safety monitoring, qualified oversight, and ethics approval; do not represent it as an approved protocol.
- Test consent gating, access controls, aggregation, and deletion/retention behavior.

## Acceptance criteria

- Operational metrics have documented definitions and do not imply biological-age improvement or clinical efficacy.
- Sensitive profile or biomarker values are not emitted into analytics events.
- No research or biomarker collection occurs without separately reviewed consent and oversight.
- Dashboards clearly distinguish measured facts from targets and projections.
- The agent reports privacy choices, metrics implemented, validation performed, and approvals still needed.

## Handoff

Finish before [Step 10](./10-launch-and-expansion-readiness.md). The launch plan must use verified product capabilities and metrics, not roadmap targets as actual results.
