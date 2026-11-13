"""Look up X accounts by username and print what each profile says, to confirm whose account it is.

Reads the token from the environment variable X_BEARER_TOKEN. Saves the raw response.
Each account found is billed as one user lookup.

    python3 collector/lookup_users.py --raw-dir data/raw name1 name2 ...
"""
import argparse
import datetime
import json
import os
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--raw-dir", required=True)
parser.add_argument("usernames", nargs="+")
args = parser.parse_args()

query = urllib.parse.urlencode({"usernames": ",".join(args.usernames),
                                "user.fields": "name,description,verified,verified_type,public_metrics,location"})
request = urllib.request.Request("https://api.x.com/2/users/by?" + query,
                                 headers={"Authorization": "Bearer " + os.environ["X_BEARER_TOKEN"]})
with urllib.request.urlopen(request, timeout=30) as response:
    body = json.load(response)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
path = os.path.join(args.raw_dir, f"user_lookup_names_{stamp}.json")
with open(path, "w") as f:
    json.dump(body, f, indent=1)
for u in body.get("data", []):
    print(f"{u['username']}\t{u['id']}\t{u['name']}\t{u.get('verified_type', '')}\t{u['public_metrics']['followers_count']}\t{u['description'][:110]!r}")
for e in body.get("errors", []):
    print("NOT FOUND:", e.get("value"))
print("Raw response:", path)
