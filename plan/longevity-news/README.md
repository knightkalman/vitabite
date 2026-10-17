# Longevity news project

## Project summary

Build a trustworthy, daily-updated longevity news service as a subpage of the
VitaBite website. A scheduled collector agent gathers items from approved
science, nutrition, food, and medicine sources. Antigravity summarizes and
tags each item using its content, with article links and source details kept
alongside the summaries. Readers browse the resulting feed at
`/news/` on the existing GitHub Pages site.

The five implementation steps below are sequential and intended to be handed
to coding agents one at a time. Each step defines its prerequisite, task,
acceptance criteria, and handoff.

## Current implementation status

- Steps 1–2 are implemented in the repository. The collector has been run
  locally against the two enabled sources and produced metadata-only
  candidates in the verification run. A candidate food-industry feed is
  configured but disabled pending review of its inaccessible terms page.
- GitHub Actions is configured to collect daily at 05:17 UTC, retain a rolling
  candidate-state artifact, update the public metadata roundup, and deploy the
  site from the same background run. The schedule is active on the default
  branch.
- A `/news/` preview is implemented and linked from the VitaBite homepage. It
  publishes all headlines from the latest successful collector run as an
  explicitly unreviewed metadata roundup. No summaries are generated, and
  future successful collector runs update the metadata roundup automatically.
- Antigravity's official unattended/programmatic route and structured-output
  SDK are documented. Step 3's local summarizer, strict output schema,
  authorization-gated input bundle, and safety tests are implemented, but no
  API secret is configured and the SDK has not been authenticated or tested
  in GitHub Actions.
- The current collector supplies metadata only. Without separately supplied
  article text with an authorized processing basis, candidates remain
  `needs_review` and are never summarized from headlines.
- Generated summaries are private and do not update the public metadata
  roundup. Step 4 still needs to integrate and validate an editorially approved
  feed; the scheduled collector continues to update the headline roundup.

## Plan files

1. [Architecture, sources, and Antigravity integration](./01-architecture-and-source-policy.md)
2. [Daily collector agent](./02-daily-collector-agent.md)
3. [Antigravity summaries and categorization](./03-antigravity-summaries-and-categorization.md)
4. [News subpage and main-site integration](./04-news-subpage-and-site-integration.md)
5. [Operations, safeguards, and launch](./05-operations-and-launch.md)

## Summary of intended outcome

- Collect longevity-related news every day from an explicit, maintained
  allowlist of reliable feeds and sources.
- Categorize each item by content. The initial primary categories are
  **Scientific research**, **Consumer goods**, **Nutrients**, and
  **Medication**; cross-cutting topics such as study type or population are
  represented as tags.
- Have a scheduled collector agent fetch, deduplicate, validate, and track
  collection results, and use an approved Antigravity agent workflow to
  summarize accessible articles and assign evidence-linked tags.
- Display reviewed, source-linked summaries on an accessible `/news/` subpage
  linked from the VitaBite website.
- Preserve article ownership: publish original links and short summaries, not
  full article text or unlicensed images. Clearly distinguish study findings
  from interpretation, hypotheses, and promotional claims.
- Avoid presenting medical news as personal medical advice, treatment
  recommendations, or established clinical guidance.

**Required architecture gate:** Antigravity must have a documented, permitted
way to run without a developer interactively operating a desktop session if it
is to perform a daily unattended job. Verify this in Step 1 before building
around it. Do not invent an API, automate a user interface as a substitute, or
store personal access credentials in the repository. If an approved unattended
integration is unavailable, pause and get the project owner's decision on an
alternative before proceeding with Steps 2–3.

## Completion

The project is ready for launch when the daily agent can recover from ordinary
source failures, each public summary is traceable to an approved source, the
news page accurately shows current data and collection freshness, safety and
quality checks pass, and deployment/rollback/ownership are documented.
