# Step 3: Summarize and categorize with Antigravity

> **Implementation status:** The schema-validated local summarizer and tests
> are implemented in `news/summarizer.py`. It accepts only a private,
> explicitly authorized source-text bundle and writes private summary records;
> it does not publish them. No provider credential is configured, no
> authenticated run has been verified in GitHub Actions, and the current
> metadata-only collector output is not sufficient evidence for summaries.

## Goal

Use the approved Antigravity agent integration to turn collected candidates
into concise, source-grounded summaries with useful categories and tags.

## Prerequisite

Complete [Step 2](./02-daily-collector-agent.md) and Step 1's Antigravity
unattended-integration gate. Use the exact supported invocation, data limits,
and authentication pattern that passed that gate.

## Agent instructions

Implement Antigravity as a constrained research-news summarization and tagging
step, not as an autonomous medical authority. The agent must use only source
material that the project is permitted to process, distinguish what the
article reports from independent evidence, and link every statement to its
source. If the article cannot be accessed or the evidence is unclear, mark the
item for review or withhold it instead of fabricating a summary.

## Scope

- Send Antigravity structured candidate metadata and only the minimum
  permitted text needed for summarization. Do not send secrets, user data, or
  unrelated repository content.
- Require schema-constrained output for: title cleanup, primary category,
  cross-cutting tags, a short original summary, source-grounded key points,
  evidence/uncertainty note, confidence, and review status.
- Assign one primary category from the Step 1 taxonomy: scientific,
  consumer goods, nutrients, or medication. Use controlled, documented tags
  for subjects such as study design, species/population, nutrient, product
  type, or evidence stage.
- In scientific summaries, preserve study design, population/model, sample or
  evidence limits when known, and distinguish association from causation.
- Treat press releases, product marketing, preprints, animal or in-vitro
  findings, and small or preliminary studies as such; do not upgrade their
  evidence level or present promotion as established benefit.
- For medication items, report news descriptively only. Do not recommend
  starting, stopping, dosing, or changing medication and do not offer
  individualized treatment advice.
- Validate outputs against the versioned schema and against source evidence.
  Route low-confidence, conflicting, potentially harmful, and medication
  items to human editorial review or withhold them according to Step 1 policy.
- Keep agent instructions/prompt, model/integration version, run timestamp,
  input references, output, and editorial overrides auditable without
  retaining excess source text.

## Acceptance criteria

- The actual verified Antigravity agent runs through the approved unattended
  integration and emits schema-valid category, tags, summary, evidence note,
  provenance, and review status.
- Representative test cases cover all four primary categories, mixed topics,
  promotional claims, weak/preliminary evidence, inaccessible sources, and
  misleading or unsafe medical claims.
- Summaries introduce no unsupported factual assertions and preserve
  material qualifications from their sources.
- Low-confidence or high-risk items are withheld or visibly routed for review,
  never silently published.
- If Antigravity becomes unavailable, the run fails visibly or leaves items
  queued; it does not produce success-shaped fabricated summaries.

## Remaining verification before Step 4

- Confirm source-specific permission and Google data-processing terms for each
  text bundle; the bundle's authorization flag is an operator attestation, not
  a legal or licensing check.
- Configure the API credential outside source control and verify the SDK's
  structured-output call in the intended scheduled runtime.
- Review representative model outputs against the source text before using
  `approved` output for any publication workflow. The current collector
  provides metadata only, so it cannot by itself satisfy the source-grounding
  acceptance criteria.

## Handoff

Proceed to [Step 4](./04-news-subpage-and-site-integration.md) only with
validated records approved for publication under the editorial policy.
