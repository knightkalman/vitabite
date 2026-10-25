# Step 5: Harden operations and launch the daily events service

## Goal

Verify the end-to-end daily events collection and publication workflow,
establish lifecycle rules for past/expired events, document operator runbooks,
and launch `/events/` on GitHub Pages with a safe rollback path.

## Prerequisite

Complete [Step 4](./04-events-subpage-and-site-integration.md). Review the
collector (`events/collector.py`), metadata publisher
(`events/publish_metadata.py`), Antigravity summarizer (`events/summarizer.py`),
GitHub Actions workflow (`.github/workflows/longevity-events-collect.yml`), and
public UI (`public/events/`) before enabling or relying on the production
schedule.

## Agent instructions

Run an end-to-end readiness review and implement automated tests covering the
full pipeline from feed collection and location grouping to `public/events/events.json`
generation and static-site integrity.

## Scope

- Exercise the complete flow:
  - Scheduled/manual collection via `events/collector.py`
  - Candidate state persistence and deduplication across runs
  - Public metadata feed generation via `events/publish_metadata.py`
  - Offline Antigravity summarization via `events/summarizer.py` with mock/test
    content bundles
  - Static site rendering and filter behavior on `public/events/`.
- Test failure and edge modes:
  - Malformed RSS/Atom XML or NCBI E-utilities JSON responses
  - Redirects to untrusted domains or non-HTTPS event links
  - Ambiguous city/country names (e.g., Vienna, Virginia in `us` vs. Vienna,
    Austria in `vienna`/`europe`; Georgia the country vs. Georgia, US)
  - Past-event pruning and retention boundaries so finished conferences do not
    clutter upcoming listings indefinitely
  - Total collection failure preserving the last known-good
    `public/events/events.json` without deploying a broken or empty feed.
- Verify GitHub Actions workflow security and concurrency:
  - Ensure `.github/workflows/longevity-events-collect.yml` uses least-privilege
    permissions (`contents: read`, `pages: write`, `id-token: write`),
    serialized concurrency compatible with `pages.yml` and
    `longevity-news-collect.yml` (so concurrent Pages deployments do not clash),
    and emits no titles or secrets in workflow logs.
- Update repository documentation (`README.md` and `events/policy.md`):
  - Document CLI commands for running the events collector, publishing metadata,
    and invoking the private Antigravity summarizer.
  - Document how to add/disable event sources, override a misclassified
    location group, withdraw an event listing, or roll back `public/events/events.json`.

## Acceptance criteria

- All unit and integration tests for both `news` and `events` pass via
  `pytest` / `unittest`.
- Ambiguous geographic cases (such as Vienna, VA vs. Vienna, Austria) are
  covered by regression tests.
- Workflow concurrency groups prevent deployment races between `pages.yml`,
  `longevity-news-collect.yml`, and `longevity-events-collect.yml`.
- Operator documentation in `README.md` and `events/policy.md` covers manual
  runs, source reviews, takedowns, and rollback.

## Completion

This completes the `longevity-events` execution plan. Future enhancements—such
as downloadable `.ics` calendar exports, user-submitted event moderation forms,
or interactive map views—can be evaluated in separate follow-up plans once the
daily static directory is live.

