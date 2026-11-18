#!/bin/bash
# Make the link preview image site/preview.png (1200 x 630) from site/preview_card.html with headless Chrome.
#     bash site/make_preview.sh
set -euo pipefail
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --hide-scrollbars \
  --window-size=1200,630 --virtual-time-budget=5000 --screenshot="$PWD/site/preview.png" "file://$PWD/site/preview_card.html" 2>/dev/null
sips -g pixelWidth -g pixelHeight site/preview.png | tail -2
