#!/usr/bin/env bash
# Local preview.
#
# uv run --isolated --no-project --python 3.12 --with-requirements requirements-docs.txt scripts/preview.sh
# (PORT=8055 by default)
set -euo pipefail
PY=$(realpath -s "$(command -v "${PY:-python3}")")  # absolute, venv symlink kept
PORT=${PORT:-8055}
ROOT=$(git rev-parse --show-toplevel)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# what CI would check out (tracked files + not-yet-committed new ones), symlinks kept
(cd "$ROOT" && git ls-files -z --cached --others --exclude-standard \
    | tar --null --ignore-failed-read -T - -cf -) | tar -C "$TMP" -xf -
# hooks/seo.py reads the git index (read-only) to point view-source links at the committed file
echo "gitdir: $(git -C "$ROOT" rev-parse --absolute-git-dir)" > "$TMP/.git"

[ -z "$(git -C "$ROOT" status --porcelain)" ] ||
echo "WARNING: uncommitted changes are included here, but CI only sees what is committed." >&2

cd "$TMP"
"$PY" scripts/link_refs.py --check || {
    [ $? -eq 1 ] || exit 1
    echo "WARNING: stale line anchors - run: python scripts/link_refs.py (and commit)" >&2
    "$PY" scripts/link_refs.py
}
"$PY" scripts/render_plotly.py docs docs-en

# drop info + material banner
quiet() { "$@" 2>&1 | { grep -v -E '^INFO|│|^\s*$|\[0m$' || true; }; }
quiet "$PY" -m mkdocs build --strict -f mkdocs.yml -d "$TMP/www"
quiet "$PY" -m mkdocs build --strict -f mkdocs.en.yml -d "$TMP/www/en"

echo "PL: http://127.0.0.1:$PORT/"
echo "EN: http://127.0.0.1:$PORT/en/"
echo "built site: $TMP/www (removed on exit)"
"$PY" -m http.server "$PORT" --bind 127.0.0.1 -d "$TMP/www"
