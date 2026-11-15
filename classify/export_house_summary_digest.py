"""Write digests of the evidence behind each House record, for drafting the one- or two-sentence
summary shown after the grade (classify/summary_prompt_house.md). People with no statement found
are left out; site/house_records.py writes their sentence by rule.

    python3 classify/export_house_summary_digest.py --records site/house_records.json --labels data/house/classify/review_queue.csv --roster data/house/roster.csv --per-file 40 --out data/house/classify/summary_digest
"""
import argparse
import collections
import csv
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--records", required=True, help="site/house_records.json")
parser.add_argument("--labels", required=True, help="Labelled X posts, for what D-level posts are about")
parser.add_argument("--roster", required=True)
parser.add_argument("--per-file", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

last_name = {r["bioguide"]: r["last_name"] for r in csv.DictReader(open(args.roster, newline=""))}
d_posts = collections.defaultdict(list)
for r in csv.DictReader(open(args.labels, newline="")):
    if r["level"] == "D":
        d_posts[r["bioguide"]].append(r)

people = []
for rec in json.load(open(args.records)):
    if rec["grade"] == "–":
        continue
    b = rec["bioguide"]
    elect = (rec.get("status") or {}).get("kind") == "representative-elect"
    # The rule-written sentence ends with one of these; anything after it is a note on how the grade was reached.
    ends = [rec["why"].find(e) + len(e) for e in ("human control.", "threat of extinction.", "in general terms.", "risk from it.", "risk from AI.") if e in rec["why"]]
    people.append({
        "bioguide": b,
        "call_them": f"Representative-elect {rec['name']}" if elect else f"Representative {last_name[b]}",
        "grade": rec["grade"],
        "grade_notes": rec["why"][min(ends):].strip() if ends else "",
        "statements": [{"date": t[0], "where": t[1], "quote": t[2], "about": t[3], "level": t[8],
                        "cosigned_letter": t[1].startswith("Letter to") and "co-signed" in t[1]} for t in rec["stmts"]],
        "topics_of_other_posts": [p["reason"] for p in sorted(d_posts[b], key=lambda p: p["date"], reverse=True)[:8]],
    })
os.makedirs(args.out, exist_ok=True)
for n, start in enumerate(range(0, len(people), args.per_file), 1):
    with open(os.path.join(args.out, f"part_{n:02d}.json"), "w") as f:
        json.dump(people[start:start + args.per_file], f, ensure_ascii=False, indent=1)
print(len(people), "people in", n, "files in", args.out)
