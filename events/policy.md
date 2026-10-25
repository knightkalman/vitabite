# Longevity-events collection policy

## Architecture and publication boundary

The VitaBite website remains a static GitHub Pages site. A GitHub Actions
workflow runs the longevity-events collector daily in **UTC** and on authorized
manual dispatches. Collector runs store source-linked candidate event metadata
in a private-to-the-repository Actions artifact, separate from the website. The
artifact is retained for 90 days; candidate records themselves expire after
90 days.

**Publication mode:** matching the owner-authorized publication mode of
[`longevity-news`](../news/policy.md), all items from the latest successful
collector run are published to the static `/events/` subpage
(`public/events/events.json`) and refreshed by the background collector. The
static events page publishes the collected event title, organizer/publisher,
source link, publication/announcement date metadata, provisional location
groupings (`vienna`, `europe`, `us`, `asia`, `other`), and event-type tags as an
explicitly **unreviewed metadata roundup**. It does not publish full web page
bodies, generated summaries, or claims of editorial/clinical review. Each
successful or partially successful scheduled run updates the static feed and
deploys Pages in that same workflow. A total collection failure preserves the
previous public feed.

## Antigravity integration decision

**Decision: GO for a separately configured Antigravity summarization step
(`events/summarizer.py`); no Antigravity invocation occurs in Steps 1–2.**

As documented in [`news/policy.md`](../news/policy.md), official Google
documentation provides two programmatic routes:

- The [Antigravity managed agent API](https://ai.google.dev/gemini-api/docs/antigravity-agent)
  via the Interactions API (`GEMINI_API_KEY`).
- The [Antigravity Python SDK](https://antigravity.google/docs/sdk/overview)
  with [structured-output validation](https://antigravity.google/docs/sdk/structured-output).

Step 3 pins the official Antigravity Python SDK (`events/summarizer.py`) with
all agent tools disabled and strict JSON schema validation. Unattended
summarization remains disabled in CI until a maintainer provisions an API
secret and supplies an operator-authorized source-text bundle.

## Location taxonomy (`Vienna`, `Europe`, `US`, `Asia`, `All`)

Each record receives a primary rule-based **candidate** `location` and a
normalized list of `location_groups` for UI filtering:

| Location key | Filter label | Use when the event or announcement is located in | Examples |
| --- | --- | --- | --- |
| `vienna` | **Vienna** | Vienna, Austria (`Vienna`, `Wien`, Hofburg, Medical University of Vienna, Austria Center Vienna). Note: Vienna events automatically include both `"vienna"` and `"europe"` in `location_groups`. | Vienna Congress; EASD Annual Meeting in Vienna; Hofburg Vienna symposium. |
| `europe` | **Europe** | Any European city, country, or pan-European scientific society congress (including Vienna/Austria, Germany, Switzerland, UK, France, Netherlands, Nordic countries, Spain, Italy, etc.). | EuGMS Congress Reykjavik; ARDD Meeting Copenhagen; EMAS European framework. |
| `us` | **US** | Any United States city, state, or US national institute/society conference (e.g., NIA workshops, Boston, San Francisco, San Diego, New York, Bethesda, Midwest Aging Consortium). | National Institute on Aging Workshop; Midwest Aging Consortium Symposium. |
| `asia` | **Asia** | Any Asian city, country, or pan-Asian congress (e.g., Singapore, Tokyo/Japan, Seoul/Korea, Shanghai/Beijing/China, Hong Kong, Taiwan, India, Bangkok/Thailand, Middle East hubs). | TimePie Longevity Forum Shanghai; APSCVIR Bangkok; KSIR Busan. |
| `other` | **All locations** | Global, virtual/online-only, or rest-of-world events (Canada, Australia, Latin America, Africa) where a specific `vienna`/`europe`/`us`/`asia` region is not primary. | International multidisciplinary gerontological symposium; global consensus workshop. |

Rule precedence for `location` is `vienna`, `europe`, `us`, `asia`, then
`other`. If an event title explicitly mentions multiple regional hubs (for
example, a multi-congress presentation in Vienna, Korea, and Thailand), all
matched regions are included in `location_groups` while `location` reflects the
highest-precedence match. Disambiguation rules prevent false positives such as
"Vienna, Virginia" or "Vienna, VA" matching `vienna`/`europe` (routing them to
`us` instead).

## Source allowlist and terms

The versioned registry is [`sources.json`](./sources.json) and conforms to
[`schemas/source-registry.schema.json`](./schemas/source-registry.schema.json).
It uses the exact same search engines, feed types, and collection methods as
`news/sources.json`:

1. **Nature Aging public RSS (`nature_aging_events`):** Springer Nature public
   RSS1 feed filtered by conference, symposium, congress, forum, workshop, and
   meeting keywords. Retains metadata and canonical `nature.com` links only.
2. **PubMed Global Longevity Events via NCBI E-utilities (`pubmed_events_global`):**
   ESearch + ESummary search for longevity, healthy aging, geroscience, and
   gerontology conferences, symposia, congresses, workshops, summits, and forums.
3. **PubMed Regional Longevity & Medical Events (`pubmed_events_vienna`,
   `pubmed_events_europe`, `pubmed_events_us`, `pubmed_events_asia`):**
   Targeted NCBI E-utilities queries surfacing peer-reviewed congress reports,
   symposium proceedings, abstract volumes, and workshops in Vienna, Europe,
   the US, and Asia.
4. **Food Business News Events RSS (`food_business_events`, disabled):**
   Configured for industry expos and summits, kept `enabled: false` until terms
   can be verified by a maintainer.

## Dedupe, retention, freshness, corrections, and takedowns

- Canonicalize HTTPS URLs, strip tracking parameters and fragments, and
  deduplicate by canonical URL SHA-256 (`item_id`).
- When an item appears in multiple queries (e.g., both global and regional
  PubMed searches), merge `location_groups` and `tags` idempotently while
  preserving the highest-precedence primary `location`.
- Retain candidate metadata for 90 days in collector state; workflow artifacts
  expire after 90 days.
- The public `/events/` page displays the timestamp of the last successful
  collection and flags the feed as stale after three days.
