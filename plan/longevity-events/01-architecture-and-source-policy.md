# Step 1: Define architecture, sources, location taxonomy, and Antigravity integration

## Goal

Make the foundational technical, geographic-classification, and source-policy
decisions needed for a safe, daily-updated longevity events directory that fits
the existing static VitaBite site and mirrors the `longevity-news` architecture.

## Prerequisite

Review the existing site, GitHub Pages workflow, and `longevity-news`
implementation in:

- [`../../public/index.html`](../../public/index.html)
- [`../../public/news/index.html`](../../public/news/index.html)
- [`../../news/policy.md`](../../news/policy.md)
- [`../../news/sources.json`](../../news/sources.json)
- [`../../.github/workflows/longevity-news-collect.yml`](../../.github/workflows/longevity-news-collect.yml)

Keep the existing website and `/news/` service working without regressions.

## Agent instructions

Produce and implement only the foundational event source policy (`events/policy.md`),
versioned JSON schemas (`events/schemas/*.schema.json`), and initial source
registry (`events/sources.json`) needed by later steps. Keep the public site
static. Do not build the collector or publish generated event pages yet.

Reuse the Antigravity verification findings recorded in `news/policy.md`
(official Antigravity Managed Agent / Interactions API and Antigravity Python
SDK with structured outputs), documenting how the same unattended gate and
operator-authorized content bundle apply to event descriptions and call-for-papers
notices.

## Scope

- Define a canonical, versioned event-item schema
  (`events/schemas/event-item.schema.json`) with:
  - `item_id` (stable SHA-256 of canonical URL), `source_id`, `upstream_id`
  - `title`, `organizer` / `publisher`, `source_url`
  - `publication_date` (when listed/announced) and `collected_at`
  - Event timing fields where available: `event_start_date`, `event_end_date`,
    `event_date_raw`, `event_status` (`upcoming`, `ongoing`, `past`, `dates_tba`)
  - Location fields: `primary_location` (`vienna`, `europe`, `us`, `asia`, `other`),
    `location_groups` (array containing applicable filter keys from
    `["vienna", "europe", "us", "asia"]`), `city`, `country`, and
    `attendance_mode` (`in_person`, `hybrid`, `online`, `unspecified`)
  - `tags` (e.g., `conference`, `symposium`, `congress`, `workshop`, `summit`,
    `clinical_trial`, `nutrition`, `geroscience`, `needs_review`)
  - `summary`, `event_notes` (e.g., registration/abstract deadlines or speaker
    highlights when verified), `review_state` (`candidate`, `needs_review`,
    `approved`, `withheld`), `run_id`, and `last_updated_at`.
- Define the location taxonomy and grouping rules:
  - **`vienna`**: Events taking place in Vienna, Austria (e.g., keywords
    `vienna`, `wien`, `austria` paired with Vienna venues/universities such as
    Medical University of Vienna, University of Vienna, Hofburg, Messe Wien,
    Austria Center Vienna). Every `vienna` event also includes `"europe"` in
    its `location_groups` so it surfaces under both **Vienna** and **Europe**
    filters.
  - **`europe`**: Events across European countries and cities (e.g., London,
    Berlin, Munich, Zurich, Basel, Geneva, Paris, Amsterdam, Copenhagen,
    Stockholm, Oslo, Brussels, Madrid, Barcelona, Milan, Rome, Prague, Budapest,
    Warsaw, Dublin, Lisbon, Helsinki, Tallinn, etc., plus Austria outside Vienna).
  - **`us`**: Events across the United States (e.g., Boston, Cambridge,
    San Francisco, Bay Area, San Diego, Los Angeles, New York, Austin, Seattle,
    Chicago, Washington D.C., Bethesda, Miami, Buck Institute / Novato, etc.).
  - **`asia`**: Events across Asia (e.g., Singapore, Tokyo, Kyoto, Osaka,
    Seoul, Beijing, Shanghai, Hong Kong, Taipei, Bengaluru, Mumbai, Tel Aviv,
    Dubai, Abu Dhabi, Doha, Riyadh, etc.).
  - **`other` / Global (`all`)**: Events in other regions (e.g., Canada,
    Australia, Latin America) or purely virtual events without a regional hub.
    These appear under the **All** filter in the UI.
- Create the source registry (`events/sources.json`) conforming to
  `events/schemas/source-registry.schema.json`, using the **same search engines,
  resources, and collection methods** as `news/sources.json`:
  - **NCBI PubMed E-utilities (`pubmed_eutils`)**: Configured with a targeted
    query for longevity/aging congresses, symposia, meeting reports, and
    conference proceedings across global venues.
  - **Nature Aging & Springer Nature RSS (`rss1` / `rss2`)**: Filtered or
    configured for conference announcements, nature conferences, symposia, and
    aging research events.
  - **Approved Longevity & Nutrition Society / Trade RSS & Atom feeds**:
    Publicly accessible feeds for scientific conferences and industry events
    (with any source whose terms page cannot be verified kept `enabled: false`
    until maintainer review, matching the `food_business_news` safeguard in
    `news/sources.json`).
- Specify the GitHub Pages data-publication boundary (`public/events/events.json`
  validated by `events/schemas/public-feed.schema.json`), deduplication rules,
  retention window (keep upcoming events until after `event_end_date` + grace
  period, or 90 days for undated announcements), and correction/takedown policy.

## Required decision gate

Record the Antigravity unattended-operation decision in `events/policy.md`:

- Steps 1–2 and the metadata-only public roundup (`public/events/events.json`)
  run without Antigravity credentials.
- Step 3 reuses the constrained Antigravity Python SDK pattern from
  `news/summarizer.py` and remains manual/private until a maintainer configures
  `ANTIGRAVITY_API_KEY` and verifies permitted source-text bundles.

## Acceptance criteria

- `events/policy.md`, `events/sources.json`, and all schemas in
  `events/schemas/` are created, versioned, and validated.
- Location grouping rules (`vienna`, `europe`, `us`, `asia`, `all`) and
  Vienna-in-Europe inclusion semantics are explicitly documented with examples.
- Sources reuse the same RSS/Atom and NCBI E-utilities engines/methods as the
  news service and document terms/licensing status.

## Handoff

Proceed to [Step 2](./02-daily-collector-agent.md) to build `events/collector.py`
and `events/publish_metadata.py` against the Step 1 schemas and source registry.

