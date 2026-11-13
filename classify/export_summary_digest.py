"""Write a short digest of the evidence for each person in one batch, for drafting the one- or
two-sentence summary shown after the grade (data/summaries.csv).

    python3 classify/export_summary_digest.py --labels data/classify/review_queue.csv --news data/news --accounts data/accounts.csv --batch 4 --parts 4 --out data/classify/summary_digest

The draft grade follows site/build.py: the highest level among X posts and news statements
(first of A, B, C, F, D), with every passage of the 23 September 2026 letter counted as A.
"""
import argparse
import collections
import csv
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--labels", required=True)
parser.add_argument("--news", required=True)
parser.add_argument("--accounts", required=True)
parser.add_argument("--batch", required=True)
parser.add_argument("--parts", type=int, required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

people = {}
for a in csv.DictReader(open(args.accounts, newline="")):
    if a["batch"] == args.batch:
        people.setdefault(a["bioguide"], a)
posts = collections.defaultdict(list)
for r in csv.DictReader(open(args.labels, newline="")):
    if r["bioguide"] in people and r["level"] != "off_topic":
        posts[r["bioguide"]].append(r)

digests = []
for b, a in sorted(people.items(), key=lambda kv: kv[1]["member"].split()[-1]):
    news = json.load(open(os.path.join(args.news, b + ".json")))
    for st in news["statements"]:
        st["letter"] = "cosigned_letter" in st.get("flags", []) and st["date"] == "2026-09-23"
        if st["letter"]:
            st["level"] = "A"
    levels = [st["level"] for st in news["statements"]] + [r["level"] for r in posts[b]]
    grade = next((g for g in "ABCFD" if g in levels), "none")
    own = [st["level"] for st in news["statements"] if not st["letter"]] + [r["level"] for r in posts[b]]
    strong = [{"where": st["venue"], "date": st["date"], "level": st["level"], "quote": st["quote"], "context": st["context"],
               "from_the_17_senator_letter": st["letter"], "flags": st.get("flags", [])}
              for st in news["statements"] if st["level"] in "ABCF"]
    strong += [{"where": "X post", "date": r["date"][:10], "level": r["level"], "quote": r["quote"], "context": r["reason"], "flags": r["flags"]}
               for r in posts[b] if r["level"] in "ABCF"]
    strong.sort(key=lambda s: "ABCF".index(s["level"]))
    ordinary = [{"where": st["venue"], "date": st["date"], "quote": st["quote"], "context": st["context"]}
                for st in news["statements"] if st["level"] == "D"][:3]
    x_topics = [r["reason"] for r in posts[b] if r["level"] == "D"][-8:]
    positions = {k: {"value": v["value"], "note": v["note"]} for k, v in news["positions"].items() if v["value"] != "none"}
    for column in ("pause", "slowdown", "intl"):
        values = sorted({r[column] for r in posts[b] if r[column] != "none"})
        if values:
            positions.setdefault(column, {})["stated_in_x_posts"] = values
    digests.append({"bioguide": b, "name": a["member"], "party": a["party"], "state": a["state"], "draft_grade": grade,
                    "highest_level_in_own_words": next((g for g in "ABCFD" if g in own), "none"),
                    "statements_A_B_C_F": strong[:12], "ordinary_ai_statements": ordinary,
                    "what_ordinary_x_posts_are_about": x_topics, "positions_stated": positions,
                    "searcher_grade_reason": news["grade_reason"], "x_posts_about_ai": len(posts[b])})

os.makedirs(args.out, exist_ok=True)
size = -(-len(digests) // args.parts)
for n in range(args.parts):
    part = digests[n * size:(n + 1) * size]
    with open(os.path.join(args.out, f"part_{n + 1}.json"), "w") as f:
        json.dump(part, f, ensure_ascii=False, indent=1)
    print(f"part_{n + 1}.json", len(part), "people")
print(collections.Counter(d["draft_grade"] for d in digests))
