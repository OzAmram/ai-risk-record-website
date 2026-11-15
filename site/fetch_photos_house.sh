#!/bin/sh
# Download each sitting House member's official congressional portrait (public domain) into site/img/,
# named by Bioguide ID. Same sources as site/fetch_photos.sh. Skips portraits already downloaded.
# Usage: sh site/fetch_photos_house.sh
tail -n +2 data/house/roster.csv | cut -d, -f1 | sort -u | while read -r id; do
  if [ -s "site/img/$id.jpg" ]; then
    echo "$id already there"
  elif curl -sS -L -f -m 30 -o "site/img/$id.jpg" "https://unitedstates.github.io/images/congress/450x550/$id.jpg" 2>/dev/null; then
    echo "$id ok"
  elif curl -sS -L -f -m 30 -A "Mozilla/5.0" -o "site/img/$id.jpg" "https://bioguide.congress.gov/bioguide/photo/$(echo "$id" | cut -c1)/$id.jpg" 2>/dev/null; then
    echo "$id ok (bioguide)"
  else
    rm -f "site/img/$id.jpg"; echo "$id MISSING"
  fi
done
