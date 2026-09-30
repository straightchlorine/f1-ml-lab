#!/usr/bin/env python3
"""Keep cross-notebook GitHub links pointing at the right lines.

Links in markdown cells look like

    [notebooka 01](https://github.com/straightchlorine/f1-ml-lab/blob/master/notebooks/01-build-dataset.ipynb?plain=1&cell=6f1c2a9e#L120-L134)

`cell=` names the target cell by its nbformat id; the `#L..` range is derived
from it: the lines of that cell's "source" array in the target file as stored.

Editing a notebook shifts lines, so re-run this afterwards (CI runs --check).

    python scripts/link_refs.py          # rewrite stale ranges in place
    python scripts/link_refs.py --check  # exit 1 if any range is stale, 2 if a link is broken
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://github.com/straightchlorine/f1-ml-lab/blob/master/"
LINK = re.compile(
    re.escape(BASE)
    + r"(?P<path>[\w./-]+\.ipynb)\?plain=1&cell=(?P<id>[\w-]+)(?:#L\d+(?:-L\d+)?)?"
)
FILES = [
    "docs/00-data-load.ipynb",
    *sorted(
        p.relative_to(ROOT).as_posix() for p in (ROOT / "notebooks").glob("0*.ipynb")
    ),
    *sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "docs-en").glob("0*.ipynb")
        if not p.is_symlink()
    ),
]
KEY = "   "  # cell keys sit at depth 3 with Jupyter's indent=1 serialization


def dump(nb):
    return json.dumps(nb, ensure_ascii=False, indent=1) + "\n"


def source_lines(path, cell_id, cache):
    """1-based (first, last) line of the cell's "source" entries in the stored file."""
    if path not in cache:
        cache[path] = (ROOT / path).read_text().splitlines()
    lines = cache[path]
    hits = [i for i, l in enumerate(lines) if l == f'{KEY}"id": "{cell_id}",']
    # a broken link, not a stale range: exit 2 so callers don't try to auto-fix
    if len(hits) != 1:
        print(f"{path}: cell id {cell_id} found {len(hits)} times", file=sys.stderr)
        sys.exit(2)
    i = hits[0]
    while not lines[i].startswith(f'{KEY}"source": ['):
        i += 1
    if lines[i].endswith("[]"):
        return i + 1, i + 1
    j = i + 1
    while lines[j] not in (f"{KEY}]", f"{KEY}],"):
        j += 1
    return i + 2, j  # first entry after '"source": [' .. last entry before ']'


def main(check):
    # canonical serialization first, so computed lines match what gets committed
    if not check:
        for rel in FILES:
            p = ROOT / rel
            text = p.read_text()
            if dump(json.loads(text)) != text:
                p.write_text(dump(json.loads(text)))
    cache, stale = {}, 0

    def sub(m):
        a, b = source_lines(m["path"], m["id"], cache)
        return f"{BASE}{m['path']}?plain=1&cell={m['id']}" + (
            f"#L{a}" if a == b else f"#L{a}-L{b}"
        )

    for rel in FILES:
        path = ROOT / rel
        nb = json.loads(path.read_text())
        changed = False
        for cell in nb["cells"]:
            if cell["cell_type"] != "markdown":
                continue
            old = "".join(cell["source"])
            new = LINK.sub(sub, old)
            if new != old:
                changed, stale = True, stale + 1
                cell["source"] = new.splitlines(keepends=True)
        if changed and not check:
            path.write_text(dump(nb))  # in-line edits only: line numbering is unchanged
    if check and stale:
        print(
            f"{stale} cell(s) with stale line anchors - run: python scripts/link_refs.py"
        )
        return 1
    print(f"{'stale' if check else 'rewritten'}: {stale} cell(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
