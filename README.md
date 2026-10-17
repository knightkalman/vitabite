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

## Publish with GitLab Pages

The `.gitlab-ci.yml` pipeline publishes `public/` to GitLab Pages when a commit
lands on the project's default branch. Enable GitLab Pages for the project if
it is not already enabled. The site uses relative asset links, so it works at
both a project Pages path and a custom domain.

## Project brief

See [`docu/vitabite_prezi.pdf`](docu/vitabite_prezi.pdf) for the source project
overview and [`plan/`](plan/) for the staged implementation plan.
