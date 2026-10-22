# Website (Python version)

A small static site generator: content in `data/*.yaml`, page layouts in `templates/`, styles and files in `static/`.
`build.py` turns them into plain HTML in `_site/`.

## Setup (once)

```bash
pip install -r requirements.txt
```

## Preview locally

```bash
python build.py --serve
```

Then open http://localhost:8000. The site rebuilds when you save a file; refresh the browser to see the change.

## Editing content

| What                         | Where                       |
|------------------------------|-----------------------------|
| Bio, interests, background   | `data/profile.yaml`         |
| Publications                 | `data/publications.yaml`    |
| Workshops, talks, reviewing  | `data/activities.yaml`      |
| Teaching                     | `data/teaching.yaml`        |
| PDFs                         | `static/files/` (linked as `files/name.pdf`) |
| Colours, fonts, layout       | `static/css/style.css`      |

Each YAML file starts with a comment explaining its fields. To add a paper, copy an existing entry and edit it.

## Publishing

Every push to `main` builds and deploys the site to GitHub Pages (`.github/workflows/deploy.yaml`).
Progress is visible in the repository's **Actions** tab.

The previous Hugo version of the site is kept under the git tag `hugo-site` (`git checkout hugo-site` to look at it).
