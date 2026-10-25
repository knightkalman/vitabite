# Step 2: Build the scheduled daily events collector agent

## Goal

Collect candidate longevity conference and event listings every day from the
approved source registry (`events/sources.json`) using the same fetching,
parsing, and validation methods as `news/collector.py`, and assign provisional
location groups (`vienna`, `europe`, `us`, `asia`, `other`) and event tags.

## Prerequisite

Complete [Step 1](./01-architecture-and-source-policy.md), including
`events/policy.md`, `events/sources.json`, and the JSON schemas in
`events/schemas/`.

## Agent instructions

Implement `events/collector.py`, `events/publish_metadata.py`, and
`.github/workflows/longevity-events-collect.yml` following the exact engineering
patterns of `news/collector.py`, `news/publish_metadata.py`, and
`.github/workflows/longevity-news-collect.yml`. Rely exclusively on the Python
standard library (`urllib.request`, `xml.etree.ElementTree`, `json`, `hashlib`,
`datetime`, `re`) and `jsonschema` for validation. Do not scrape behind
paywalls, bypass `robots.txt`, or embed credentials.

## Scope

- Implement `events/collector.py` supporting the same source types and methods
  as `news/collector.py`:
  - `rss` (`rss1`, `rss2`, `atom`) and `pubmed_eutils` (NCBI ESearch + ESummary)
    with a 20-second timeout, 3 bounded retries with exponential backoff, 5 MB
    response cap, redirect-host verification, and per-source error isolation.
  - Event-relevance filtering: where a general feed is used, match event-related
    keywords (`conference`, `symposium`, `congress`, `workshop`, `summit`,
    `forum`, `annual meeting`, `colloquium`, `seminar`, `call for abstracts`,
    `registration`) alongside longevity/aging/nutrition scope terms.
- Implement deterministic rule-based **location extraction and grouping**:
  - Inspect title, publisher/venue metadata, and feed category/location fields
    for geographic indicators:
    - **`vienna`**: Matches `Vienna`, `Wien`, or Vienna-specific institutions;
      sets `primary_location = "vienna"` and
      `location_groups = ["vienna", "europe"]`.
    - **`europe`**: Matches European countries, ISO codes, or major European
      conference cities; sets `primary_location = "europe"` and
      `location_groups = ["europe"]`.
    - **`us`**: Matches United States names, state abbreviations with city
      context, or major US research hubs; sets `primary_location = "us"` and
      `location_groups = ["us"]`.
    - **`asia`**: Matches Asian countries or major Asian conference cities; sets
      `primary_location = "asia"` and `location_groups = ["asia"]`.
    - **`other`**: When no specific region in the four groups is detected (or
      the event is global/online), sets `primary_location = "other"` and
      `location_groups = []` (still visible under the **All** view in the UI).
  - Extract lightweight date hints (`event_start_date`, `event_end_date`, or
    `event_date_raw`) and attendance mode (`in_person`, `hybrid`, `online`,
    `unspecified`) when present in feed metadata.
- Implement `events/publish_metadata.py` to transform the collector state into
  `public/events/events.json`, validated against
  `events/schemas/public-feed.schema.json`.
- Create `.github/workflows/longevity-events-collect.yml`:
  - Runs daily on a UTC cron schedule (staggered from `longevity-news-collect.yml`,
    e.g., `47 5 * * *`) and supports `workflow_dispatch`.
  - Downloads the previous `longevity-events-candidates` artifact, runs
    `python3 -m events.collector`, uploads the updated 90-day artifact, runs
    `python3 -m events.publish_metadata`, and deploys the updated `public/`
    artifact to GitHub Pages when collection succeeds or partially succeeds.
- Add comprehensive unit tests in `tests/test_events_collector.py` and
  `tests/test_events_publish_metadata.py`.

## Acceptance criteria

- Running `python3 -m events.collector --state /tmp/vitabite-events-candidates.json --run-id local`
  fetches enabled sources, validates candidates against
  `events/schemas/event-item.schema.json`, and outputs a clear run summary.
- Location classifier unit tests verify accurate mapping for **Vienna**
  (and its dual inclusion in **Europe**), **Europe**, **US**, **Asia**, and
  global/**All** fallback cases.
- Duplicates, malformed URLs, off-domain links, and partial source failures are
  isolated and tested.
- No secrets or full third-party page bodies are stored in git or public files.

## Handoff

Proceed to [Step 3](./03-antigravity-summaries-and-categorization.md) with
schema-validated candidate event records.

