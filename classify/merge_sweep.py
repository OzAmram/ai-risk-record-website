"""Add statements found by a themed news sweep to the per-person news search files.

A sweep file (data/news_sweep/<date>.json) lists statements and record items for many people,
each with "bioguide" and "chamber". This appends each to that person's news file, skipping
quotes already there, and adds a dated note. Files keep their own layout.

    python3 classify/merge_sweep.py --sweep data/news_sweep/2026-11-23.json --news data/news --news-house data/news_house
"""
import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--sweep", required=True)
parser.add_argument("--news", required=True, help="Folder of Senate-side news files")
parser.add_argument("--news-house", required=True, help="Folder of House news files")
args = parser.parse_args()

sweep = json.load(open(args.sweep))
mark = f"News sweep of {sweep['window']} (run {sweep['run']})"
added = {}
for kind, items in (("statements", sweep["statements"]), ("record", sweep["record_items"])):
    for item in items:
        added.setdefault(item["bioguide"], {"statements": [], "record": []})[kind].append(item)
for bioguide, new in sorted(added.items()):
    paths = [os.path.join(folder, bioguide + ".json") for folder in (args.news, args.news_house)]
    paths = [p for p in paths if os.path.exists(p)]
    if len(paths) != 1:
        raise SystemExit(f"{bioguide}: expected one news file, found {paths}")
    raw = open(paths[0]).read()
    found = json.loads(raw)
    if mark in found["notes"]:
        print(found["member"], "already merged; skipped")
        continue
    indent = len(raw.split("\n")[1]) - len(raw.split("\n")[1].lstrip())
    old = {s["quote"] for s in found["statements"]}
    statements = [{k: v for k, v in s.items() if k not in ("bioguide", "member", "chamber")}
                  for s in new["statements"] if s["quote"] not in old]
    found["statements"] += statements
    record = [[r["item"], r["source_label"], r["url"]] for r in new["record"]]
    found["record"] += [r for r in record if r not in found["record"]]
    found["notes"] += f" {mark}: {len(statements)} statement{'s' if len(statements) != 1 else ''} and {len(record)} record item{'s' if len(record) != 1 else ''} added."
    with open(paths[0], "w") as f:
        json.dump(found, f, indent=indent or None, ensure_ascii="\\u" in raw)
        f.write("\n" if raw.endswith("\n") else "")
    print(f"{found['member']}: +{len(statements)} statements ({', '.join(s['level'] for s in statements) or 'none'}), +{len(record)} record items")
