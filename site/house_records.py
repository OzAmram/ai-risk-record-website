"""Draft one record per House member for the site, from the news search files, the catalogue of
co-signed letters and (if given) the labelled X posts. Writes a JSON list that site/build.py
adds to the page with --house.

    python3 site/house_records.py --roster data/house/roster.csv --news data/news_house --letters data/house/letters.json --letter-levels data/house/letter_levels.csv --quote-check data/news_house_quote_check.csv --labels data/house/classify/review_queue.csv --elect data/house/members_elect.csv --leaving data/house/not_returning.csv --out site/house_records.json

How the draft grade is worked out (Oz's rulings of 11 and 12 November 2026, applied by rule here;
for senators they were applied by hand):
- Statements are the member's own (news search and X posts) plus letters they co-signed.
- If there is any statement from 2026, only 2026 statements count.
- The grade is the highest of A, B, C reached. Statements about misuse of AI by people only are C.
- A dismissive (F) statement lowers the grade one letter, unless the grade is already C only
  because of misuse-only statements.
- With nothing at A, B or C: F if there is a dismissive statement, D if they have spoken about AI,
  otherwise no statement found.
"""
import argparse
import collections
import csv
import datetime
import html
import json
import os
import unicodedata

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
SENTENCE = {
    "A": "has acknowledged that AI could threaten human survival or escape human control.",
    "B": "has acknowledged catastrophic risk from AI, without describing it as a threat of extinction.",
    "C": "has acknowledged serious risks from AI in general terms.",
    "D": "has spoken about AI but has not acknowledged catastrophic risk from it.",
    "F": "has dismissed warnings of catastrophic risk from AI.",
    "–": "has no statement about AI that the searches could find.",
}
LOWER = {"A": "B", "B": "C", "C": "D"}

parser = argparse.ArgumentParser()
parser.add_argument("--roster", required=True)
parser.add_argument("--news", required=True, help="Folder of news search files, one per member")
parser.add_argument("--letters", required=True, help="Catalogue of co-signed letters")
parser.add_argument("--letter-levels", required=True, help="CSV: letter id, level, quote number, ruled by")
parser.add_argument("--quote-check", help="Output of classify/check_news_quotes.py for the House files")
parser.add_argument("--quote-review", help="Results of the second check of quotes the automatic check missed (data/quote_review/results.csv)")
parser.add_argument("--labels", help="Labelled X posts (output of classify/merge.py). Left out: records use news and letters only")
parser.add_argument("--elect", help="CSV of representatives-elect written by data/house/merge_elections.py")
parser.add_argument("--leaving", help="CSV of sitting members not among the 2026 winners")
parser.add_argument("--summaries", help="CSV (bioguide, summary, grade) of written sentences shown after the grade, from data/house/merge_summaries.py. "
                    "Used only while the record's grade is still the grade the sentence was written for")
parser.add_argument("--election", help="Table of 2026 House results (data/house/election_2026.csv); gives each returning member the district they won")
parser.add_argument("--out", required=True)
args = parser.parse_args()


def show_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def slug(name):
    plain = "".join(c for c in unicodedata.normalize("NFD", name.lower()) if c.isalnum() or c == " ")
    return "h-" + "-".join(plain.split())


with open(args.roster, newline="") as f:
    roster = list(csv.DictReader(f))
with open(args.letter_levels, newline="") as f:
    letter_level = {r["letter_id"]: r for r in csv.DictReader(f)}
letters = json.load(open(args.letters))
letters = letters["letters"] if isinstance(letters, dict) else letters
signed = collections.defaultdict(list)
for letter in letters:
    if letter["id"] not in letter_level:
        raise SystemExit(f"No level for letter {letter['id']} in {args.letter_levels}")
    for signer in letter["signers"]:
        if signer["bioguide"]:
            signed[signer["bioguide"]].append(letter)
confirmed = set()
if args.quote_check:
    with open(args.quote_check, newline="") as f:
        confirmed = {(r["url"], r["quote"]) for r in csv.DictReader(f) if r["result"] == "found"}
by_person = set()  # quotes Oz opened and confirmed himself
reviewed = set()  # quotes a subagent found in the downloaded page text after the automatic check missed them
if args.quote_review:
    with open(args.quote_review, newline="") as f:
        review_rows = list(csv.DictReader(f))
    reviewed = {(r["url"], r["quote"]) for r in review_rows if r["result"] == "confirmed"}
    by_person = {(r["url"], r["quote"]) for r in review_rows if r["result"] == "confirmed_by_person"}
posts = collections.defaultdict(list)
if args.labels:
    with open(args.labels, newline="") as f:
        for row in csv.DictReader(f):
            posts[row["bioguide"]].append(row)
else:
    print("No X post labels given: records are drafted from news searches and letters only")

status = {}  # bioguide or member-elect id -> mark shown beside the name
if args.leaving:
    with open(args.leaving, newline="") as f:
        for r in csv.DictReader(f):
            if not r["note"]:  # members from states with an uncalled race are left unmarked
                status[r["bioguide"]] = {"kind": "lame duck", "label": "", "url": "",
                                         "note": "Not among the winners of the 3 November 2026 House elections. Leaves the House on 3 January 2027."}
if args.elect:
    with open(args.elect, newline="") as f:
        for r in csv.DictReader(f):
            roster.append({"bioguide": r["id"], "member": r["winner"], "last_name": r["id"].split("-")[-1].title(), "party": r["party"],
                           "state": r["state"], "district": r["district"], "elect": True})
            status[r["id"]] = {"kind": "representative-elect", "label": r["source_label"], "url": r["source_url"],
                               "note": f"Elected 3 November 2026; takes office 3 January 2027. {r['previous']} {r['background']}".strip()}

won = {}  # bioguide of a returning member -> the district they won in November 2026, in the form used in "seat"
if args.election:
    with open(args.election, newline="") as f:
        for r in csv.DictReader(f):
            if r["sitting_bioguide"] and r["status"] == "called":
                won[r["sitting_bioguide"]] = f"{STATES[r['state']]}, " + ("at large" if r["district"] == "0" else f"district {r['district']}")

summaries = {}
if args.summaries:
    with open(args.summaries, newline="") as f:
        summaries = {r["bioguide"]: r for r in csv.DictReader(f)}
stale = []  # people whose grade has changed since their sentence was written

records, grades, missing = [], collections.Counter(), []
for member in roster:
    b = member["bioguide"]
    path = os.path.join(args.news, b + ".json")
    if not os.path.exists(path):
        missing.append(member["member"])  # the six senators-elect, whose records are on the Senate side
        continue
    found = json.load(open(path))
    items, stmts = [], []  # items: (date, level, misuse only?, from a co-signed letter?)
    for st in found["statements"]:
        flags = st.get("flags", [])
        items.append((st["date"], st["level"], "misuse_only" in flags, "cosigned_letter" in flags))
        checked = (1 if (st["url"], st["quote"]) in confirmed
                   else "checked against the source by a person" if (st["url"], st["quote"]) in by_person
                   else "found on the page by a second check run by a language model" if (st["url"], st["quote"]) in reviewed
                   else "read by a language model; not confirmed by the automatic check" if st.get("read_at_source") else 0)
        stmts.append([show_date(st["date"]), st["venue"], st["quote"], st["context"], st["source_label"], st["url"], checked, None, st["level"]])
    for letter in signed[b]:
        ruling = letter_level[letter["id"]]
        quote = letter["quotes"][int(ruling["quote_number"]) - 1]
        items.append((letter["date"], ruling["level"], False, True))
        stmts.append([show_date(letter["date"]), f"Letter to {letter['addressed_to']}, co-signed with {len(letter['signers']) - 1} other members",
                      quote["text"], letter["summary"], "Letter text", quote["source_url"],
                      "wording found on the source page", None, ruling["level"]])
    seen = set()
    for p in posts[b]:
        if p["level"] == "off_topic":
            continue
        items.append((p["date"], p["level"], "misuse_only" in p["flags"], False))
        if p["level"] in "ABCF" and p["quote"] not in seen:
            seen.add(p["quote"])
            stmts.append([show_date(p["date"]), "X post, @" + p["handle"], html.unescape(p["quote"]), p["reason"], "Post on X", p["url"],
                          "chosen by a language model", None, p["level"]])

    recent = [i for i in items if i[0] >= "2026"]
    pool = recent or items
    levels = {i[1] for i in pool}
    top = next((g for g in "ABC" if g in levels), None)
    notes = []
    if top:
        at_top = [i for i in pool if i[1] == top]
        misuse_c = top == "C" and all(i[2] for i in at_top)
        grade = top
        if "F" in levels and not misuse_c:
            grade = LOWER[top]
            notes.append(f"Lowered one letter from {top} because of a dismissive statement.")
        if all(i[3] for i in at_top):
            notes.append("This rests on a co-signed letter, not on the member's own words.")
        if misuse_c:
            notes.append("The only catastrophic risk named is misuse of AI by people.")
    elif "F" in levels:
        grade = "F"
    elif pool or found["suggested_grade"] == "D":
        grade = "D"
    else:
        grade = "–"
    if recent and len(recent) < len(items) and any(i[1] in "ABC" for i in items if i[0] < "2026") and (not top or "ABC".index(top) > min("ABC".index(i[1]) for i in items if i[1] in "ABC")):
        notes.append("A stronger statement from 2025 was outweighed by 2026 statements.")
    grades[grade] += 1

    pos = {}
    for field, column in (("slow", "slowdown"), ("pause", "pause"), ("intl", "intl"), ("rsi", "rsi")):
        n = found["positions"][column]
        pos[field] = [n["value"], n["note"], n.get("sources", [])] if n["value"] != "none" else ["none", "None found."]
        stated = sorted((p for p in posts[b] if p.get(column, "none") != "none"), key=lambda p: p["date"], reverse=True) if column != "rsi" else []
        if stated:
            values = {p[column] for p in stated}
            x_value = "mixed" if {"yes", "no"} <= values or "mixed" in values else values.pop()
            x_note = f"Stated in {len(stated)} post{'s' if len(stated) != 1 else ''} on X."
            x_sources = [[f"X post, {show_date(p['date'])}", p["url"]] for p in stated[:3]]
            if pos[field][0] == "none":
                pos[field] = [x_value, x_note, x_sources]
            else:  # stated in both places; if they disagree the record shows Mixed
                pos[field] = [pos[field][0] if pos[field][0] == x_value else "mixed", f"{pos[field][1]} {x_note}", pos[field][2] + x_sources]

    # A co-signed letter that Oz has ruled counts as a policy position. The member's own stated position is kept if there is one.
    for letter in signed[b]:
        ruling = letter_level[letter["id"]]
        if ruling.get("position_field"):
            source = [f"Letter, {show_date(letter['date'])}", letter["url"]]
            current = pos[ruling["position_field"]]
            if current[0] == "none":
                pos[ruling["position_field"]] = [ruling["position_value"], ruling["position_note"], [source]]
            else:
                pos[ruling["position_field"]] = [current[0], f"{current[1]} Also co-signed a letter urging talks with China on AI safety.", current[2] + [source]]

    district = "at large" if member["district"] == "0" else f"district {member['district']}"
    searched = "a web search of news reports and official records, co-signed letters" + (" and X posts" if args.labels else "")
    records.append({
        "id": slug(member["member"]), "bioguide": b, "name": member["member"], "chamber": "house",
        "seat": f"{member['party']} · {STATES[member['state']]}, {district}", "grade": grade,
        "why": f"{'Representative-elect ' + member['member'] if member.get('elect') else 'Representative ' + member['last_name']} {SENTENCE[grade]}" + "".join(" " + n for n in notes),
        "flag": f"The grade, positions and quotes come from a language model working from {searched}, "
                "and have been spot-checked by a person. The grade is worked out by rule from the statements found; "
                "the levels given to co-signed House letters were set by a human reviewer on 15 November 2026.",
        "pos": pos, "stmts": stmts, "record": found.get("record", []), "gaps": [],
    })
    records[-1]["posts"] = len(posts[b])  # X posts collected for this member, for the total on the methodology page
    if b in summaries:
        if summaries[b]["grade"] == grade:
            records[-1]["why"] = summaries[b]["summary"]
        else:
            stale.append(member["member"])  # keeps the sentence written by rule
    if b in status:
        records[-1]["status"] = status[b]
    if b in won:
        records[-1]["next"] = won[b]
if len({r["id"] for r in records}) != len(records):
    raise SystemExit("Two House members would get the same page id")
with open(args.out, "w") as f:
    json.dump(records, f, ensure_ascii=False)
print(len(records), "House records written to", args.out, "| grades:", " ".join(f"{g} {grades[g]}" for g in "ABCDF–"))
if args.summaries:
    print(sum(1 for r in records if r["bioguide"] in summaries) - len(stale), "records use a written summary;", len(stale), "have a summary written for a different grade and use the rule sentence:", ", ".join(stale))
print("Not included (no file in the House news folder):", ", ".join(missing))
