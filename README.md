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
Antigravity summaries and editorial review remain future work.

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
