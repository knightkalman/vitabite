# Step 2: Build the scheduled daily collector agent

> **Implementation status:** Implemented as `news/collector.py` and
> `.github/workflows/longevity-news-collect.yml`. It collects metadata
> candidates only; it does not invoke Antigravity or publish to Pages.

## Goal

Collect candidate longevity-news items every day from the approved source
registry and produce validated, deduplicated records for summarization.

## Prerequisite

Complete [Step 1](./01-architecture-and-source-policy.md), including its source
allowlist, data schema, publication architecture, and Antigravity decision
gate. Implement this step only if the chosen hosting and data architecture
supports a secure scheduled agent.

## Agent instructions

Implement the collector as an unattended, scheduled agent with a bounded,
version-controlled task definition. The agent fetches only approved sources,
uses only documented access methods, and emits candidate records rather than
inventing content. Use the verified Antigravity invocation only where Step 1
has confirmed it is supported; do not embed credentials in code, prompts,
artifacts, the website, or logs.

## Scope

- Create a daily scheduled job using the architecture chosen in Step 1. Record
  the timezone explicitly and make manual, authorized reruns possible.
- Fetch approved RSS/Atom feeds or documented APIs with timeouts, bounded
  retries, rate limits, and per-source error isolation.
- Normalize dates, canonicalize URLs, validate required metadata against the
  Step 1 schema, and deduplicate by canonical URL and other documented stable
  keys.
- Record provenance and operational metadata: source, fetch time, publication
  time where available, run ID, item ID, and collection outcome.
- Separate newly collected candidates from already summarized or approved
  items; make reruns idempotent so a retry does not multiply or overwrite
  records unexpectedly.
- Keep intermediate article text ephemeral/minimal and subject to Step 1's
  source terms. Never bypass subscriptions, paywalls, access controls, or
  robots restrictions.
- Add actionable run summaries for success, partial failure, and total
  failure. A failed feed must not silently appear as an empty day of news.
- Limit the scheduler's permissions to collection and the specific storage
  operation it requires; protect generated data against concurrent writes.

## Acceptance criteria

- A manual run can collect approved sample/feed items and produce schema-valid
  records without relying on a developer's logged-in browser.
- Scheduled runs occur once daily in the documented timezone.
- Duplicates, malformed records, unavailable feeds, timeouts, and retries are
  tested; one broken source does not suppress other sources.
- Run history makes the last successful run, per-source status, and partial
  failures visible to maintainers.
- No secrets or unlicensed source text leak into logs, site output, or commits.

## Handoff

Proceed to [Step 3](./03-antigravity-summaries-and-categorization.md) with the
validated, provenance-linked candidate records. Keep unprocessed candidates
out of the public feed. Configure and verify the Antigravity credential and
structured-output integration before enabling that next step.
