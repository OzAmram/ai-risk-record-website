"""Add the 75 remaining senators to data/accounts.csv as batch 4, from the saved X profile lookups.

    python3 -I data/sample/add_batch4.py --legislators <dir with legislators-current.json and legislators-social-media.json> --accounts data/accounts.csv --lookups data/raw/user_lookup_names_20261112T003306.json data/raw/user_lookup_names_20261112T003319.json data/raw/user_lookup_names_20261112T003337.json

Each looked-up account is matched to a senator by last name (and first name for the two Scotts).
Accounts whose profile did not identify the senator are listed in SKIP. Prints every match for checking.
"""
import argparse
import csv
import json

SKIP = {"SenAlsobrooks", "DebFischerNE", "SenJimJustice", "SenSheehy", "TTuberville"}
# Official accounts that do not start with "Sen" (judged from the profile text or the congress-legislators file).
OFFICIAL = {"MarshaBlackburn", "JohnBoozman", "JohnCornyn", "MikeCrapo", "SteveDaines", "ChuckGrassley", "GrassleyPress",
            "maziehirono", "McConnellPress", "JerryMoran", "lisamurkowski", "ChrisVanHollen", "MarkWarner", "RonWyden",
            "WydenPress", "gillibrandny", "Sen_Alsobrooks"}
PERSONAL = {"SenGillibrand"}  # despite the name, this is her personal account; @gillibrandny is the Senate one
NAMES = {"B001267": "Michael Bennet", "B001288": "Cory Booker", "B001319": "Katie Britt", "C001047": "Shelley Moore Capito",
         "C001113": "Catherine Cortez Masto", "C001114": "John Curtis", "G000555": "Kirsten Gillibrand",
         "H001076": "Maggie Hassan", "H000273": "John Hickenlooper", "H001042": "Mazie Hirono", "J000312": "Jim Justice",
         "K000383": "Angus King", "L000570": "Ben Ray Luján", "L000571": "Cynthia Lummis", "M000133": "Ed Markey",
         "M001243": "Dave McCormick", "P000595": "Gary Peters", "R000584": "Jim Risch", "S000148": "Chuck Schumer",
         "W000790": "Raphael Warnock", "W000805": "Mark Warner", "A000382": "Angela Alsobrooks", "S001181": "Jeanne Shaheen",
         "H001079": "Cindy Hyde-Smith", "S001217": "Rick Scott", "S001184": "Tim Scott", "C000880": "Mike Crapo",
         "G000386": "Chuck Grassley", "P000145": "Alex Padilla", "R000122": "Jack Reed"}

parser = argparse.ArgumentParser()
parser.add_argument("--legislators", required=True)
parser.add_argument("--accounts", required=True)
parser.add_argument("--lookups", nargs="+", required=True)
args = parser.parse_args()

with open(args.accounts, newline="") as f:
    rows = list(csv.DictReader(f))
have = {r["bioguide"] for r in rows}
current = json.load(open(args.legislators + "/legislators-current.json"))
senators = [m for m in current if m["terms"][-1]["type"] == "sen" and m["id"]["bioguide"] not in have]
assert len(senators) == 75, len(senators)

def keys(m):
    b = m["id"]["bioguide"]
    name = NAMES.get(b, m["name"]["first"] + " " + m["name"]["last"])
    last = name.split()[-1].lower().replace("á", "a")
    return b, name, last

new = []
for path in args.lookups:
    for u in json.load(open(path)).get("data", []):
        if u["username"] in SKIP:
            continue
        text = (u["username"] + " " + u["name"]).lower().replace("á", "a").replace("team_mitch", "mcconnell")
        hits = [m for m in senators if keys(m)[2] in text]
        if len(hits) > 1:  # the two Scotts
            hits = [m for m in hits if keys(m)[1].split()[0].lower() in text]
        assert len(hits) == 1, (u["username"], u["name"], [keys(m)[1] for m in hits])
        m = hits[0]
        b, name, _ = keys(m)
        t = m["terms"][-1]
        h = u["username"]
        kind = "official" if (h in OFFICIAL or (h.lower().startswith("sen") and h not in PERSONAL)) else "personal_or_campaign"
        new.append({"bioguide": b, "member": name, "chamber": "senate", "party": t["party"], "state": t["state"],
                    "handle": h, "x_user_id": u["id"], "account_type": kind, "batch": "4"})
new.sort(key=lambda r: (r["member"].split()[-1], r["account_type"]))
for r in new:
    print(r["member"], r["state"], r["handle"], r["account_type"], sep="\t")
missing = [keys(m)[1] for m in senators if m["id"]["bioguide"] not in {r["bioguide"] for r in new}]
assert not missing, missing
with open(args.accounts, "a", newline="") as f:
    csv.DictWriter(f, fieldnames=list(rows[0].keys())).writerows(new)
print(len(new), "accounts added for", len({r["bioguide"] for r in new}), "senators")
