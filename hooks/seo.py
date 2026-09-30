"""MkDocs hooks for the bilingual site.

- Notebook pages have no front matter. Per-page meta descriptions come from
  `extra.descriptions` (keyed by source file name) and are injected early,
  so that social-cards plugin can pick them up.
- The "view source" button must point at the file as committed.
  Pages in docs/ and docs-en/ are partly symlinks into notebooks/. CI replaces
  those symlinks with rendered copies before building, so the answer comes from
  the git index, not from the working tree.
- Post-render cleanup: drop Material's relative hreflang links (hreflang pairs
  live in overrides/sitemap.xml), name the search dialog for screen readers,
  and skip the MathJax loader on notebooks without math. 404.html gets the same
  cleanup via on_post_template.
"""

import functools
import json
import logging
import os
import re
import subprocess

from mkdocs.plugins import event_priority

# Material emits
# <link rel="alternate" href="/" hreflang="pl">
# for extra.alternate: relative, and the same on every page, so wrong for hreflang.
MATERIAL_HREFLANG = re.compile(
    r'\s*<link rel="alternate" href="[^"]*" hreflang="[^"]*">'
)
MATHJAX_BLOCK = re.compile(
    r"<!-- Load mathjax -->.*?<!-- End of mathjax configuration -->", re.S
)
# what the stripped MathJax config would typeset: $..$, $$, \(..\), \[..\], \begin{..}
MATH = re.compile(r"\$[^$\n]+\$|\$\$|\\\(|\\\[|\\begin\{")
log = logging.getLogger("mkdocs.hooks.seo")  # warnings fail `mkdocs build --strict`
SEARCH_LABEL = {"pl": "Szukaj", "en": "Search"}


@functools.lru_cache(maxsize=None)
def _repo_path(repo_root, rel):
    """Repo-relative path of the committed file behind `rel` (follows one symlink)."""
    try:
        entry = subprocess.run(
            ["git", "ls-files", "-s", "--", rel],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return rel
    if entry and entry[0] == "120000":
        target = subprocess.run(
            ["git", "cat-file", "blob", f":{rel}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return os.path.normpath(os.path.join(os.path.dirname(rel), target))
    return rel


def _has_math(ipynb_path):
    nb = json.loads(open(ipynb_path, encoding="utf-8").read())
    return any(
        MATH.search("".join(c["source"]))
        for c in nb["cells"]
        if c["cell_type"] == "markdown"
    )


@event_priority(100)  # before the social plugin's on_page_markdown
def on_page_markdown(markdown, page, config, files):
    desc = (config.extra.get("descriptions") or {}).get(page.file.src_path)
    if desc and not page.meta.get("description"):
        page.meta["description"] = desc
    return markdown


def on_page_context(context, page, config, nav):
    repo_root = os.path.dirname(os.path.abspath(config.config_file_path))
    rel = os.path.relpath(os.path.join(config.docs_dir, page.file.src_path), repo_root)
    page.edit_url = (
        f"{config.repo_url.rstrip('/')}/blob/master/{_repo_path(repo_root, rel)}"
    )
    return context


def _clean(output, config, where):
    output = MATERIAL_HREFLANG.sub("", output)
    label = SEARCH_LABEL.get(config.theme["language"], "Search")
    output = output.replace(
        'data-md-component="search" role="dialog"',
        f'data-md-component="search" role="dialog" aria-label="{label}"',
    )
    head = output.split("</head>", 1)[0]
    if "hreflang=" in head or 'role="dialog">' in output:  # Material markup changed
        log.warning(f"{where}: Material markup changed, update hooks/seo.py patterns")
    return output


def on_post_page(output, page, config):
    output = _clean(output, config, page.file.src_path)
    if page.file.src_path.endswith(".ipynb") and not _has_math(page.file.abs_src_path):
        output = MATHJAX_BLOCK.sub("", output)
    return output


def on_post_template(output_content, template_name, config):
    # 404.html is a theme template, rendered without on_post_page
    if template_name == "404.html":
        return _clean(output_content, config, template_name)
    return output_content
