# Longevity-news collection policy

## Architecture and publication boundary

The VitaBite website remains a static GitHub Pages site. A GitHub Actions
workflow runs the collector daily in **UTC** and on authorized manual
dispatches. Collector runs store source-linked candidate metadata in a
private-to-the-repository Actions artifact, separate from the website. The
artifact is retained for 90 days; candidate records themselves expire after
30 days.

**Publication mode selected on 2026-10-17:** the project owner requested that
all items from the latest successful collector run be made live and refreshed
by the background collector. Therefore the static news page publishes the
collected title, source/publisher, source link, publication-date metadata, and
provisional category/tags as an explicitly **unreviewed metadata roundup**. It
does not publish article bodies, generated summaries, or claims of
editorial/clinical review. Each successful or partially successful scheduled
run updates the static feed and deploys Pages in that same workflow. A total
collection failure preserves the previous public feed. Full candidate state
remains in the workflow artifact.

Scheduled workflows can be delayed or disabled by GitHub, so the page reports
the actual collection time and source-level run status rather than implying
that a run happened at an exact minute.

## Antigravity integration decision

**Decision: GO for a later, separately configured Antigravity summarization
step; no Antigravity invocation occurs in Steps 1–2.**

Official Google documentation describes two programmatic routes:

- The [Antigravity managed agent API](https://ai.google.dev/gemini-api/docs/antigravity-agent)
  is called through the Interactions API using an API key and supports a hosted
  remote environment. This is the appropriate unattended route to evaluate
  for a scheduled workflow; it is not the interactive Antigravity desktop app.
- The [Antigravity Python SDK overview](https://antigravity.google/docs/sdk/overview)
  documents an `Agent` runtime, and the
  [SDK structured-output guide](https://antigravity.google/docs/sdk/structured-output)
  documents Pydantic-schema validated JSON output. This supports the required
  programmatic/structured-output design, but the local SDK runtime must be
  evaluated separately from the managed API.

Official references: [Interactions API overview](https://ai.google.dev/gemini-api/docs/interactions-overview),
[Antigravity SDK policies](https://antigravity.google/docs/sdk/policies),
and [Google's Antigravity introduction](https://developers.googleblog.com/en/build-with-google-antigravity-our-new-agentic-development-platform/).
The managed agent's published example uses `GEMINI_API_KEY`, a remote agent
name, and an Interactions API request. SDK structured-output examples use an
explicit response schema. The selected integration, model, accepted schema
mechanism, rate limits, costs, and retention obligations must be re-verified
against the deployed account and current terms before Step 3 is enabled.

**Important deployment qualification:** this checkout has neither the
Antigravity CLI/SDK installed nor an Antigravity API credential, so an
authenticated integration test in the target GitHub Actions environment has
not been performed. This is sufficient to choose an officially documented
unattended integration path, but it is not evidence that a production secret,
quota, or billing setup is configured. Keep summarization disabled until a
maintainer provisions an API key as a GitHub Actions secret, verifies access
and billing, runs a schema-validated test in Actions, and reviews the
provider's current data terms. Never store a key in this repository or in a
public artifact.

## Category taxonomy

Each record receives one rule-based **candidate** category; this classification
is provisional until Step 3 and editorial review.

| Category | Use when the main content is about | Examples |
| --- | --- | --- |
| `scientific` | Aging/longevity research, study methods, trials, reviews, mechanisms, or general scientific reporting without a more specific topic category. | Senescence mechanism; lifespan study; aging cohort review. |
| `consumer_goods` | Consumer-facing longevity products, food, supplements, wellness products, marketing, or product availability. | Supplement launch; longevity-branded food; wearable product coverage. |
| `nutrients` | A named dietary nutrient, food component, or nutrition guidance is the main topic. | Vitamin D and aging; protein intake; omega-3 research. |
| `medication` | A drug, therapeutic, prescription medicine, pharmacological intervention, or medication safety is the main topic. | Metformin trial; rapamycin research; medicine safety report. |

Rule precedence is `medication`, `consumer_goods`, `nutrients`, then
`scientific`. This gives each item one primary bucket; tags can capture
secondary subjects. Unclear cases remain `scientific` with `needs_review`.
Title-only classification is expressly provisional and is not a scientific
assessment.

## Source allowlist and terms

The versioned registry is [`sources.json`](./sources.json) and conforms to
[`schemas/source-registry.schema.json`](./schemas/source-registry.schema.json).
The initial registry has two enabled primary sources and one disabled
candidate pending terms review, rather than unverified broad web scraping:

1. **Nature Aging public RSS:** publisher feed covering aging and longevity
   research. The feed advertises publisher copyright. Collect only feed
   metadata, preserve the publisher and article link, and check current
   Springer Nature terms before any expanded reuse.
2. **Food Business News public RSS (disabled):** specialist food-industry publisher feed,
   filtered by explicit longevity, aging, supplement, and nutrient terms.
   Retain matching article metadata and original links only; the feed may be
   temporarily broader than the project and off-topic entries are discarded.
   The feed is reachable but the linked terms page returned HTTP 403 during
   the 2026-10-17 check. This source remains disabled until a maintainer can
   review the terms and confirm collection/reuse permission.
3. **PubMed via NCBI E-utilities:** primary bibliographic search with a
   bounded, overlapping 30-day publication window. Retain bibliographic
   metadata only; this collector does not request abstracts or full text.
   Follow NCBI's current API policy, use a descriptive User-Agent, bounded
   retries, and remain below NCBI's unauthenticated rate limit.

This is an initial, narrow source set, not comprehensive longevity-news
coverage. Only Nature Aging and PubMed are enabled. Consumer-product news is
not currently collected because the candidate trade source's terms could not
be verified; that category may be absent until an approved source is enabled.
Expand the allowlist through the source-review process rather than implying
balanced coverage that the sources do not support.

Only HTTPS URLs and source-approved article domains are accepted. Source
additions require a maintainer to verify the feed/API, domain, terms/license,
content-access method, topic scope, failure behavior, and a live sample record,
then update the registry's `last_checked_date`. Disabled entries are skipped.
Enabled feed/API availability and linked Nature terms were checked on
2026-10-17; Food Business News terms were not accessible and its source is
disabled. Re-check all terms before launch and whenever a source changes.

## Candidate data contract and content handling

Each record conforms to
[`schemas/news-item.schema.json`](./schemas/news-item.schema.json). Required
fields include a stable SHA-256 ID of its canonical URL, source and upstream
record IDs, title, publisher, author when available, source URL, publication
date and precision when available (with the source's raw date retained),
collection timestamp, access basis, candidate category and tags, review state,
run ID, and last-updated timestamp.

`summary` and `evidence_notes` are deliberately null in collector output.
Collection does not fetch article pages, abstracts, article bodies, or images.
Only public feed/API bibliographic metadata is persisted. Do not bypass
paywalls, authentication, robots restrictions, source quotas, or technical
access controls. A future summarizer must separately confirm its access and
processing basis and publish only original, concise summaries with prominent
source attribution and links.

`candidate` is not an approval state. Collector state remains private in the
workflow artifact. Only the selected metadata fields from the current
successful run are copied to the public feed; there they remain marked
`candidate`, `summary` and `evidence_notes` stay null, and the UI says that
the records and classifications are not reviewed. No malformed, off-domain,
stale, duplicate, or disabled-source record is eligible for this roundup.
This owner-authorized metadata publication mode does not constitute editorial
approval. Future generated summaries must use a separately approved process
and must never be inferred from headlines.

## Dedupe, retention, freshness, corrections, and takedowns

- Canonicalize HTTPS article URLs, remove fragments and common tracking
  parameters, and deduplicate by canonical URL and stable PubMed identifier.
- Merge identical candidates idempotently. Preserve the original discovery
  time and current-run provenance; do not replace an existing record with an
  incomplete duplicate.
- Retain candidate metadata for 30 days. Workflow artifacts expire after 90
  days. No article text is retained.
- Each run reports its timestamp and each source's success, count, and
  failure. An all-source failure fails the job; a partial failure is clearly
  reported and does not erase candidates from successful sources.
- The public page shows the timestamp of the published snapshot's last
  successful collection and flags it as stale after three days. A later
  private collector run is not proof that the public snapshot was updated.
- Maintainers must be able to correct an item, disable a source, and remove a
  candidate/public item on request. Record the decision in the review history;
  do not republish a withdrawn or corrected item from an older artifact.
- Withhold invalid, inaccessible, duplicate, off-topic, clearly promotional
  without independent context, misleading, or potentially harmful material
  for the editorial review stage.

## Security and operations

The scheduled workflow receives read-only repository and Actions metadata
permissions. It has no Pages deployment permission and no third-party API
secret. The feed fetcher has network timeouts, a bounded response size, a small
retry budget, and per-source error isolation. Workflow concurrency is
serialized. Only action run summaries are written to logs; titles, item
payloads, and credentials are not included in the run summary.
