# Step 4: Build the news subpage and link it from VitaBite

> **Implementation status:** The static `/news/` preview page and homepage
> navigation link are implemented under `public/news/`. The public feed
> contains no approved articles yet: the collector stores candidates in
> workflow artifacts, while Antigravity summarization and editorial approval
> remain unimplemented.

## Goal

Present approved longevity-news summaries in a useful, accessible subpage
linked from the existing VitaBite website and deploy it on GitHub Pages.

## Prerequisite

Complete [Step 3](./03-antigravity-summaries-and-categorization.md). Use
approved, validated records and the data-publication architecture defined in
Step 1. Do not display candidate or rejected items.

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
  where useful, category, tags, concise summary, evidence caveat, and a clear
  link to the original article.
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
- Ensure the existing deployment workflow includes page assets and published
  news data, while never exposing private keys, API credentials, intermediate
  source dumps, or unapproved content.

## Acceptance criteria

- The `/news/` page works locally and at the deployed project Pages path.
- The homepage links to the news page, and the news page links back.
- Category filters, article links, empty/error/stale states, and responsive
  layouts are tested.
- Keyboard navigation, semantic landmarks/headings, contrast, and screen-reader
  labels follow the existing site's accessibility conventions.
- Only approved records render; original sources remain clearly attributed and
  linked.
- Existing homepage content, assets, and GitHub Pages deployment continue to
  work.

## Handoff

Before calling this step fully complete, implement a controlled process to
transfer reviewed and approved summaries into `public/news/news.json`. Keep
collector candidates private and keep all non-approved items out of the Pages
artifact. Proceed to [Step 5](./05-operations-and-launch.md) after that
publication flow and the Pages deployment are verified end to end.
