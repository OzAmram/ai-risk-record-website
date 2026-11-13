"""Check each quote found by the news search against the page it links to.

For every statement in the news search files, download the linked page, strip the markup, and
look for the quote (ignoring differences in spacing, quote marks and dashes). Writes one row per
statement. "found" is real confirmation that the wording is on the page; "not_found" and
"fetch_failed" mean a person still has to check (many news sites refuse automatic downloads,
and PDFs are not read).

    python3 classify/check_news_quotes.py --news data/news --out data/news/quote_check.csv
"""
import argparse
import csv
import glob
import html
import json
import os
import re
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--news", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()


def normalise(text):
    text = html.unescape(text)
    text = re.sub(r"[‘’“”\"'`]", "", text)  # quote marks vary between copies
    text = re.sub(r"[‐-―-]", " ", text)
    return re.sub(r"\s+", " ", text).lower().strip()


pages = {}


def page_text(url):
    if url not in pages:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (quote check for a research project)"})
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8", errors="replace")
            body = re.sub(r"(?s)<(script|style)\b.*?</\1>", " ", body)
            pages[url] = normalise(re.sub(r"<[^>]+>", " ", body))
        except Exception as error:  # recorded in the output, not hidden
            pages[url] = error
    return pages[url]


rows = []
for path in sorted(glob.glob(os.path.join(args.news, "*.json"))):
    record = json.load(open(path))
    for s in record["statements"]:
        text = page_text(s["url"])
        if isinstance(text, Exception):
            result, detail = "fetch_failed", str(text)[:100]
        else:
            result, detail = ("found" if normalise(s["quote"]) in text else "not_found"), ""
        rows.append([record["bioguide"], record["member"], s["url"], result, detail, s["quote"]])
        print(result, record["member"], s["url"])

with open(args.out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["bioguide", "member", "url", "result", "detail", "quote"])
    w.writerows(rows)
counts = {}
for r in rows:
    counts[r[3]] = counts.get(r[3], 0) + 1
print(len(rows), "statements checked:", counts)
