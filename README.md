# VitaBite AI

VitaBite AI is a project exploring how nutrition science, food, and AI can
support more personalized food choices. The current deliverable is a static
project website; product features described there are concepts and planned
work, not available services.

## Run locally

From the repository root, serve the static site with Python:

```sh
python3 -m http.server 8000 --directory public
```

Then open <http://localhost:8000>.

## Longevity-news collector

The approved sources and collection policy are in [`news/`](news/). To run
the metadata-only collector manually:

```sh
python3 -m news.collector --state /tmp/vitabite-news-candidates.json --run-id local
```

The collector reads the Nature Aging public RSS feed and PubMed's public
E-utilities, producing schema-validated candidates with title, publisher,
source link, publication metadata, a provisional rule-based category, and
tags. It does **not** fetch article text or create summaries.

GitHub Actions runs this collector daily at 05:17 UTC and supports authorized
manual dispatch. It keeps full candidate state in an Actions artifact,
publishes only source-linked metadata from a successful run into the static
roundup, and deploys the refreshed site. Total collection failure leaves the
last published feed unchanged. Food Business News remains disabled until a
maintainer can verify its terms. The collector needs no API keys. Antigravity
summarization remains a separate future step.

## Longevity news

The [`/news/` subpage](public/news/index.html) is linked from the VitaBite
homepage and is included in the GitHub Pages deployment. The current public
feed in [`public/news/news.json`](public/news/news.json) contains all 58
source-linked headlines from the latest successful collection. They are
explicitly labeled as unreviewed metadata candidates: categories and tags are
provisional, and no article summaries are generated. Future successful
background collection runs update this headline-only roundup automatically.

### Antigravity summaries

The Step 3 summarizer is a separate manual operation. It processes only
article text supplied in a private bundle with explicit processing
authorization and a matching source URL. Current candidates contain metadata
only, so without that bundle they remain `needs_review` and receive no
headline-derived summary. Do not fetch or send article text to Google unless
the source's terms or explicit permission allow that processing.

Install `requirements-news.txt` and create a private JSON input bundle
conforming to [`permitted-content.schema.json`](news/schemas/permitted-content.schema.json).
Each entry needs `processing_authorized: true`, an `authorization_basis`
(`licensed_excerpt`, `public_domain`, or `publisher_permission`), and the
exact candidate `item_id` and `source_url`, plus text of at most 30,000
characters. Keep this bundle outside Git. Then run:

```sh
ANTIGRAVITY_API_KEY=... python3 -m news.summarizer \
  --candidates /path/to/candidates.json \
  --content /private/path/permitted-content.json \
  --output /private/path/summaries.json \
  --audit /private/path/summarizer-audit.jsonl \
  --run-id local
```

The Antigravity SDK is configured with agent tools disabled. Output is
validated against the versioned summary schema and key points cite numbered
source paragraphs; audit records retain hashes and decisions, not the source
text. Medication, low-confidence, preliminary, promotional, conflicting, and
other flagged items require human review. Summary output remains private and
does not update or publish `/news/`. The SDK path has not yet been
authenticated or verified in GitHub Actions, so unattended summarization is
not enabled.

## Longevity-events collector and `/events/` directory

The approved event sources and collection policy are in [`events/`](events/).
To run the metadata-only events collector and update the static `/events/`
feed manually:

```sh
python3 -m events.collector --state /tmp/vitabite-events-candidates.json --run-id local
python3 -m events.publish_metadata --state /tmp/vitabite-events-candidates.json --output public/events/events.json
```

The [`/events/` subpage](public/events/index.html) is linked from the VitaBite
homepage and `/news/`, and groups collected conferences, symposia, workshops,
and congresses into **All**, **Vienna**, **Europe** (including Vienna),
**US**, and **Asia**. GitHub Actions runs
[`.github/workflows/longevity-events-collect.yml`](.github/workflows/longevity-events-collect.yml)
daily at 05:47 UTC and on manual dispatch, updating `public/events/events.json`
and deploying GitHub Pages. Private Antigravity summarization for authorized
event descriptions is implemented in [`events/summarizer.py`](events/summarizer.py).

## Publish with GitHub Pages

The [GitHub Actions workflow](.github/workflows/pages.yml) publishes `public/`
to GitHub Pages when a commit lands on `main`, or when manually triggered.
In the repository, go to **Settings → Pages → Build and deployment** and set
**Source** to **GitHub Actions**. The workflow uses relative asset links so
the site works at the repository's project Pages path.

After the first successful deployment, GitHub displays the published URL under
**Settings → Pages**.

## Project brief

See [`docu/vitabite_prezi.pdf`](docu/vitabite_prezi.pdf) for the source project
overview and [`plan/`](plan/) for the staged implementation plan.
