"""MkDocs hooks for the bilingual site.

- Notebook pages have no front matter. Per-page meta descriptions come from
  `extra.descriptions` (keyed by source file name) and are injected early,
  so that social-cards plugin can pick them up.
- The "view source" button must point at the file as committed.
  Pages in docs/ and docs-en/ are partly symlinks into notebooks/. CI replaces
  those symlinks with rendered copies before building, so the answer comes from
  the git index, not from the working tree.
"""

import functools
import os
import subprocess

from mkdocs.plugins import event_priority


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
