"""Check the House summary sentences written by subagents and join them into one file.

    python3 data/house/merge_summaries.py --parts data/house/summaries --digests data/house/classify/summary_digest --out data/house/summaries.csv

Checks, per person: exactly one row; the sentence starts with the name form the digest gave;
every passage in straight double quotes appears exactly in one of that person's quotes;
20 to 70 words. Rows that fail are listed and left out (those people keep the sentence written by
rule). The grade the sentence was written for is stored beside it.
"""
import argparse
import csv
import glob
import json
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("--parts", required=True)
parser.add_argument("--digests", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

rows, problems = [], []
for digest_path in sorted(glob.glob(os.path.join(args.digests, "part_*.json"))):
    people = json.load(open(digest_path))
    part = os.path.join(args.parts, os.path.basename(digest_path).replace(".json", ".csv"))
    if not os.path.exists(part):
        problems.append((os.path.basename(part), "file missing"))
        continue
    written = list(csv.DictReader(open(part, newline="")))
    by_id = {}
    for r in written:
        by_id.setdefault(r["bioguide"], []).append(r["summary"].strip())
    for p in people:
        got = by_id.get(p["bioguide"], [])
        if len(got) != 1:
            problems.append((p["bioguide"], f"{len(got)} rows"))
            continue
        text = got[0]
        quotes = [s["quote"] for s in p["statements"]]
        bad = [q for q in re.findall(r'"([^"]+)"', text) if not any(q.rstrip(".,") in src for src in quotes)]
        words = len(text.split())
        if not text.startswith(p["call_them"]):
            problems.append((p["bioguide"], "does not start with " + p["call_them"]))
        elif bad:
            problems.append((p["bioguide"], "quoted words not in their statements: " + " | ".join(bad)))
        elif not 20 <= words <= 70:
            problems.append((p["bioguide"], f"{words} words"))
        else:
            rows.append({"bioguide": p["bioguide"], "summary": text, "grade": p["grade"]})
with open(args.out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["bioguide", "summary", "grade"], lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(len(rows), "summaries written to", args.out, "|", len(problems), "left out:")
for p in problems:
    print("  ", *p)
