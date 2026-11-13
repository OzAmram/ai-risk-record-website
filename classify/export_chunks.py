"""Write the collected posts to JSON files for labelling, split by senator into chunks.

    python3 classify/export_chunks.py --db data/posts.sqlite --accounts data/accounts.csv --out data/classify/input --chunk-size 65
"""
import argparse
import csv
import json
import os
import sqlite3

parser = argparse.ArgumentParser()
parser.add_argument("--db", required=True)
parser.add_argument("--accounts", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--chunk-size", type=int, default=65)
args = parser.parse_args()

with open(args.accounts, newline="") as f:
    member_by_handle = {a["handle"]: a for a in csv.DictReader(f)}

db = sqlite3.connect(args.db)
by_member = {}
for post_id, handle, created_at, text in db.execute(
    "SELECT id, handle, created_at, text FROM posts ORDER BY created_at, id"
):
    bioguide = member_by_handle[handle]["bioguide"]
    by_member.setdefault(bioguide, []).append(
        {"id": post_id, "handle": handle, "created_at": created_at, "text": text}
    )

os.makedirs(args.out, exist_ok=True)
for bioguide, posts in sorted(by_member.items()):
    for start in range(0, len(posts), args.chunk_size):
        chunk = posts[start:start + args.chunk_size]
        name = f"{bioguide}_{start // args.chunk_size + 1}.json"
        with open(os.path.join(args.out, name), "w") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=1)
        print(name, len(chunk), "posts", sum(len(p["text"]) for p in chunk), "characters")
