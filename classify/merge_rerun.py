"""Merge the results of rerun web searches into the news search files.

Twenty Senate-side news search files recorded web searches that never ran (the shared search
budget had run out). The searches were rerun on 15 November 2026, one subagent per politician,
each writing a result file holding only what was new. This adds those results to the files in
the news folder: new statements, new bills and actions, changed positions, the searches that
ran (replacing the entries marked as not run), and a dated note.

    python3 classify/merge_rerun.py --results data/news_rerun --news data/news --date "15 November 2026"
"""
import argparse
import glob
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--results", required=True, help="Folder of result files, one per politician, named <id>.json")
parser.add_argument("--news", required=True)
parser.add_argument("--date", required=True, help="Date of the rerun, as written in the notes")
args = parser.parse_args()

MARK = f"Searches rerun on {args.date}"
for path in sorted(glob.glob(os.path.join(args.results, "*.json"))):
    result = json.load(open(path))
    target = os.path.join(args.news, os.path.basename(path))
    raw = open(target).read()
    found = json.loads(raw)
    # keep the file's own layout (the files were written by different runs) so the change stays readable
    indent = len(raw.split("\n")[1]) - len(raw.split("\n")[1].lstrip())
    if result["bioguide"] != found["bioguide"]:
        raise SystemExit(f"{path} is for {result['bioguide']}, not {found['bioguide']}")
    if MARK in found["notes"]:
        print(found["member"], "already merged; skipped")
        continue
    if result.get("searches_refused"):
        raise SystemExit(f"{path}: some searches were refused; not merging")
    old_quotes = {s["quote"] for s in found["statements"]}
    new = [s for s in result["new_statements"] if s["quote"] not in old_quotes]
    found["statements"] += new
    found["record"] += [r for r in result.get("new_record_items", []) if r not in found["record"]]
    for field, change in result.get("position_changes", {}).items():
        print(f"  {found['member']}: position {field} {found['positions'][field]['value']} -> {change['value']}")
        found["positions"][field] = change
    not_run = [s for s in found["searches"] if "NOT RUN" in s or "not run" in s]
    found["searches"] = [s for s in found["searches"] if s not in not_run] + [f"{q} (run {args.date})" for q in result["searches_run"]]
    grade_before = found["suggested_grade"]
    found["suggested_grade"], found["grade_reason"] = result["suggested_grade"], result["grade_reason"]
    found["notes"] += (f" {MARK}: {len(result['searches_run'])} ran, none refused; {len(new)} new statement{'s' if len(new) != 1 else ''}."
                       + (f" Corrections: {result['corrections']}" if result.get("corrections") else "")
                       + (f" Notes from the rerun: {result['notes']}" if result.get("notes") else ""))
    with open(target, "w") as f:
        json.dump(found, f, indent=indent or None, ensure_ascii="\\u" in raw)
        f.write("\n" if raw.endswith("\n") else "")
    print(f"{found['member']}: {len(result['searches_run'])} searches, {len(new)} new statements "
          f"({', '.join(s['level'] for s in new) or 'none'}), suggested grade {grade_before} -> {found['suggested_grade']}")
