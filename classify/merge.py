"""Check the labelled chunks against their inputs and write one review file.

Fails loudly if any post is missing, duplicated or unknown, if a label is not an
allowed value, or if a quote is not an exact piece of the post's text.

    python3 classify/merge.py --input data/classify/input --output data/classify/output --review data/classify/review_queue.csv --overrides classify/overrides.csv
"""
import argparse
import csv
import json
import os
import sys

LEVELS = {"A", "B", "C", "D", "F", "off_topic"}
POSITIONS = {"yes", "no", "mixed", "none"}
FLAGS = {"relayed_warning", "bill_or_action", "cosigned_letter", "boundary", "needs_media", "unsure"}
ORDER = ["A", "B", "C", "F", "D", "off_topic"]

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--review", required=True)
parser.add_argument("--overrides", help="CSV of id, level, note: levels set by a person, which replace the labeller's")
args = parser.parse_args()

overrides = {}
if args.overrides:
    with open(args.overrides, newline="") as f:
        overrides = {r["id"]: r for r in csv.DictReader(f)}
    assert all(r["level"] in LEVELS for r in overrides.values()), "bad level in overrides"

problems, rows, used = [], [], set()
for name in sorted(os.listdir(args.input)):
    posts = json.load(open(os.path.join(args.input, name)))
    out_path = os.path.join(args.output, name)
    if not os.path.exists(out_path):
        problems.append(f"{name}: no output file")
        continue
    labels = json.load(open(out_path))
    if [str(l.get("id")) for l in labels] != [p["id"] for p in posts]:
        problems.append(f"{name}: ids do not match the input ({len(labels)} labels, {len(posts)} posts)")
        continue
    for post, label in zip(posts, labels):
        where = f"{name} post {post['id']}"
        if label.get("level") not in LEVELS:
            problems.append(f"{where}: bad level {label.get('level')!r}")
        for field in ("pause", "slowdown", "intl"):
            if label.get(field) not in POSITIONS:
                problems.append(f"{where}: bad {field} {label.get(field)!r}")
        if not set(label.get("flags", [])) <= FLAGS:
            problems.append(f"{where}: bad flags {label.get('flags')!r}")
        quote = label.get("quote", "")
        if quote and quote not in post["text"]:
            problems.append(f"{where}: quote is not an exact piece of the post text")
        if label.get("level") in {"A", "B", "C", "F"} and not quote:
            problems.append(f"{where}: level {label['level']} has no quote")
        note = ""
        if post["id"] in overrides:
            used.add(post["id"])
            label = dict(label, level=overrides[post["id"]]["level"])
            note = overrides[post["id"]]["note"]
            if label["level"] in {"D", "off_topic"}:
                quote = ""
        rows.append({
            "bioguide": name.split("_")[0], "handle": post["handle"], "date": post["created_at"][:10],
            "url": f"https://x.com/{post['handle']}/status/{post['id']}",
            "level": label.get("level"), "pause": label.get("pause"), "slowdown": label.get("slowdown"),
            "intl": label.get("intl"), "flags": " ".join(label.get("flags", [])),
            "quote": quote, "reason": label.get("reason", ""), "text": post["text"],
            "reviewer_level": label["level"] if note else "", "reviewer_notes": note,
        })

problems += [f"override for unknown post {i}" for i in set(overrides) - used]
if problems:
    print("\n".join(problems))
    sys.exit(f"{len(problems)} problems; review file not written")

rows.sort(key=lambda r: (r["bioguide"], ORDER.index(r["level"]), r["date"]))
with open(args.review, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f"{len(rows)} posts written to {args.review}")
