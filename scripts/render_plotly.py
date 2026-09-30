#!/usr/bin/env python3
"""Rewrite Plotly JSON outputs in .ipynb files into self-rendering HTML.

nbconvert (used by mkdocs-jupyter) silently drops
application/vnd.plotly.v1+json outputs, so every chart would vanish from the
site. This replaces each such output with a text/html div + Plotly.newPlot
call; plotly.js itself is loaded once per notebook page (see PLOTLY_JS).

Run in CI before `mkdocs build` — it rewrites files in place (replacing
symlinks with transformed copies), so never run it on a working tree you
care about.
"""
import json
import sys
from pathlib import Path

MIME = "application/vnd.plotly.v1+json"
# Loaded with the first chart of each notebook, so pages without charts never fetch
# it. `defer` runs it before DOMContentLoaded, when the charts below are drawn.
PLOTLY_JS = '<script defer src="https://cdn.plot.ly/plotly-3.1.0.min.js"></script>\n'


def transform(path: Path) -> int:
    nb = json.loads(path.read_text())
    n = 0
    for cell in nb["cells"]:
        for out in cell.get("outputs", []):
            fig = out.get("data", {}).pop(MIME, None)
            if fig is None:
                continue
            div = f"plotly-{path.stem}-{n}"
            # "</" escaped so chart strings can't close the script tag early
            data = json.dumps(fig.get("data", [])).replace("</", "<\\/")
            layout = json.dumps(fig.get("layout", {})).replace("</", "<\\/")
            out["data"]["text/html"] = [
                (PLOTLY_JS if n == 0 else "")
                + f'<div id="{div}" style="width:100%"></div>\n'
                f"<script>document.addEventListener('DOMContentLoaded', () => "
                f'Plotly.newPlot("{div}", {data}, {layout}, '
                f'{{"responsive": true}}))</script>'
            ]
            n += 1
    if n:
        if path.is_symlink():
            path.unlink()  # write a real transformed copy, keep the original
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n")
    return n


total = 0
for d in sys.argv[1:]:
    for p in sorted(Path(d).glob("*.ipynb")):
        total += transform(p)
        print(f"{p}: done")
assert total > 0, "no plotly outputs found - wrong input dirs?"
print(f"{total} plotly outputs converted")
