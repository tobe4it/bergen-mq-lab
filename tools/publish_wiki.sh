#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-}"
if [[ -n "$MODE" && "$MODE" != "--push" ]]; then
  echo "Usage: bash tools/publish_wiki.sh [--push]" >&2
  exit 2
fi
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
if ! git clone --quiet https://github.com/tobe4it/bergen-mq-lab.wiki.git "$WORK/wiki"; then
  echo "Initialize the first Home page on GitHub and verify Wiki Git access." >&2
  exit 1
fi
for f in "$ROOT"/wiki/Quick-Start-??.md; do cp "$f" "$WORK/wiki/"; done
cp "$ROOT/wiki/Home.md" "$ROOT/wiki/_Sidebar.md" "$WORK/wiki/"
for lang in EN DE FR; do cp "$ROOT/wiki/${lang,,}/Guide.md" "$WORK/wiki/Guide-$lang.md"; done
cd "$WORK/wiki"
git add Home.md _Sidebar.md Quick-Start-??.md Guide-EN.md Guide-DE.md Guide-FR.md
if git diff --cached --quiet; then echo "Wiki already up to date."; exit 0; fi
git diff --cached --stat
if [[ "$MODE" != "--push" ]]; then echo "Dry-run only: use --push to publish."; exit 0; fi
git commit -m "docs: add MQSC Quick Starts in 24 EU languages"
git push origin HEAD
echo "Published. Verify the live GitHub Wiki."
