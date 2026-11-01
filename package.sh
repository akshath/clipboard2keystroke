#!/bin/sh
# Build the store uploads from extension/:
#   dist/clipboard2keystroke-chrome-<version>.zip   Chrome Web Store, Edge Add-ons
#   dist/clipboard2keystroke-firefox-<version>.zip  Firefox Add-ons (AMO)
#   dist/firefox/                                   unpacked Firefox build, for
#                                                   about:debugging and web-ext lint
#
# extension/manifest.json is the Chrome/Edge manifest. The Firefox build
# rewrites it: a background page instead of the service worker, no offscreen
# API, and the add-on ID from firefox/browser_specific_settings.json.
#
# Usage: ./package.sh
set -eu

cd "$(dirname "$0")"

version=$(sed -n 's/^ *"version": *"\([^"]*\)".*/\1/p' extension/manifest.json)
[ -n "$version" ] || { echo "error: no version in extension/manifest.json" >&2; exit 1; }

for size in 16 32 48 128; do
  [ -f "extension/icons/icon$size.png" ] || {
    echo "error: missing extension/icons/icon$size.png" >&2; exit 1; }
done

# Rewriting JSON needs Python; fall back to uv, which this project uses anyway.
if command -v python3 >/dev/null 2>&1; then
  python() { python3 "$@"; }
elif command -v uv >/dev/null 2>&1; then
  python() { uv run --no-project python "$@"; }
else
  echo "error: python3 or uv is needed to build the Firefox manifest" >&2; exit 1
fi

mkdir -p dist

# --- Chrome / Edge ---------------------------------------------------------

chrome_zip="dist/clipboard2keystroke-chrome-$version.zip"
rm -f "$chrome_zip"
# manifest.json must sit at the top of the zip, so zip from inside extension/.
# Tests and icon sources are not part of the extension.
(cd extension && zip -qr "../$chrome_zip" . -x 'test/*' 'icons/*.svg' '*.DS_Store')
echo "Built $chrome_zip"

# --- Firefox ---------------------------------------------------------------

rm -rf dist/firefox
mkdir -p dist/firefox
# Firefox has no offscreen API, so the offscreen page is left out.
(cd extension && tar cf - --exclude test --exclude 'icons/*.svg' \
  --exclude offscreen.html --exclude offscreen.js --exclude .DS_Store . ) |
  (cd dist/firefox && tar xf -)

python - extension/manifest.json firefox/browser_specific_settings.json \
  dist/firefox/manifest.json <<'EOF'
import json, sys

src, gecko_file, out = sys.argv[1:]
with open(src) as f:
    manifest = json.load(f)
with open(gecko_file) as f:
    gecko = json.load(f)

manifest.pop('minimum_chrome_version', None)
manifest['background'] = {'scripts': [manifest['background']['service_worker']]}
manifest['permissions'] = [p for p in manifest['permissions'] if p != 'offscreen']
manifest['browser_specific_settings'] = gecko

with open(out, 'w') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write('\n')
EOF

firefox_zip="dist/clipboard2keystroke-firefox-$version.zip"
rm -f "$firefox_zip"
(cd dist/firefox && zip -qr "../../$firefox_zip" .)
echo "Built $firefox_zip (unpacked copy in dist/firefox/)"
