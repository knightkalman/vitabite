# Step 4: Build the `/events/` subpage and link it from VitaBite

## Goal

Present collected longevity conferences and events in an accessible, responsive
`/events/` subpage linked from the VitaBite homepage and `/news/` page, with
interactive location group filtering for **All**, **Vienna**, **Europe**,
**US**, and **Asia**.

## Prerequisite

Complete [Step 2](./02-daily-collector-agent.md) (and
[Step 3](./03-antigravity-summaries-and-categorization.md) for offline
summarizer support). Like `/news/`, the public `/events/` page can display the
owner-authorized metadata roundup from `public/events/events.json` while clearly
labeling unreviewed candidate listings and supporting approved summaries when
present.

## Agent instructions

Implement `public/events/index.html`, `public/events/events.css`,
`public/events/events.js`, and `public/events/events.json` matching the visual
design, typography, editorial tone, and accessibility standards of
[`../../public/news/`](../../public/news/). Update the navigation bars in
[`../../public/index.html`](../../public/index.html) and
[`../../public/news/index.html`](../../public/news/index.html) so users can move
seamlessly between the main VitaBite site, **Longevity news**, and **Longevity
events**.

## Scope

- Create `public/events/index.html` and `public/events/events.css`:
  - Match the VitaBite aesthetic (`#f6f5ef` warm editorial palette, serif/sans
    hierarchy, skip link, semantic landmarks, responsive shell).
  - Include a hero section introducing the global longevity events directory
    (highlighting VitaBite's roots in Vienna alongside European, US, Asian, and
    worldwide gatherings).
  - Include an editorial status banner explaining that items from the latest
    background collection are source-linked event listings with provisional
    location groupings until editorially reviewed.
  - Provide a location filter bar (`role="group"` with `aria-label="Event location"`)
    containing semantic `<button type="button">` controls with `aria-pressed`:
    1. **All locations** (`data-location="all"`)
    2. **Vienna** (`data-location="vienna"`)
    3. **Europe** (`data-location="europe"`)
    4. **US** (`data-location="us"`)
    5. **Asia** (`data-location="asia"`)
  - Include a regional guide section explaining the five views (**Vienna**,
    **Europe**, **US**, **Asia**, and **All / Global**) similar to the four-way
    category guide on `/news/`.
- Implement `public/events/events.js`:
  - Fetch `./events.json` with `cache: "no-store"` and validate its schema
    version and structure.
  - Filter events by selected location group:
    - `"all"`: shows all valid events.
    - `"vienna"`: shows events where `primary_location === "vienna"` or
      `location_groups.includes("vienna")`.
    - `"europe"`: shows events where `primary_location === "europe"`,
      `primary_location === "vienna"`, or `location_groups.includes("europe")`
      (so Vienna events are included in Europe as well).
    - `"us"`: shows events where `primary_location === "us"` or
      `location_groups.includes("us")`.
    - `"asia"`: shows events where `primary_location === "asia"` or
      `location_groups.includes("asia")`.
  - Sort displayed events sensibly (upcoming events with known start dates in
    chronological order first, followed by recently published event
    announcements).
  - Render each event card with:
    - Location badge (e.g., `Provisional · Vienna · Europe` or `Europe · Zurich, Switzerland`)
    - Event date range (or publication date when event dates are TBA)
    - Attendance mode badge (`In-person`, `Hybrid`, `Online`) when known
    - Organizer / publisher name
    - Event title, review-state label, summary (or unreviewed metadata notice),
      event tags (`conference`, `symposium`, `workshop`, etc.), and an external
      `https:` link to the original event/publisher page (`rel="noopener noreferrer"`).
  - Update `#filter-status` (`aria-live="polite"`) whenever the location filter
    changes, and render clear empty states when a specific region (e.g.,
    Vienna) has no currently listed events in the feed.
  - Display collection freshness (`last_successful_collection`), partial-run
    status, and 3-day staleness notices identically to `news.js`.
- Link `/events/` across the site:
  - Add `<a href="./events/">Longevity events</a>` to the primary navigation and
    footer of `public/index.html`.
  - Add `<a href="../events/">Longevity events</a>` to `public/news/index.html`.
  - Ensure `public/events/index.html` links back to `../` (VitaBite home) and
    `../news/` (Longevity news).

## Acceptance criteria

- `/events/` renders cleanly locally (`python3 -m http.server 8000 --directory public`)
  and at the deployed GitHub Pages relative path.
- Clicking **All**, **Vienna**, **Europe**, **US**, and **Asia** filters the
  event list accurately, updates `aria-pressed` and `#filter-status`, and
  includes Vienna events inside the **Europe** filter as well as **Vienna** and
  **All**.
- Empty region states, stale feed notices, and error states are tested and
  accessible via keyboard and screen readers.
- Homepage, `/news/`, and `/events/` navigation links all resolve properly with
  relative paths.

## Handoff

Proceed to [Step 5](./05-operations-and-launch.md) to verify end-to-end
scheduled collection, past-event expiration, operational monitoring, and launch
readiness.

