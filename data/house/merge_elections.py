"""Combine the per-state election result files into one table and work out who is new and who is leaving.

    python3 data/house/merge_elections.py --results data/house/elections --roster data/house/roster.csv --out data/house/election_2026.csv --elect data/house/members_elect.csv --leaving data/house/not_returning.csv

Checks that there are 435 districts, each once, and that every winner marked as a sitting
member is in the roster with a matching last name.
"""
import argparse
import collections
import csv
import glob
import json
import os
import unicodedata

parser = argparse.ArgumentParser()
parser.add_argument("--results", required=True)
parser.add_argument("--roster", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--elect", required=True)
parser.add_argument("--leaving", required=True)
args = parser.parse_args()

plain = lambda s: "".join(c for c in unicodedata.normalize("NFD", s.lower()) if c.isalpha())
with open(args.roster, newline="") as f:
    roster = {r["bioguide"]: r for r in csv.DictReader(f)}
rows = []
for path in sorted(glob.glob(os.path.join(args.results, "*.json"))):
    rows += json.load(open(path))["districts"]
seats = collections.Counter((r["state"], int(r["district"])) for r in rows)
if len(rows) != 435 or any(n != 1 for n in seats.values()):
    raise SystemExit(f"{len(rows)} rows; districts listed more than once: {[k for k, n in seats.items() if n != 1]}")
problems = []
for r in rows:
    b = r.get("sitting_bioguide", "")
    if b and (b not in roster or plain(roster[b]["last_name"]) not in plain(r["winner"])):
        problems.append((r["state"], r["district"], r["winner"], b))
    if not b and r["winner"]:  # a winner not marked as sitting whose name matches a sitting member of that state
        same = [m for m in roster.values() if m["state"] == r["state"] and plain(m["last_name"]) in plain(r["winner"]) and plain(m["member"].split()[0]) in plain(r["winner"])]
        if same:
            problems.append((r["state"], r["district"], r["winner"], "looks like sitting member " + same[0]["bioguide"]))
if problems:
    raise SystemExit(f"Check these rows: {problems}")
fields = ["state", "district", "winner", "party", "status", "sitting_bioguide", "previous", "background", "source_label", "source_url"]
rows.sort(key=lambda r: (r["state"], int(r["district"])))
for path, keep in ((args.out, rows), (args.elect, [r for r in rows if r["winner"] and not r.get("sitting_bioguide") and r["status"] == "called"])):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(keep)
returning = {r["sitting_bioguide"] for r in rows if r.get("sitting_bioguide")}
undecided = {(r["state"], int(r["district"])) for r in rows if r["status"] != "called"}
with open(args.leaving, "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["bioguide", "member", "party", "state", "district", "note"])
    for b, m in roster.items():
        if b not in returning:
            w.writerow([b, m["member"], m["party"], m["state"], m["district"],
                        "this district's race is not yet called; may still be returning" if (m["state"], int(m["district"])) in undecided else ""])
status = collections.Counter(r["status"] for r in rows)
party = collections.Counter(r["party"] for r in rows if r["status"] == "called")
print(f"435 districts: {dict(status)}; called seats by party: {dict(party)}")
print(f"{sum(1 for r in rows if r['winner'] and not r.get('sitting_bioguide') and r['status'] == 'called')} members-elect; "
      f"{len(returning)} sitting members returning; {len(roster) - len(returning)} sitting members not among the winners")
