# Longevity events project — Execution Plan

## Project summary

Build a trustworthy, daily-updated global longevity conferences and events
service as a subpage of the VitaBite website (`/events/`), modeled directly on
the [`longevity-news`](../longevity-news/README.md) architecture. A scheduled
collector agent gathers longevity, healthy aging, nutrition science, and
geroscience conferences, symposia, congresses, and community events from the
same search engines, feed types, resources, and collection methods used for the
news site (approved RSS/Atom feeds, NCBI/PubMed E-utilities event/congress
queries, and curated scientific publisher/society event feeds). Antigravity
summarizes, normalizes event metadata (dates, venue, organizer, format), and
assigns location groupings and tags from authorized source material. Readers
browse the resulting directory at `/events/` on the existing GitHub Pages site,
filtering events by location group: **All**, **Vienna**, **Europe**, **US**,
and **Asia**.

The five implementation steps below are sequential and intended to be handed
to coding agents one at a time. Each step defines its prerequisite, task,
acceptance criteria, and handoff.

## Current implementation status

- Steps 1–5 are implemented in the repository (`events/`, `public/events/`,
  `.github/workflows/longevity-events-collect.yml`, and `tests/test_events_*.py`).
- The collector has been run against the 6 enabled sources (`nature_aging_events`
  and the 5 regional/global PubMed E-utilities queries) and published 72
  schema-validated event records into `public/events/events.json` across
  **Vienna** (15), **Europe** (30, including Vienna), **US** (9), **Asia** (20),
  and **All** (72).
- GitHub Actions is configured to collect daily at 05:47 UTC, retain a rolling
  90-day candidate-state artifact, update `public/events/events.json`, and
  deploy the static site to `https://knightkalman.github.io/vitabite/events/`.

## Plan files

1. [Architecture, sources, location taxonomy, and Antigravity integration](./01-architecture-and-source-policy.md)
2. [Scheduled daily events collector agent](./02-daily-collector-agent.md)
3. [Antigravity event summaries and location categorization](./03-antigravity-summaries-and-categorization.md)
4. [Events subpage (`/events/`) and main-site integration](./04-events-subpage-and-site-integration.md)
5. [Operations, safeguards, and launch](./05-operations-and-launch.md)

## Execution architecture and reuse from `longevity-news`

To keep the repository coherent, maintainable, and dependency-light, the
longevity events implementation reuses the proven patterns, utilities, and
safeguards from [`news/`](../../news/) and [`public/news/`](../../public/news/):

| Layer | `longevity-news` reference | `longevity-events` implementation |
| --- | --- | --- |
| **Policy & schemas** | `news/policy.md`, `news/schemas/*.schema.json` | `events/policy.md`, `events/schemas/*.schema.json` (`event-item`, `source-registry`, `public-feed`, `permitted-content`, `summarized-event`) |
| **Search engines & resources** | `news/sources.json` (RSS1/RSS2/Atom feeds + NCBI PubMed E-utilities API) | `events/sources.json` using the same RSS/Atom + NCBI E-utilities engines filtered for conferences, symposia, congresses, workshops, and calls for abstracts, plus approved academic/longevity event feeds |
| **Collector method** | `news/collector.py` (`fetch_bytes`, `canonicalize_url`, XML/JSON parsing, SHA-256 IDs, rule-based provisional classification) | `events/collector.py` reusing bounded HTTP fetching, domain allowlists, URL canonicalization, and deterministic rule-based location detection (`vienna`, `europe`, `us`, `asia`) + event-type tagging |
| **Metadata publisher** | `news/publish_metadata.py` | `events/publish_metadata.py` publishing validated candidate/approved event metadata to `public/events/events.json` |
| **Antigravity SDK** | `news/summarizer.py` (tools disabled, strict Pydantic/JSON schema, paragraph-cited key points, private audit log) | `events/summarizer.py` extracting structured event summaries, verified dates/venues, and confirmed location groups from permitted content bundles |
| **Frontend UI** | `public/news/index.html`, `news.css`, `news.js` | `public/events/index.html`, `events.css`, `events.js` with location filter bar (`All`, `Vienna`, `Europe`, `US`, `Asia`) |
| **CI/CD automation** | `.github/workflows/longevity-news-collect.yml` | `.github/workflows/longevity-events-collect.yml` running daily in UTC, storing rolling artifacts, updating `public/events/events.json`, and deploying GitHub Pages |

## Location grouping model (`Vienna`, `Europe`, `US`, `Asia`, `All`)

Instead of filtering primarily by article topic, the events service organizes
items by geographic location so researchers, clinicians, founders, and readers
can find conferences near them or globally (with special emphasis on VitaBite's
home city of Vienna):

- **`vienna` (Vienna):** Events hosted in Vienna, Austria (or the greater Vienna
  metropolitan area, including hybrid events with an in-person Vienna hub).
- **`europe` (Europe):** Events hosted anywhere in Europe (including Austria /
  Vienna, EU/EEA, UK, Switzerland, and broader European research hubs). Note:
  in the UI filter logic, selecting **Europe** displays both `europe` and
  `vienna` events (or records carry `primary_location: "vienna"` with
  `location_groups: ["vienna", "europe"]`), ensuring Vienna events appear under
  both **Vienna** and **Europe** as well as **All**.
- **`us` (US):** Events hosted in the United States.
- **`asia` (Asia):** Events hosted in Asia (e.g., Singapore, Japan, South Korea,
  China, Hong Kong, Taiwan, India, Israel, UAE/Middle East hubs).
- **`all` (All):** All collected events worldwide, including global/online-only
  events, rest-of-world locations (Canada, Australia, Latin America, Africa),
  and all four regional groups above.

Cross-cutting event attributes—such as **Conference**, **Symposium**,
**Workshop**, **Clinical Congress**, **Industry Expo**, **Hybrid**, or
**Online**—are represented as structured `tags`.

## Summary of intended outcome

- Collect global longevity, aging science, nutrition, and preventive-medicine
  event listings daily from an explicit, maintained allowlist of reliable
  feeds, search APIs, and scientific event calendars.
- Group each event into **`vienna`**, **`europe`**, **`us`**, **`asia`**, or
  global **`all`**, while tagging event format (`in_person`, `hybrid`,
  `online`) and event type (`conference`, `symposium`, `workshop`, `congress`,
  `summit`).
- Have a scheduled collector agent fetch, deduplicate, validate, and track
  collection results, and use the approved Antigravity agent workflow to
  summarize authorized event descriptions and verify dates, venues, and
  organizer details.
- Display source-linked event listings on an accessible `/events/` subpage
  linked from the VitaBite homepage and `/news/` navigation.
- Preserve organizer and publisher ownership: publish original event/source
  links, structured metadata (dates, city, country, organizer), and concise
  summaries—never scraped full web pages or unlicensed media.

**Required architecture gate:** Follow the same Antigravity architecture gate
established in [`longevity-news`](../longevity-news/01-architecture-and-source-policy.md).
Steps 1–2 and the public metadata roundup operate without Antigravity
credentials; Step 3's Antigravity summarizer uses the official Antigravity
Python SDK with tools disabled and requires a maintainer-provisioned API key
and permitted-content bundle before unattended execution is enabled.

## Completion

The project is ready for launch when the daily collector recovers gracefully
from source failures, each public event listing links to an approved source,
location filters (`All`, `Vienna`, `Europe`, `US`, `Asia`) work accessibly via
keyboard and screen readers, upcoming vs. past event handling is verified,
safety and schema checks pass, and operational/rollback procedures are
documented.

