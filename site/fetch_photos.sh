#!/bin/sh
# Download each member's official congressional portrait (public domain) into site/img/,
# named by Bioguide ID. First choice: https://github.com/unitedstates/images
# Fallback for members it lacks: the Biographical Directory of the US Congress.
# Usage: sh site/fetch_photos.sh
tail -n +2 data/accounts.csv | cut -d, -f1 | sort -u | while read -r id; do
  if curl -sS -L -f -o "site/img/$id.jpg" "https://unitedstates.github.io/images/congress/450x550/$id.jpg" 2>/dev/null; then
    echo "$id ok"
  elif curl -sS -L -f -A "Mozilla/5.0" -o "site/img/$id.jpg" "https://bioguide.congress.gov/bioguide/photo/$(echo "$id" | cut -c1)/$id.jpg"; then
    echo "$id ok (bioguide)"
  else
    echo "$id MISSING"
  fi
done
