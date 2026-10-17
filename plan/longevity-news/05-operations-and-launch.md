# Step 5: Harden operations and launch the daily news service

## Goal

Verify the complete daily-to-publication workflow, establish editorial and
operational ownership, and launch with a safe rollback path.

## Prerequisite

Complete [Step 4](./04-news-subpage-and-site-integration.md). Review the real
collector, Antigravity integration, data publishing, and public UI before
enabling the production schedule.

## Agent instructions

Run an end-to-end readiness review and implement concrete reliability,
monitoring, privacy, and documentation gaps. Do not enable an unattended
production schedule until the approved source policy, Antigravity integration,
secrets, and publication safeguards are configured and tested.

## Scope

- Exercise the complete flow from scheduled collection to Antigravity
  categorization, validation/review, site data publication, and successful
  GitHub Pages deployment.
- Test retries, duplicate runs, interrupted execution, bad schema output,
  unavailable Antigravity, malformed or stale feeds, rate limits, rejected
  content, and Pages deployment failure.
- Add alerts or equivalent actionable operator notifications for failed,
  partial, stale, or unexpectedly empty runs. Identify an accountable operator
  and documented response path.
- Review least-privilege workflow permissions, protected secrets, logs,
  dependency updates, source terms, data minimization, and concurrent-run
  behavior.
- Define quality checks for summary grounding, attribution, classification,
  category balance, medicine-related safeguards, freshness, and correction or
  takedown requests.
- Document normal operation, reruns, source additions/removals, editorial
  overrides, incident handling, generated-data restoration, and deployment
  rollback.
- Start the daily schedule only after an explicitly reviewed readiness
  checklist. Mark initial launch status and show when the service began
  running; do not imply a historical archive exists before it does.

## Acceptance criteria

- A full scheduled test run publishes only validated, authorized records and
  deploys the working `/news/` page on GitHub Pages.
- Failed or partial collection and summarization are observable and do not
  silently publish misleading success or erase previously published items.
- Credentials are least-privilege and never present in static assets, commits,
  generated public data, prompts, or logs.
- Operators can identify stale data, pause the collector, remove/correct
  public records, and restore the last known-good publication.
- A human owner, source-review process, escalation path, and rollback steps
  are documented.
- All relevant automated checks pass and known external approvals or
  integration limitations are listed before launch.

## Completion

This completes the initial longevity-news project plan. Expansion to
additional sources, languages, personalization, or medical decision support
requires a separate review; medical advice or individualized treatment
recommendations are outside this news service's scope.
