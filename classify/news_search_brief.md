# Instructions for the news and official-record search (one politician per run)

You are researching one US senator or senator-elect for a public website that records what
politicians have said about **catastrophic risk from AI**. Your output is a first draft
that a person will review. A fabricated or misattributed quote is the main way this
project could discredit itself, so accuracy matters more than finding something.

Read `classify/rubric_prompt.md` first. Its levels (A, B, C, D, F), its six rulings and its
position definitions apply here unchanged, except that you are grading statements found in
news articles and official records rather than X posts. Do not search X; that is done
separately.

## What to search for

Statements by the politician since 1 January 2025 about: AI risk, superintelligence,
artificial general intelligence, loss of control, human extinction, AI and bioweapons, AI
safety, a pause or slowdown of AI development, an agreement with China on AI, a ban on
superintelligence or on self-improving AI. Sources to look for: their senate.gov (or
campaign) press releases, letters they signed, bills they sponsored or co-sponsored,
hearing remarks, floor speeches, interviews, op-eds and news reports.

Run at least six different web searches, including at least one restricted to their
official site if they have one, and one each on: superintelligence, extinction or
existential risk, pause or slowdown or moratorium, China agreement or treaty, and their
name with "AI safety". Two events to check specifically: the 23 September 2026 letter from
17 senators urging AI talks with China, and the "Ban Artificial Superintelligence Act"
(September 2026); say whether the politician signed or co-sponsored, only if a source
shows it.

Open the pages you rely on if you have a tool that can fetch pages. If you cannot open a
page, you may use wording seen in a search result, but mark it `"read_at_source": false`.

## Rules for quotes

- A quote must be the politician's own words (or the words of a letter they signed, with
  the flag `cosigned_letter`), copied exactly from the source, one continuous passage, at
  most 300 characters. Never write a quote from memory, never paraphrase inside a quote,
  never join passages, and do not cut a quote so that its meaning changes.
- If a news report paraphrases them, do not turn the paraphrase into a quote. Leave it
  out of `statements` and mention it in `notes`.
- Make sure the statement is by this person and not someone with a similar name.
- Every statement needs a working link to the page where you saw the wording, and the
  date the statement was made (not the date you found it).
- Finding nothing is a valid and useful result. Do not stretch weak material.

## Extra position, not in the rubric file

- `rsi`: a ban on self-improving AI: a ban on AI systems that improve themselves or carry
  out AI research without human direction (recursive self-improvement). A ban on
  superintelligence alone does not count.

For every position, "no" requires a statement against the policy; otherwise "none".
Co-sponsoring a bill or signing a letter that calls for the policy counts as "yes"; say
which in the note.

## Output

Write one JSON file to the path you are given, and nothing else in the project.

    {"bioguide": "...", "member": "...",
     "searches": ["each search query you ran"],
     "statements": [
       {"date": "YYYY-MM-DD", "venue": "e.g. Senate floor speech, CNN interview, press release",
        "quote": "exact words", "context": "one plain sentence on what was being discussed",
        "source_label": "e.g. Senate press release, Axios", "url": "https://...",
        "read_at_source": true, "level": "A|B|C|D|F", "flags": [],
        "reason": "one plain sentence explaining the level"}],
     "positions": {
       "slowdown": {"value": "yes|no|mixed|none", "note": "plain sentence", "sources": [["label", "url"]]},
       "pause": {...}, "intl": {...}, "rsi": {...}},
     "record": [["bill, letter or action in one sentence", "source label and date", "url"]],
     "suggested_grade": "A|B|C|D|F|none", "grade_reason": "one or two plain sentences",
     "notes": "anything uncertain, paraphrases you left out, pages you could not open"}

Include every A, B, C or F statement you find (at most eight, the strongest and most
varied). Include D statements (at most three) only if they are the politician's most
substantial remarks on AI. `suggested_grade` is the highest level among the statements,
except F only if nothing reached A, B or C; "none" if you found nothing about AI at all.

When finished, reply with three lines: the suggested grade, the number of statements by
level, and anything a reviewer must know.
