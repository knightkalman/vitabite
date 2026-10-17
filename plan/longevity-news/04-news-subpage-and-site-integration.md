# Step 4: Build the news subpage and link it from VitaBite

> **Implementation status:** The static `/news/` preview page and homepage
> navigation link are implemented under `public/news/`. Per the owner's
> request, the public feed lists all 58 headlines from the latest successful
> collector run as unreviewed source metadata. Antigravity summarization and
> human editorial review remain unimplemented.

## Goal

Present approved longevity-news summaries in a useful, accessible subpage
linked from the existing VitaBite website and deploy it on GitHub Pages.

## Prerequisite

Complete [Step 3](./03-antigravity-summaries-and-categorization.md) for
summarized editorial content. The current owner-authorized metadata roundup
can display validated candidate headlines, but it must identify them as
unreviewed and must not imply that categories are confirmed or summaries exist.

## Agent instructions

Implement a responsive `/news/` page that matches the existing VitaBite
website's visual identity and works at the GitHub Pages project path. Integrate
it into the existing static-site artifact and Pages Actions workflow; do not
introduce a dependency on a server runtime for readers unless Step 1 explicitly
approved one.

## Scope

- Add an accessible news landing page at `/news/` with plain-language
  explanation of the feed, its update cadence, and a direct link back to the
  VitaBite home page.
- Add a visible **Longevity news** link in the main website navigation so
  readers can reach the subpage.
- Render titles, source/publisher, publication date, collection/update date
  where useful, provisional category and tags, and a clear link to the
  original article. Show summaries and evidence notes only when they exist and
  are editorially approved.
- Provide category filters for scientific research, consumer goods,
  nutrients, and medication. Filters must remain understandable and usable
  without a mouse; use semantic controls and update accessible status where
  results change.
- Display the feed's last successful collection time, stale-data state, empty
  state, and source/run failure state without implying no news was published
  if collection failed.
- If an archive or pagination is added, bound the amount of data loaded and
  preserve direct links. Avoid invasive tracking and external embeds.
- Label medical material as news, not medical advice. Avoid instructing users
  to take medication, supplements, or change treatment.
- Ensure the existing deployment workflow includes page assets and the
  owner-authorized metadata-only roundup, while never exposing private keys,
  API credentials, intermediate source dumps, or generated unreviewed
  summaries.

## Acceptance criteria

- The `/news/` page works locally and at the deployed project Pages path.
- The homepage links to the news page, and the news page links back.
- Category filters, article links, empty/error/stale states, and responsive
  layouts are tested.
- Keyboard navigation, semantic landmarks/headings, contrast, and screen-reader
  labels follow the existing site's accessibility conventions.
- Metadata-only candidates are visibly identified as unreviewed; original
  sources remain clearly attributed and linked. Future summaries require
  approved records.
- Existing homepage content, assets, and GitHub Pages deployment continue to
  work.

## Handoff

Before adding summaries, implement a controlled review and publication process
for generated content. The metadata-only roundup refreshes from each
successful/partial scheduled collector run; generated summaries remain outside
this auto-publication flow. Proceed to
[Step 5](./05-operations-and-launch.md) after the publication policy and Pages
deployment are verified end to end.
