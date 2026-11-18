#!/bin/bash
# Collect the files the public site needs into public/ (the page and the portraits, nothing else),
# ready to upload to the host. Run from the project root after site/build.py and site/render_check.py.
#     bash site/make_public.sh
set -euo pipefail
python3 site/render_check.py site/index.html
rm -rf public
mkdir -p public/img
cp site/index.html site/preview.png public/
cp site/img/*.jpg public/img/
echo "public/ holds $(find public -type f | wc -l | tr -d ' ') files, $(du -sh public | cut -f1)"
