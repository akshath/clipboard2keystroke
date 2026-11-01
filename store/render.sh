#!/bin/sh
# Render the Chrome Web Store images in store/ from store/src/*.html and the
# real settings page (zoomed to 92% so the speed section fits), using headless Chrome. Usage: store/render.sh
set -eu
cd "$(dirname "$0")"
here=$(pwd)
ext=$(cd ../extension && pwd)

chrome=${CHROME:-}
if [ -z "$chrome" ]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           google-chrome google-chrome-stable chromium chromium-browser; do
    if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then chrome=$c; break; fi
  done
fi
[ -n "$chrome" ] || { echo "error: Chrome not found; set CHROME=/path/to/chrome" >&2; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

shot() { # url width height out
  "$chrome" --headless --user-data-dir="$tmp/profile" --hide-scrollbars \
    --force-device-scale-factor=1 --window-size="$2,$3" \
    --screenshot="$here/$4" "$1" >/dev/null 2>&1
  echo "Rendered store/$4 ($2x$3)"
}

shot "file://$here/src/screenshot-login.html" 1280 800 screenshot-1-login.png

# The settings page as shipped, with a stand-in for the chrome.* APIs that
# only exist inside the extension.
sed 's#<meta charset="utf-8">#<meta charset="utf-8"><style>body{zoom:.92}</style><base href="file://'"$ext"'/"><script>window.chrome={runtime:{getManifest:()=>({version:"1.0.0"})},storage:{sync:{get:async d=>d,set:async()=>{}}},commands:{getAll:async()=>[{name:"type-clipboard",shortcut:"\\u2325\\u21e7K"}]},tabs:{create(){}}};</script>#' \
  "$ext/options.html" > "$tmp/options.html"
shot "file://$tmp/options.html" 1280 800 screenshot-2-settings.png

shot "file://$here/src/promo-small.html" 440 280 promo-small-440x280.png
shot "file://$here/src/promo-marquee.html" 1400 560 promo-marquee-1400x560.png
