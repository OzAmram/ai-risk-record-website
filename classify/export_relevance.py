"""Export the posts labelled D for people with nothing stronger, for the relevance pass
(see classify/relevance_prompt.md). Posts already judged in the output folder are skipped.

    python3 classify/export_relevance.py --labels data/classify/review_queue.csv --news data/news --template xrisk-record.html --out data/classify/relevance/input --done data/classify/relevance/output --chunk-size 125
"""
import argparse, collections, csv, glob, json, os, re

parser = argparse.ArgumentParser()
for name in ("labels", "news", "template", "out", "done"):
    parser.add_argument("--" + name, required=True)
parser.add_argument("--chunk-size", type=int, required=True)
args = parser.parse_args()

STRONG = {"A", "B", "C", "F"}
rows = collections.defaultdict(list)
for r in csv.DictReader(open(args.labels, newline="")):
    rows[r["bioguide"]].append(r)
strong_news = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(args.news, "*.json"))
               if any(s["level"] in STRONG for s in json.load(open(p))["statements"])}
hand = dict(re.findall(r'bioguide:"(\w+)",name:"[^"]*",seat:"[^"]*",grade:"(.)"', open(args.template).read()))
done = {o["id"] for p in glob.glob(os.path.join(args.done, "*.json")) for o in json.load(open(p))}
posts = [{"id": r["url"].rsplit("/", 1)[1], "handle": r["handle"], "date": r["date"], "text": r["text"]}
         for b, rs in sorted(rows.items())
         if not any(r["level"] in STRONG for r in rs) and b not in strong_news and hand.get(b, "D") in "D–"
         for r in rs if r["level"] == "D" and r["url"].rsplit("/", 1)[1] not in done]
os.makedirs(args.out, exist_ok=True)
os.makedirs(args.done, exist_ok=True)
stamp = len(glob.glob(os.path.join(args.out, "*.json")))
for n in range(0, len(posts), args.chunk_size):
    path = os.path.join(args.out, f"chunk_{stamp + n // args.chunk_size + 1}.json")
    json.dump(posts[n:n + args.chunk_size], open(path, "w"), indent=1, ensure_ascii=False)
    print(path, len(posts[n:n + args.chunk_size]), "posts")
print(len(posts), "posts exported")
