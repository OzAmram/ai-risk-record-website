"""List the sitting members of the US House of Representatives, with their official X handle if known.

Reads the public unitedstates/congress-legislators files (legislators-current.json and
legislators-social-media.json) and writes one row per voting member. Delegates and the
resident commissioner (who do not vote on the floor) are left out.

    python3 -I data/house/make_roster.py --legislators <folder with the two json files> --out data/house/roster.csv
"""
import argparse
import csv
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--legislators", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

people = json.load(open(os.path.join(args.legislators, "legislators-current.json")))
social = {p["id"]["bioguide"]: p["social"] for p in json.load(open(os.path.join(args.legislators, "legislators-social-media.json")))}
NON_VOTING = {"AS", "DC", "GU", "MP", "PR", "VI"}
rows = []
for p in people:
    term = p["terms"][-1]
    if term["type"] != "rep" or term["state"] in NON_VOTING:
        continue
    b = p["id"]["bioguide"]
    rows.append({"bioguide": b, "member": p["name"].get("official_full") or f"{p['name']['first']} {p['name']['last']}",
                 "last_name": p["name"]["last"], "chamber": "house", "party": term["party"], "state": term["state"],
                 "district": term.get("district", ""), "handle": social.get(b, {}).get("twitter", ""),
                 "website": term.get("url", "")})
rows.sort(key=lambda r: (r["state"], int(r["district"] or 0)))
with open(args.out, "w", newline="") as f:
    w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(len(rows), "voting members written;", sum(1 for r in rows if not r["handle"]), "without an X handle on file")
