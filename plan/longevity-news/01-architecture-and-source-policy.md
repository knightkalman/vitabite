# Step 1: Define architecture, sources, and Antigravity integration

> **Implementation status:** Implemented in `news/policy.md`, the versioned
> schema files, and `news/sources.json`. The Antigravity route is documented
> from official sources, but an authenticated GitHub Actions request still
> requires a maintainer-provisioned secret and test.

## Goal

Make the key technical and editorial decisions needed for a safe daily news
service that fits the existing static VitaBite site.

## Prerequisite

The existing public site and GitHub Pages workflow are in
[`../../public/index.html`](../../public/index.html) and
[`../../.github/workflows/pages.yml`](../../.github/workflows/pages.yml).
Review the repository before proposing changes; keep the existing site working.

## Agent instructions

Produce and implement only the foundational source policy, data contract, and
documented architecture decisions needed by later steps. Keep the public site
static unless there is a demonstrated requirement for a server. Do not build
the collector or publish generated news yet.

Investigate Antigravity in the actual intended deployment environment. Verify
from authoritative product documentation and available project access whether
it supports unattended, scheduled invocation and structured input/output.
Record the concrete supported invocation method, required permissions, and
credential-handling approach. The agentic desktop application alone must not be
assumed to be a deployable automation API.

## Scope

- Define a canonical, versioned news-item schema with stable ID, title,
  publisher, author where available, canonical source URL, publication date,
  collection date, content-access basis, category, tags, concise summary,
  evidence notes, review state, and last-updated time.
- Define the primary categories:
  - `scientific`: research, trials, reviews, and scientific reporting.
  - `consumer_goods`: consumer-facing food, supplement, wellness, and other
    longevity product announcements or coverage.
  - `nutrients`: nutrient-specific research, reporting, and nutrition guidance.
  - `medication`: drug, therapeutic, and medication-related reporting.
- Allow a primary category and zero or more cross-cutting tags. Document
  category boundaries and ambiguous-item handling.
- Create a source registry format with source name, feed/API URL, publisher,
  source type, topic coverage, update cadence, permitted collection method,
  license/terms notes, trust tier, enabled status, and last checked date.
- Select and justify an initial diverse, relevant allowlist; prefer stable
  RSS/Atom feeds or documented APIs, honor terms and robots guidance where
  applicable, and avoid scraping paywalls or bypassing access controls.
- Specify a data-publication approach compatible with GitHub Pages and existing
  GitHub Actions. Document how daily-generated data reaches the Pages artifact
  without races, secret exposure, or accidental publication of unreviewed or
  invalid records.
- Define article-text and image handling: retain only what is necessary for
  processing; publicly display metadata, original links, and brief original
  summaries, not republished article bodies or unlicensed images.
- Specify retention, freshness indicators, duplicate handling, correction and
  takedown procedures, and criteria for withholding an item.

## Required decision gate

Before Step 2 begins, the project owner must have an evidence-backed decision
on whether the intended Antigravity setup can run unattended with structured
inputs and outputs. Record:

- The supported integration or invocation path and authoritative reference.
- Whether it works in the target scheduled runtime, not only on a developer's
  interactive machine.
- Authentication, data-handling, rate-limit, and licensing constraints.
- A go/no-go result. If unattended operation is unsupported or unverified,
  stop before Steps 2–3 and ask the owner to choose a supported alternative;
  do not claim Antigravity runs daily.

## Acceptance criteria

- The schema and source registry are versioned and have validation rules.
- Every category has an understandable definition and examples.
- Sources, licensing/terms assumptions, content access, and curation process
  are documented.
- The Antigravity go/no-go decision is recorded with verified evidence;
  unsupported capabilities are not assumed.
- The data-publication and security model is compatible with the existing
  GitHub Pages deployment and does not require exposing credentials to the
  static site.

## Handoff

The approved design allows Step 2's metadata-only collector to run without
Antigravity. Do not implement Step 3's summarizer until a maintainer has
configured the official API/SDK path, verified credentials, limits, billing,
data terms, and structured output in the target workflow. If that verification
fails, stop and obtain the owner's decision rather than silently substituting
another summarizer.
