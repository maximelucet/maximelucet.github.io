#!/usr/bin/env python3
"""Build the website into _site/.

    python build.py            build once
    python build.py --serve    build, serve on http://localhost:8000 and rebuild on changes
"""
import argparse
import datetime
import functools
import http.server
import shutil
import threading
import time
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, pass_context, select_autoescape
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
WATCHED = [ROOT / "data", ROOT / "templates", ROOT / "static"]

# (template, output file, menu label). The output paths keep the old site's URLs.
PAGES = [
    ("home.html", "index.html", "About"),
    ("publications.html", "research/index.html", "Publications"),
    ("activities.html", "projects/index.html", "Research activities"),
    ("teaching.html", "cv/index.html", "Teaching"),
]


def load_data():
    return {f.stem: yaml.safe_load(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "data").glob("*.yaml"))}


@pass_context
def url(ctx, path):
    """Make a site path (e.g. 'files/x.pdf') relative to the current page, so the site works under any base URL."""
    if path.startswith(("http://", "https://", "mailto:", "#")):
        return path
    return (ctx["root"] + path) or "./"


@pass_context
def authors(ctx, names):
    """Join author names, highlighting the site owner."""
    me = ctx["profile"]["name"]
    return Markup(", ").join(Markup("<strong>%s</strong>") % n if n == me else escape(n) for n in names)


def build():
    data = load_data()
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(), trim_blocks=True, lstrip_blocks=True)
    env.filters.update(url=url, authors=authors)
    nav = [{"label": label, "path": out.removesuffix("index.html")} for _, out, label in PAGES]

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    for template, out, label in PAGES:
        target = OUT / out
        target.parent.mkdir(parents=True, exist_ok=True)
        html = env.get_template(template).render(
            **data,
            nav=nav,
            current=out.removesuffix("index.html"),
            title=None if out == "index.html" else label,
            root="../" * out.count("/"),
            year=datetime.date.today().year,
        )
        target.write_text(html, encoding="utf-8")
    print(f"Built {len(PAGES)} pages into {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT}")


def snapshot():
    return {p: p.stat().st_mtime for d in WATCHED for p in d.rglob("*") if p.is_file()}


def watch():
    last = snapshot()
    while True:
        time.sleep(1)
        now = snapshot()
        if now != last:
            last = now
            try:
                build()
            except Exception as e:  # keep serving on template or YAML errors
                print(f"Build failed: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="serve the site locally and rebuild on changes")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    build()
    if args.serve:
        threading.Thread(target=watch, daemon=True).start()
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print(f"Serving on http://localhost:{args.port} (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("", args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
