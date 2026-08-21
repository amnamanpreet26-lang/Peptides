#!/usr/bin/env bash
# Rebuild the installable plugin zip from source.
# Run this after changing anything under plugin/compound-index/.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root/plugin"

for f in $(find compound-index -name '*.php'); do
	php -l "$f" > /dev/null
done

rm -f "$root/compound-index.zip"
zip -rq "$root/compound-index.zip" compound-index -x '*.DS_Store' -x '__MACOSX/*'

echo "built compound-index.zip ($(du -h "$root/compound-index.zip" | cut -f1))"
