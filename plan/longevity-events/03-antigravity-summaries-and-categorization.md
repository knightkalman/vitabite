# Step 3: Summarize and categorize events with Antigravity

## Goal

Use the approved Antigravity Python SDK integration to turn collected event
candidates and authorized event descriptions into concise, source-grounded
event summaries with verified dates, city/country details, attendance mode, and
confirmed location groupings (`vienna`, `europe`, `us`, `asia`, `other`).

## Prerequisite

Complete [Step 2](./02-daily-collector-agent.md) and adhere to Step 1's
Antigravity unattended-integration gate and permitted-content requirements.

## Agent instructions

Implement `events/summarizer.py` by adapting `news/summarizer.py`. Configure the
Antigravity agent with all tools disabled (`tools=[]`), strict structured-output
schema enforcement (`events/schemas/summarized-event.schema.json`), and
numbered source-paragraph citations. Never infer event dates, venues, speakers,
or registration details from a headline alone; require an operator-authorized
content bundle (`events/schemas/permitted-content.schema.json`) before invoking
the model.

## Scope

- Accept candidate event records (`--candidates`) and a private,
  schema-validated permitted-content bundle (`--content`) where each item has
  `processing_authorized: true`, an `authorization_basis`
  (`licensed_excerpt`, `public_domain`, or `publisher_permission`), matching
  `item_id` and `source_url`, and up to 30,000 characters of event description
  text.
- Require schema-constrained output (`events/schemas/summarized-event.schema.json`)
  containing:
  - Cleaned event title and verified organizer
  - Confirmed `primary_location` (`vienna`, `europe`, `us`, `asia`, `other`)
    and `location_groups` (`["vienna", "europe"]` when in Vienna)
  - Verified `city`, `country`, and `attendance_mode` (`in_person`, `hybrid`,
    `online`, `unspecified`)
  - Verified `event_start_date`, `event_end_date`, or `event_date_raw`
  - Controlled `tags` (`conference`, `symposium`, `congress`, `workshop`,
    `summit`, `nutrition`, `geroscience`, `clinical_trial`, `biomarkers`, etc.)
  - Concise, neutral 2–3 sentence `summary` of the event's focus and target
    audience
  - Paragraph-grounded `key_points` (e.g., key themes, abstract deadlines,
    venue info) citing exact source paragraph numbers
  - `event_notes` (e.g., whether the event is peer-reviewed scientific vs.
    commercial/sponsor-led)
  - `confidence` (`high`, `medium`, `low`) and `review_state` (`approved`,
    `needs_review`, `withheld`).
- Enforce safety and quality rules:
  - Treat commercial longevity retreats, product expos, or sponsor pitches
    descriptively and flag promotional claims for `needs_review`.
  - Never present conference topics or speaker claims as clinical advice or
    endorsed treatments.
  - Route low-confidence items, missing/conflicting location or date data, and
    medical/therapeutic intervention workshops to `needs_review`.
- Write private audit records (`--audit`) containing SHA-256 hashes of prompts
  and source text rather than raw text.
- Add unit tests in `tests/test_events_summarizer.py` covering all location
  groups (`vienna`, `europe`, `us`, `asia`, `other`), promotional event
  handling, missing-permission rejection, and paragraph citation checks.

## Acceptance criteria

- `events/summarizer.py` validates inputs and outputs strictly against the
  versioned schemas in `events/schemas/`.
- Candidates without authorized text remain `needs_review` and are never
  summarized from titles alone.
- Vienna events confirmed by the summarizer automatically include both
  `"vienna"` and `"europe"` in `location_groups`.
- Unit tests pass without requiring a live API key in CI, while supporting
  authenticated runs via `ANTIGRAVITY_API_KEY`.

## Handoff

Proceed to [Step 4](./04-events-subpage-and-site-integration.md) to build the
public `/events/` subpage and connect it to the VitaBite site.

