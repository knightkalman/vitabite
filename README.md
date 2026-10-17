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
tags. It does **not** fetch article text or create summaries. Results remain
candidates; they are not included in the website or published as news.

GitHub Actions runs this collector daily at 05:17 UTC and supports authorized
manual dispatch. Candidate state is stored in a repository Actions artifact,
not in the Pages artifact. Food Business News has a candidate feed configured
but remains disabled until a maintainer can verify its terms. The collector
needs no API keys. Antigravity summarization is not part of Steps 1–2 and
remains disabled pending a separately configured and tested provider
credential.

## Longevity news preview

The [`/news/` subpage](public/news/index.html) is linked from the VitaBite
homepage and is included in the GitHub Pages deployment. Its public feed in
[`public/news/news.json`](public/news/news.json) currently contains no
approved articles. This is intentional: collector candidates remain in a
private-to-the-repository Actions artifact and are not published. Antigravity
summaries, editorial review, and an approved-feed publication step must be
implemented before real news appears on the public page.

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
