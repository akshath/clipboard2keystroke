#!/bin/sh
# Build the Chrome Web Store / Edge Add-ons upload: dist/clipboard2keystroke-<version>.zip
# Usage: ./package.sh
set -eu

cd "$(dirname "$0")"

version=$(sed -n 's/^ *"version": *"\([^"]*\)".*/\1/p' extension/manifest.json)
[ -n "$version" ] || { echo "error: no version in extension/manifest.json" >&2; exit 1; }

for size in 16 32 48 128; do
  [ -f "extension/icons/icon$size.png" ] || {
    echo "error: missing extension/icons/icon$size.png" >&2; exit 1; }
done

mkdir -p dist
out="dist/clipboard2keystroke-$version.zip"
rm -f "$out"

# manifest.json must sit at the top of the zip, so zip from inside extension/.
# Tests and icon sources are not part of the extension.
(cd extension && zip -qr "../$out" . -x 'test/*' 'icons/*.svg' '*.DS_Store')

echo "Built $out"
unzip -l "$out"
