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
