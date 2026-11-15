"""Make the zip code lookup table for the site: which congressional district(s) each zip code is in.

Source: the US Census Bureau's table relating zip code areas to the districts of the current
(119th) Congress, downloaded with
    curl -o data/raw/census/tab20_cd11920_zcta520_natl.txt https://www2.census.gov/geo/docs/maps-data/data/rel2020/cd-sld/tab20_cd11920_zcta520_natl.txt

    python3 site/make_zip_districts.py --table data/raw/census/tab20_cd11920_zcta520_natl.txt --min-share 0.01 --out site/zip_districts.json

Limits: the Census areas are close to, but not the same as, postal zip codes (zip codes used only
for post office boxes are missing). The districts are those of the current House, not the ones
used in the November 2026 elections. Only the 50 states are kept.
"""
import argparse
import collections
import csv
import json

FIPS = {"01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas", "06": "California", "08": "Colorado",
        "09": "Connecticut", "10": "Delaware", "12": "Florida", "13": "Georgia", "15": "Hawaii", "16": "Idaho",
        "17": "Illinois", "18": "Indiana", "19": "Iowa", "20": "Kansas", "21": "Kentucky", "22": "Louisiana",
        "23": "Maine", "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
        "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska", "32": "Nevada",
        "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico", "36": "New York", "37": "North Carolina",
        "38": "North Dakota", "39": "Ohio", "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania",
        "44": "Rhode Island", "45": "South Carolina", "46": "South Dakota", "47": "Tennessee", "48": "Texas",
        "49": "Utah", "50": "Vermont", "51": "Virginia", "53": "Washington", "54": "West Virginia",
        "55": "Wisconsin", "56": "Wyoming"}

parser = argparse.ArgumentParser()
parser.add_argument("--table", required=True)
parser.add_argument("--min-share", type=float, required=True,
                    help="Leave out a district that covers less than this share of the zip code's area")
parser.add_argument("--out", required=True)
args = parser.parse_args()

states = sorted(FIPS.values())
parts = collections.defaultdict(dict)  # zip code -> {(state number, district number): area}
skipped = collections.Counter()
with open(args.table, encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f, delimiter="|"):
        zip_code, district = row["GEOID_ZCTA5_20"], row["GEOID_CD119_20"]
        if not zip_code:
            continue  # part of a district outside any zip code area
        if district[:2] not in FIPS:
            skipped["outside the 50 states"] += 1
            continue
        if not district[2:].isdigit():
            skipped["no district defined"] += 1
            continue
        key = (states.index(FIPS[district[:2]]), int(district[2:]))  # district 0 means at large
        parts[zip_code][key] = parts[zip_code].get(key, 0) + int(row["AREALAND_PART"]) + int(row["AREAWATER_PART"])

zips, dropped, several = {}, 0, 0
for zip_code in sorted(parts):
    total = sum(parts[zip_code].values())
    keep = [k for k, area in sorted(parts[zip_code].items(), key=lambda p: -p[1]) if area >= args.min_share * total]
    dropped += len(parts[zip_code]) - len(keep)
    several += len(keep) > 1
    zips[zip_code] = " ".join(f"{s}-{d}" for s, d in keep)  # largest share first
with open(args.out, "w") as f:
    json.dump({"states": states, "zips": zips}, f, separators=(",", ":"))
print(len(zips), "zip codes written to", args.out, "|", several, "are in more than one district |", dropped,
      "small overlaps left out | rows skipped:", dict(skipped))
