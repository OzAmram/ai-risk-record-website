"""Pick a random sample of current senators to add to the account list.

    python3 data/sample/pick_senators.py --legislators <dir with legislators-current.json and legislators-social-media.json> --accounts data/accounts.csv --n 20 --seed 20261111

Source data: https://unitedstates.github.io/congress-legislators/ (JSON files).
"""
import argparse
import csv
import json
import random

parser = argparse.ArgumentParser()
parser.add_argument("--legislators", required=True)
parser.add_argument("--accounts", required=True)
parser.add_argument("--n", type=int, required=True)
parser.add_argument("--seed", type=int, required=True)
args = parser.parse_args()

current = json.load(open(args.legislators + "/legislators-current.json"))
social = {s["id"]["bioguide"]: s["social"] for s in json.load(open(args.legislators + "/legislators-social-media.json"))}
with open(args.accounts, newline="") as f:
    have = {a["bioguide"] for a in csv.DictReader(f)}

senators = sorted((m for m in current if m["terms"][-1]["type"] == "sen" and m["id"]["bioguide"] not in have),
                  key=lambda m: m["id"]["bioguide"])
print(len(senators), "current senators not yet in the account list")
for m in sorted(random.Random(args.seed).sample(senators, args.n), key=lambda m: m["name"]["last"]):
    t, b = m["terms"][-1], m["id"]["bioguide"]
    s = social.get(b, {})
    print(",".join([b, m["name"].get("official_full") or m["name"]["first"] + " " + m["name"]["last"], t["party"], t["state"],
                    s.get("twitter", ""), str(s.get("twitter_id", ""))]))
