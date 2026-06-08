#!/usr/bin/env bash
# Export docs/assets/*.mmd to docs/assets/generated/*.png
# Requires: npm install -g @mermaid-js/mermaid-cli

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASSETS="$REPO_ROOT/docs/assets"
OUT="$ASSETS/generated"
mkdir -p "$OUT"

if ! command -v mmdc >/dev/null 2>&1; then
  echo "mmdc not found. Install: npm install -g @mermaid-js/mermaid-cli" >&2
  exit 1
fi

for f in "$ASSETS"/*.mmd; do
  [ -e "$f" ] || continue
  base=$(basename "$f" .mmd)
  mmdc -i "$f" -o "$OUT/${base}.png" -b transparent
  echo "Wrote $OUT/${base}.png"
done
echo "Done."
