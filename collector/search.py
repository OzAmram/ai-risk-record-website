"""Collect posts about AI from member accounts through the X API search endpoints.

Builds keyword searches restricted to batches of accounts, saves every raw API
response to data/raw/, and writes one row per post to a SQLite database.

Needs the environment variable X_BEARER_TOKEN. Example (seven-day pilot):

    set -a; . ./.env; set +a
    python3 collector/search.py --accounts data/accounts.csv --db data/posts.sqlite
"""
import argparse
import csv
import datetime
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request

ENDPOINTS = {
    "recent": "https://api.x.com/2/tweets/search/recent",  # last seven days
    "all": "https://api.x.com/2/tweets/search/all",  # full archive
}

# Starting keyword list from HANDOFF.md. "frontier AI" and "AI safety" are left out
# because the bare term AI already matches them. "data centers" added for the plural.
KEYWORDS = [
    "AI", '"artificial intelligence"', "superintelligence", "AGI", "chatbot",
    "OpenAI", "Anthropic", '"data center"', '"data centers"',
]


def build_queries(handles, keywords, max_len):
    """Split handles into as few queries as fit within max_len characters."""
    tail = " (" + " OR ".join(keywords) + ") -is:retweet"
    queries, batch = [], []
    for handle in handles:
        candidate = "(" + " OR ".join("from:" + h for h in batch + [handle]) + ")" + tail
        if len(candidate) > max_len and batch:
            queries.append("(" + " OR ".join("from:" + h for h in batch) + ")" + tail)
            batch = [handle]
        else:
            batch.append(handle)
    queries.append("(" + " OR ".join("from:" + h for h in batch) + ")" + tail)
    for q in queries:
        if len(q) > max_len:
            sys.exit(f"Query is {len(q)} characters, over the limit of {max_len}: {q}")
    return queries


def get(url, params, token):
    request = urllib.request.Request(
        url + "?" + urllib.parse.urlencode(params),
        headers={"Authorization": "Bearer " + token},
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        sys.exit(f"X API returned HTTP {error.code}: {error.read().decode()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--accounts", required=True, help="CSV with handle and x_user_id columns")
    parser.add_argument("--db", required=True, help="SQLite file to write")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--endpoint", choices=ENDPOINTS, default="recent")
    parser.add_argument("--start-time", help="ISO time, e.g. 2025-01-01T00:00:00Z. Default: the API's own (seven days ago)")
    parser.add_argument("--end-time", help="ISO time. Default: now")
    parser.add_argument("--batch", help="Only search accounts whose batch column has this value")
    parser.add_argument("--max-query-len", type=int, default=512)
    parser.add_argument("--max-posts", type=int, default=500, help="Stop after this many posts, as a cost guard")
    args = parser.parse_args()

    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        sys.exit("X_BEARER_TOKEN is not set")

    with open(args.accounts, newline="") as f:
        # rows with no handle record a member for whom no account was found
        accounts = [a for a in csv.DictReader(f) if a["handle"] and (not args.batch or a.get("batch") == args.batch)]
    handle_by_id = {a["x_user_id"]: a["handle"] for a in accounts}
    queries = build_queries([a["handle"] for a in accounts], KEYWORDS, args.max_query_len)

    os.makedirs(args.raw_dir, exist_ok=True)
    db = sqlite3.connect(args.db)
    db.execute(
        """CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY, url TEXT, handle TEXT, author_id TEXT, created_at TEXT,
            text TEXT, query TEXT, fetched_at TEXT, raw_file TEXT)"""
    )

    run = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    total = 0
    for q_index, query in enumerate(queries):
        print(f"Query {q_index + 1} of {len(queries)} ({len(query)} characters): {query}")
        params = {
            "query": query,
            "max_results": 100,
            # note_tweet holds the full text of posts longer than 280 characters
            "tweet.fields": "created_at,author_id,note_tweet,conversation_id,referenced_tweets",
        }
        if args.start_time:
            params["start_time"] = args.start_time
        if args.end_time:
            params["end_time"] = args.end_time
        page = 0
        while True:
            body = get(ENDPOINTS[args.endpoint], params, token)
            raw_file = os.path.join(args.raw_dir, f"search_{run}_q{q_index}_p{page}.json")
            with open(raw_file, "w") as f:
                json.dump({"endpoint": args.endpoint, "params": params, "response": body}, f, ensure_ascii=False, indent=1)
            for post in body.get("data", []):
                handle = handle_by_id.get(post["author_id"])
                if handle is None:
                    sys.exit(f"Post {post['id']} has author {post['author_id']}, not in the accounts file")
                text = post.get("note_tweet", {}).get("text") or post["text"]
                db.execute(
                    "INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?,?,?,?)",
                    (post["id"], f"https://x.com/{handle}/status/{post['id']}", handle, post["author_id"],
                     post["created_at"], text, query, run, raw_file),
                )
                total += 1
            db.commit()
            next_token = body.get("meta", {}).get("next_token")
            page += 1
            if not next_token:
                break
            if total >= args.max_posts:
                sys.exit(f"Stopped at {total} posts (--max-posts {args.max_posts}); more results remain")
            params["next_token"] = next_token
    print(f"Done. {total} posts returned by the API in this run; database: {args.db}")


if __name__ == "__main__":
    main()
