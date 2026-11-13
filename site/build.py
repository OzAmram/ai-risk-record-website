"""Build the review page: the prototype template plus each senator's X posts labelled A, B, C or F.

The template itself picks which statements to show (see `statements` in its script).

Posts whose link already appears in the template (cited by hand) are not added again.

Reads the labelled posts and writes a copy of the template with the post data filled in.

Senators without a hand-written record in the template get a drafted one, from the X labels and,
if present, the news search files (see classify/news_search_brief.md) and the automatic quote
check (classify/check_news_quotes.py). The status file marks senators-elect and lame ducks.

    python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --news data/news --quote-check data/news/quote_check.csv --status data/status.csv --summaries data/summaries.csv --relevance data/classify/relevance/output --map site/us_states.json --grade-overrides data/grade_overrides.csv

The summaries file holds the sentence shown after each drafted record's grade. It is written by hand
(so far by the assistant, from the statements found) and must be revised when a grade changes.
"""
import argparse
import collections
import csv
import datetime
import glob
import html
import json
import os
import re

PLACEHOLDER = "const XPOSTS = {}; /*XPOSTS*/"
SENATORS_PLACEHOLDER = "const XSENATORS = []; /*XSENATORS*/"
STATUS_PLACEHOLDER = "const STATUS = {}; /*STATUS*/"
MAP_PLACEHOLDER = "const STATE_PATHS = {}; /*STATE_PATHS*/"
STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
          "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
          "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
          "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
          "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
          "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
          "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
          "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
          "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
          "WI": "Wisconsin", "WY": "Wyoming"}
# page field -> column in the labels file
POLICIES = {"slow": "slowdown", "pause": "pause", "intl": "intl"}
RANK = {"A", "B", "C", "F"}  # levels that are evidence; D and off_topic posts are never shown

parser = argparse.ArgumentParser()
parser.add_argument("--labels", required=True)
parser.add_argument("--accounts", required=True)
parser.add_argument("--template", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--since", required=True, help="Start of the collection period, as shown on the page")
parser.add_argument("--news", help="Folder of news search files, one per politician")
parser.add_argument("--quote-check", help="Output of classify/check_news_quotes.py")
parser.add_argument("--summaries", required=True, help="CSV with one written sentence per drafted record, shown after the grade")
parser.add_argument("--relevance", required=True, help="Folder of relevance decisions for posts labelled D")
parser.add_argument("--status", help="CSV marking senators-elect and lame-duck senators")
parser.add_argument("--grade-overrides", help="CSV of grades ruled by a person, which replace the drafted grade")
parser.add_argument("--map", required=True, help="State outlines written by site/make_map.py")
args = parser.parse_args()


def show_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


with open(args.accounts, newline="") as f:
    # the template identifies senators by lower-case last name
    accounts = list(csv.DictReader(f))
last_names = collections.Counter(n.split()[-1].lower() for n in {a["bioguide"]: a["member"] for a in accounts}.values())
# people who share a last name (the two Scotts) get first and last name, e.g. "rick-scott"
page_id = {a["bioguide"]: a["member"].split()[-1].lower() if last_names[a["member"].split()[-1].lower()] == 1
           else "-".join(a["member"].lower().split()) for a in accounts}
if len(set(page_id.values())) != len(page_id):
    raise SystemExit("Two people share a last name; page ids would collide")

LETTER_DATE = "2026-09-23"
LEVELS, VALUES = {"A", "B", "C", "D", "F"}, {"yes", "no", "mixed", "none"}
news = {}
if args.news:
    for path in sorted(glob.glob(os.path.join(args.news, "*.json"))):
        record = json.load(open(path))
        for st in record["statements"]:
            datetime.date.fromisoformat(st["date"])
            if st["level"] not in LEVELS or not st["quote"].strip() or len(st["quote"]) > 300 or not st["url"].startswith("http"):
                raise SystemExit(f"Bad statement in {path}: {st}")
        for field in ("slowdown", "pause", "intl", "rsi"):
            if record["positions"][field]["value"] not in VALUES:
                raise SystemExit(f"Bad position in {path}: {field}")
        for st in record["statements"]:
            # Oz's ruling of 11 November 2026 (revised the same day from B): the 23 September 2026
            # letter of 17 senators is level A, whatever passage is quoted from it.
            if "cosigned_letter" in st.get("flags", []) and st["date"] == LETTER_DATE and st["level"] != "A":
                print(f"Letter ruling applied ({st['level']} -> A):", record["member"], st["url"])
                st["level"] = "A"
        news[record["bioguide"]] = record
confirmed = set()  # (link, quote) pairs whose wording the automatic check found on the linked page
if args.quote_check:
    with open(args.quote_check, newline="") as f:
        confirmed = {(r["url"], r["quote"]) for r in csv.DictReader(f) if r["result"] == "found"}

by_senator = collections.defaultdict(list)
with open(args.labels, newline="") as f:
    for row in csv.DictReader(f):
        by_senator[page_id[row["bioguide"]]].append(row)

template = open(args.template).read()
hand_grades = dict(re.findall(r'\{id:"(\w+)",bioguide:"\w+",name:"[^"]*",seat:"[^"]*",grade:"(.)"', template))
bioguide_of = {v: k for k, v in page_id.items()}


# Which ordinary AI posts are worth showing, and the quote for each (see classify/relevance_prompt.md).
picks = {}
for path in sorted(glob.glob(os.path.join(args.relevance, "*.json"))):
    for o in json.load(open(path)):
        picks[o["id"]] = o


data = {}
for senator, rows in by_senator.items():
    posts, seen_quotes = [], set()
    found = news.get(bioguide_of[senator])
    # Posts that do not address catastrophic risk (level D) are shown only when nothing stronger
    # was found anywhere for this person, so that a D record still shows what it rests on.
    nothing_stronger = (not any(r["level"] in RANK for r in rows)
                        and not (found and any(st["level"] in RANK for st in found["statements"]))
                        and hand_grades.get(senator, "D") in "D–")
    for r in rows:
        if r["level"] == "D" and nothing_stronger:
            pick = picks.get(r["url"].rsplit("/", 1)[1])
            if pick is None:
                raise SystemExit(f"No relevance decision for {r['url']}; run classify/export_relevance.py and judge the new posts")
            if not pick["show"]:
                continue  # mentions AI but says nothing of substance about it
            if not pick["quote"] or pick["quote"] not in r["text"] or len(pick["quote"]) > 300:
                raise SystemExit(f"Bad relevance quote for {r['url']}")
            r = dict(r, quote=pick["quote"])
        elif r["level"] not in RANK:
            continue
        if r["url"] in template or r["quote"] in seen_quotes:
            continue  # already cited by hand, or the same text posted twice
        seen_quotes.add(r["quote"])
        posts.append({
            "iso": r["date"], "date": show_date(r["date"]), "handle": r["handle"], "url": r["url"], "level": r["level"],
            "borderline": "boundary" in r["flags"] or "unsure" in r["flags"],
            # the API returns &amp; and similar; show them as the characters they stand for
            "quote": html.unescape(r["quote"]), "reason": r["reason"],
        })
    data[senator] = {
        "total": len(rows), "since": args.since, "posts": posts,
    }
    print(senator, len(rows), "posts,", len(posts), "passed to the page")



def draft_record(account, rows, found):
    """A first-draft record for a politician who has no hand-written one, from the labelled X posts
    and, if there is one, the news search file (`found`)."""
    count = collections.Counter(r["level"] for r in rows)
    news_count = collections.Counter(st["level"] for st in found["statements"]) if found else collections.Counter()
    # Draft grade: the highest level any post or statement reached; F only if nothing reached A, B or C;
    # D if they spoke about AI at all; otherwise no relevant statement.
    grade = next((g for g in "ABCFD" if count[g] + news_count[g]), "–")
    if not account["handle"]:
        why = "No X account was found, so no posts have been collected."
    elif not rows:
        why = "No posts matching AI-related keywords were found on their X accounts."
    else:
        why = (f"Of {len(rows)} X posts matching AI-related keywords, a language model labelled "
               f"{count['A']} at A, {count['B']} at B, {count['C']} at C and {count['D']} at D.")
    if found:
        levels = ", ".join(f"{news_count[g]} at {g}" for g in "ABCFD" if news_count[g])
        why += (f" A web search of news reports and official records found {len(found['statements'])} "
                f"statement{'s' if len(found['statements']) != 1 else ''}" + (f" ({levels})." if levels else "."))
        if found["grade_reason"]:
            why += " " + found["grade_reason"]
    pos = {}
    for field, column in POLICIES.items():
        stated = sorted((r for r in rows if r[column] != "none"), key=lambda r: r["date"], reverse=True)
        values = {r[column] for r in stated}
        value = ("none" if not values else "mixed" if {"yes", "no"} <= values or values == {"mixed"} or "mixed" in values and "yes" not in values
                 else "yes" if "yes" in values else "no")
        pos[field] = ([value, f"Stated in {len(stated)} post{'s' if len(stated) != 1 else ''} on X.",
                       [[f"X post, {show_date(r['date'])}", r["url"]] for r in stated[:3]]]
                      if stated else ["none", "None found in X posts."])
    pos["rsi"] = ["none", "None found. The X post labels do not cover this policy."]
    if found:
        for field, column in list(POLICIES.items()) + [("rsi", "rsi")]:
            n = found["positions"][column]
            if n["value"] == "none":
                pos[field][1] += " None found in the web search." if field != "rsi" else ""
                continue
            x_value, x_note, x_sources = (pos[field] + [[]])[:3]
            if x_value == "none":
                pos[field] = [n["value"], n["note"], n.get("sources", [])]
            else:  # stated in both places; if they disagree the record shows Mixed
                pos[field] = [x_value if x_value == n["value"] else "mixed", f"{n['note']} {x_note}", n.get("sources", []) + x_sources]
    stmts = []
    for st in (found["statements"] if found else []):
        checked = (1 if (st["url"], st["quote"]) in confirmed
                   else "read by a language model; not confirmed by the automatic check" if st.get("read_at_source")
                   else 0)
        stmts.append([show_date(st["date"]), st["venue"], st["quote"], st["context"], st["source_label"], st["url"],
                      checked, None, st["level"]])
    searched = "X posts and a web search of news reports and official records" if found else "X posts"
    return {
        "id": page_id[account["bioguide"]], "bioguide": account["bioguide"], "name": account["member"],
        "seat": f"{account['party']} · {STATES[account['state']]}", "grade": grade, "why": why,
        "flag": f"Machine-drafted record. The grade, positions and quotes come from a language model working from {searched}, "
                "and have not been checked by a person.",
        "pos": pos, "stmts": stmts, "record": found["record"] if found else [],
        "gaps": [] if found else ["Only X posts have been searched."],
    }


with open(args.summaries, newline="") as f:
    summaries = {r["bioguide"]: r["summary"] for r in csv.DictReader(f)}

ruled = {}
if args.grade_overrides:
    with open(args.grade_overrides, newline="") as f:
        ruled = {r["bioguide"]: r for r in csv.DictReader(f)}
    if any(r["grade"] not in LEVELS for r in ruled.values()):
        raise SystemExit("Bad grade in " + args.grade_overrides)
drafted, seen = [], set()
for account in accounts:
    b = account["bioguide"]
    if b in seen or f'bioguide:"{b}"' in template:  # one record per person; hand-written records win
        continue
    seen.add(b)
    drafted.append(draft_record(account, by_senator.get(page_id[b], []), news.get(b)))
    if b not in summaries:
        raise SystemExit(f"No summary sentence for {account['member']} ({b}) in {args.summaries}")
    drafted[-1]["why"] = summaries[b]
    if b in ruled:
        d, r = drafted[-1], ruled.pop(b)
        print(f"Grade ruling applied: {d['name']} drafted {d['grade']}, ruled {r['grade']}")
        was = "the machine draft agreed" if d["grade"] == r["grade"] else f"the machine draft was {d['grade']}"
        d["flag"] = (f"Grade {r['grade']} was set by Oz on {r['date']} ({was}). {r['reason']} "
                     + d["flag"].replace("The grade, positions and quotes come", "The positions and quotes come"))
        d["grade"] = r["grade"]
print(len(drafted), "records drafted:", " ".join(f"{d['id']}={d['grade']}" for d in drafted))
if ruled:
    raise SystemExit(f"Grade rulings for people with no drafted record: {sorted(ruled)}")
unused = set(news) - seen
if unused:
    raise SystemExit(f"News files for people not in the accounts file or with a hand-written record: {unused}")

status = {}
if args.status:
    with open(args.status, newline="") as f:
        for r in csv.DictReader(f):
            if r["status"] not in ("senator-elect", "lame duck"):
                raise SystemExit(f"Unknown status: {r}")
            status[page_id[r["bioguide"]]] = {"kind": r["status"], "note": r["note"], "label": r["source_label"], "url": r["source_url"]}

for placeholder in (PLACEHOLDER, SENATORS_PLACEHOLDER, STATUS_PLACEHOLDER, MAP_PLACEHOLDER):
    if template.count(placeholder) != 1:
        raise SystemExit(f"Template must contain exactly one line: {placeholder}")
as_js = lambda value: json.dumps(value, ensure_ascii=False).replace("</", "<\\/")
with open(args.out, "w") as f:
    f.write(template.replace(PLACEHOLDER, f"const XPOSTS = {as_js(data)};")
            .replace(SENATORS_PLACEHOLDER, f"const XSENATORS = {as_js(drafted)};")
            .replace(STATUS_PLACEHOLDER, f"const STATUS = {as_js(status)};")
            .replace(MAP_PLACEHOLDER, f"const STATE_PATHS = {open(args.map).read().strip()};"))
print("Wrote", args.out)
