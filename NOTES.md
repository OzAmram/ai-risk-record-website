# Project notes

## 2026-11-11: X API setup and pilot account list

**Goal:** get X API access working and build the account list for the five pilot senators.

**What was done**
- Created `.gitignore` (excludes `.env`, databases, `data/raw/`), `.env.example`, and ran `git init`. Nothing committed yet.
- Oz created the X developer app and token (in `.env` as `X_BEARER_TOKEN`). First test failed with HTTP 403 `client-not-enrolled`: the app was only in a project labelled "Ads / MCP access only". Adding the app to the default project fixed it; the same token then worked.
- Test request: recent search, `from:SenSanders (AI OR "artificial intelligence")`, 10 results maximum. Returned 1 post. Raw responses in `data/raw/token_check_*.json`.
- Built `data/accounts.csv`: 10 accounts (official plus personal or campaign) for Sanders, Blumenthal, Hawley, Cruz, Slotkin.
  - Official handles and user ids from `unitedstates/congress-legislators` (`legislators-social-media`, last changed 2026-10-24, commit 489900c).
  - Personal or campaign handles were proposed from the assistant's memory, then each confirmed to exist through the X API user lookup (`/2/users/by`). Raw responses in `data/raw/user_lookup_*.json`.

**Results**
- The token works for recent search and user lookup.
- The repository's handle for Slotkin (`RepSlotkin`) is out of date: that handle no longer exists. The same user id now belongs to `@SenatorSlotkin`. So the repository's user ids are more reliable than its handles; resolve handles by id when building the full list.
- Cost: the console showed a total of $0.01 after the first one-post search (reported rate would be $0.005; possibly rounded up). Not yet rechecked after the user lookups (12 users looked up, 1 of them twice).

**Decisions by Oz**
- Backfill through the X API only to January 2025, not January 2023.
- For earlier statements, and as a cross-check, use the quotes list at https://theaipn.org/issue/quotes/ . Not yet read or evaluated.

**Open questions / known problems**
- Full-archive search availability and price on pay-per-use: still not confirmed in the console. X's docs say it is available with a 1,024-character query limit.
- Spend cap: not confirmed as set.
- X's terms on storing and displaying post text: not yet read.
- `@DickBlumenthal` is a small campaign account (4,906 followers, 320 posts); it exists but may be inactive.
- The congress-legislators repository lists official accounts only. Personal and campaign accounts for the other 95 senators need another source.
- The six rubric questions in `HANDOFF.md` are still open.

**Next steps**
1. Check console usage after the lookups to pin down per-post and per-user prices.
2. Write `collector/search.py` and `collector/pilot.py`; run the seven-day pilot on these 10 accounts.
3. Review theaipn.org quotes list as a source for pre-2025 statements.

## 2026-11-11 (later): seven-day pilot on the ten accounts

**Goal:** run the pilot from `HANDOFF.md`: five senators, last seven days, and compare cost with the estimate.

**What was done**
- Wrote `collector/search.py` (standard library only). One command does the pilot, so there is no separate `pilot.py`.
- Command (no git commit exists yet, so the code state is the working folder as of this date):
  `set -a; . ./.env; set +a; python3 collector/search.py --accounts data/accounts.csv --db data/posts.sqlite`
- Output: `data/posts.sqlite` (table `posts`), raw response `data/raw/search_*_q0_p0.json`.
- Choices made: reposts are excluded (`-is:retweet`); replies and quote posts are kept. "frontier AI" and "AI safety" dropped from the keyword list because bare `AI` covers them; "data centers" (plural) added.

**Results**
- All ten accounts and nine keywords fit in one query of 347 characters (limit used: 512).
- 6 posts returned for roughly 4 to 11 November 2026: Sanders 3 (two official, one personal), Cruz 1, Slotkin 1, Hawley 1, Blumenthal 0.
- Five of six are about data centers (moratorium, electricity bills). Only one touches the rubric: @SenSanders, 4 Nov, "threatening humanity's future". Cruz's match is a passing mention inside a long election post.
- Long posts come back in full through the `note_tweet` field (checked on the Cruz post).
- Expected charge at the reported $0.005 per post: about $0.03. Actual charge not yet checked in the console.
- Caveat: this was the week after the midterm election, so volume and topics may not be typical. Six posts is too few to estimate a monthly rate.

**Open questions / known problems**
- Not checked whether the search missed AI posts (for example ones that say "A.I." or only name a product). Would need a manual look at the accounts' timelines.
- Console questions still open: actual charges, full-archive availability and price, spend cap.

**Next steps**
1. Oz checks console usage (expected roughly: 7 posts read, 13 user lookups in total today).
2. If full-archive search is available, test it on these ten accounts for one past month before the backfill to January 2025.
3. Commit the work so later results can cite a commit.

## 2026-11-11 (later still): one-month backfill on the ten accounts

**Goal:** test full-archive search by collecting the last month for the pilot accounts.

**What was done**
- Command (still no git commit):
  `set -a; . ./.env; set +a; python3 collector/search.py --accounts data/accounts.csv --db data/posts.sqlite --endpoint all --start-time 2026-10-11T00:00:00Z --max-query-len 1024 --max-posts 500`
- Output: same database `data/posts.sqlite`; raw response in `data/raw/search_*_q0_p0.json` (second file).

**Results**
- Full-archive search works on this pay-per-use account. This settles the handoff's main unknown about availability; its price is still unknown.
- 28 posts from 11 October to 11 November 2026 (the 6 pilot posts plus 22 new): SenSanders 14, BernieSanders 9, HawleyMO 2, tedcruz 1, SenatorSlotkin 1, SenBlumenthal 1.
- Several Sanders posts are directly relevant to the rubric (13 Oct on advanced AI and superintelligence; 14 Oct "could threaten the human race"; 16 Oct on humans remaining in control; "Pause AI NOW" on 22 Oct and 3 Nov). Not yet classified or checked by a person.
- Two pairs of Sanders posts have the same text under different post ids (15 Oct and 22 Oct). Probably re-posted with a different attachment; not investigated.
- Cost before this run, per Oz: console total $0.13 after 1 + 6 posts and 13 user lookups (12 distinct users). That does not match the reported rates exactly ($0.005 per post, $0.010 per user would give about $0.15 to $0.17). Possible explanations: usage shown with a delay, or repeat reads on the same day not billed. Unresolved.
- Spend cap, per Oz: $65.

**Next steps**
1. Oz reads the console total again. This run had no user lookups, so the increase over $0.13 is the cost of 22 new posts (28 if repeats are billed) through full-archive search.
2. Decide the next scale step: backfill these ten accounts to January 2025, or build the full Senate account list first.

## 2026-11-11 (evening): backfill of the ten accounts to January 2025

**Goal:** collect all keyword-matching posts from the ten pilot accounts since 1 January 2025.

**What was done**
- Oz chose not to wait for the console total to update before running this.
- Command (still no git commit):
  `set -a; . ./.env; set +a; python3 collector/search.py --accounts data/accounts.csv --db data/posts.sqlite --endpoint all --start-time 2025-01-01T00:00:00Z --end-time 2026-10-11T00:00:00Z --max-query-len 1024 --max-posts 2000`
- The end time stops where the one-month run started, to avoid reading the same posts twice.
- Output: `data/posts.sqlite`; raw responses `data/raw/search_*_q0_p0.json` to `_p5.json` (six pages).

**Results**
- 595 posts returned in this run. The database now holds 623 posts, 9 January 2025 to 11 November 2026.
- By account: HawleyMO 140, SenSanders 130, BernieSanders 120, SenBlumenthal 56, SenTedCruz 52, SenHawleyPress 45, tedcruz 40, SenatorSlotkin 39, ElissaSlotkin 1, DickBlumenthal 0.
- By month: under 20 per month until mid-2025, 25 to 47 per month from July 2025, with a peak of 80 in September 2026. January 2026 has only 9, which stands out against 32 the month before and 29 the month after; not investigated.
- Expected cost at the reported $0.005 per post: about $3.00 for this run, about $3.10 for all posts read today. Actual cost not confirmed; the console total had not updated.
- Nothing is classified yet. These are keyword matches, and many will be off-topic (the pilot month was mostly data centers).

**Open questions / known problems**
- Actual price per post for full-archive search.
- Whether the keyword search misses relevant posts.
- @SenatorSlotkin's count covers her House-era posts too, since the account was renamed from @RepSlotkin and kept its id. Her Senate term began in January 2025, so this should not matter for this date range.

**Next steps**
1. Oz checks the console total once it updates.
2. Commit the work.
3. Either classify these 623 posts against the rubric (handoff step 7) or build the full Senate account list (step 3).

## 2026-11-11 (night): first-pass labelling of the 623 posts

**Goal:** label every collected post against the rubric with a language model, and produce a file for a person to review.

**What was done**
- First commit made before this work: `7491721`. The labelling code below is not yet committed.
- `classify/rubric_prompt.md`: the instructions given to each labeller. Adds two bins the rubric lacks (`other_ai`: about AI, nothing on risk; `off_topic`), position fields, flags for the open rubric questions, and an exact-quote requirement.
- `python3 classify/export_chunks.py --db data/posts.sqlite --accounts data/accounts.csv --out data/classify/input --chunk-size 65` wrote 11 chunk files (Sanders 4, Hawley 3, Cruz 2, Blumenthal 1, Slotkin 1).
- 11 Claude subagents (one per chunk, model Fable 5.2, launched from the Claude Code session, not from a script) each labelled one chunk into `data/classify/output/`. This step is not reproducible by command; rerunning would give somewhat different labels.
- `python3 classify/merge.py --input data/classify/input --output data/classify/output --review data/classify/review_queue.csv` checked and merged them. All checks passed: every post labelled exactly once, all values allowed, every quote an exact piece of its post.
- `data/classify/` is excluded from git because it contains post text.

**Results (first-pass labels, not reviewed by a person)**

| Senator | A | B | C | D | F | About AI, no risk | Off topic | Total |
|---|---|---|---|---|---|---|---|---|
| Sanders | 14 | 28 | 31 | 108 | 0 | 51 | 18 | 250 |
| Blumenthal | 0 | 0 | 11 | 36 | 0 | 7 | 2 | 56 |
| Hawley | 0 | 2 | 16 | 149 | 0 | 17 | 1 | 185 |
| Cruz | 0 | 2 | 3 | 26 | 0 | 54 | 7 | 92 |
| Slotkin | 0 | 0 | 8 | 7 | 0 | 19 | 6 | 40 |
| All | 14 | 32 | 69 | 326 | 0 | 148 | 34 | 623 |

- Positions: only Sanders has any. Pause: 24 yes, 9 mixed. Slowdown: 37 yes, 3 mixed. International agreement: 12 yes.
- Flags: bill or action 150, boundary 119, needs media 80, unsure 44, relayed warning 12, co-signed letter 2. 307 of 623 posts carry at least one flag.
- Highest level per senator from X posts alone: Sanders A, Hawley B, Cruz B, Blumenthal C, Slotkin C. The prototype's drafts were Sanders A, Blumenthal B, Hawley B, Cruz C, Slotkin C, but those used other sources too.

**How much to trust this**
- One labeller per post, no second pass, so there is no measure of how consistent the labels are.
- The instruction "when between two levels, choose the one nearer A" pushes labels upward; 119 posts were boundary cases.
- Labellers were not consistent with each other on some rules: one Sanders chunk gave A or B to relayed warnings that he endorsed (the instructions said C); one chunk set slowdown equal to pause throughout while others did not; "threatens humanity" wording went to B in some chunks.
- 80 posts depend on a video, image or link the labeller could not see.

**New rubric questions raised by the data** (in addition to the six in `HANDOFF.md`)
1. Military AI without human oversight (autonomous weapons, nuclear launch): C or D? Decides 6 of Slotkin's 8 C labels.
2. "Rogue AI" posts about agents escaping or hacking (Hawley, Blumenthal): C or D, or B?
3. AI as a tool of surveillance and control if China wins the race (Cruz): C, or not about AI risk?
4. "AI must benefit everyone, not just billionaires" with no named harm (21 Sanders posts): D, or not about risk?
5. "Threatens humanity" or "the future of humanity" without extinction wording: A, B or C?
6. A relayed warning that the senator endorses in his own words: still C?

**Next steps**
1. Oz reviews `data/classify/review_queue.csv`, starting with the 115 posts labelled A, B or C, and fills in `reviewer_level` and `reviewer_notes`.
2. Decide the rubric questions, update `classify/rubric_prompt.md`, and relabel.
3. Commit the labelling code.

## 2026-11-11 (late night): rubric v0.2 and relabelling

**Goal:** apply Oz's rulings on the six rubric questions and his rewording of level D, then relabel all 623 posts.

**Decisions by Oz**
1. Military AI without human oversight is C.
2. "Rogue AI" is not a rubric category; grade by the harm named. Cybercrime alone is D.
3. AI as a tool of surveillance or control if China wins the race is not AI safety risk.
4. "AI must benefit everyone, not just billionaires" is not about AI risk.
5. "Threatens the future of humanity" is A.
6. A relayed warning the politician endorses counts as their own.
7. D is reworded to "catastrophic AI risk not acknowledged", and the methodology must say plainly that the project tracks catastrophic risk only and does not discount other harms.

**What was done**
- `xrisk-record.html`: D reworded, scope paragraph added to the methodology page, label changed to draft v0.2. Not opened in a browser to check.
- `HANDOFF.md`: rubric v0.2, scope paragraph, list of rulings.
- `classify/rubric_prompt.md` rewritten as v0.2. Choices made by the assistant, for Oz to confirm:
  - D has a second sentence, "Has spoken about AI, but not about catastrophic risk", to separate it from "no relevant statement found".
  - At post level the old "about AI, nothing on risk" bin is merged into D.
  - Rogue AI with no stated consequence is D with a boundary flag; with a general threat named (national security, public safety) it is C.
  - Relayed warnings without endorsement stay C.
  - The "choose the level nearer A" rule was removed; labellers pick the best-supported level.
  - A call to pause AI for safety reasons also counts as yes on slowdown.
- `classify/merge.py`: allowed levels updated to match; a quote is now required for A, B, C and F only (D no longer needs one, since it records an absence).
- First-pass labels moved to `data/classify/output_v1/` and `data/classify/review_queue_v1.csv`.
- 11 new Claude subagents (Fable 5.2) relabelled all chunks into `data/classify/output/`; then
  `python3 classify/merge.py --input data/classify/input --output data/classify/output --review data/classify/review_queue.csv`. All checks passed.

**Results (rubric v0.2, not reviewed by a person)**

| Senator | A | B | C | D | F | Off topic | Total |
|---|---|---|---|---|---|---|---|
| Sanders | 30 | 11 | 20 | 181 | 0 | 8 | 250 |
| Blumenthal | 0 | 0 | 4 | 50 | 0 | 2 | 56 |
| Hawley | 0 | 2 | 4 | 177 | 0 | 2 | 185 |
| Cruz | 0 | 2 | 0 | 80 | 0 | 10 | 92 |
| Slotkin | 0 | 0 | 6 | 27 | 0 | 7 | 40 |
| All | 30 | 15 | 34 | 515 | 0 | 29 | 623 |

- Highest level per senator from X posts alone: Sanders A, Hawley B, Cruz B, Blumenthal C, Slotkin C. Same as the first pass.
- Positions: only Sanders. Pause 21 yes, 9 mixed. Slowdown 32 yes. International agreement 10 yes.
- Flags: bill or action 84, boundary 83, needs media 40, relayed warning 26, unsure 4.
- 79 posts are A, B or C; 124 are A, B, C or flagged boundary or unsure.
- Compared with the first pass (old "about AI, nothing on risk" counted as D): 72 of 623 labels changed. C to D 33, B to A 16, off topic to D 11, D to off topic 5, and 7 others. Most of these follow from the rulings and the removal of the upward tilt, so this is not a clean measure of labeller consistency. The 16 moves between D and off topic are not explained by any ruling and do show labeller disagreement on passing mentions.

**Open questions / known problems**
- Still one labeller per post. Labellers still differ on some points: whether a pause through a treaty with China is "yes" or "mixed"; what counts as endorsing a relayed warning (two Sanders posts quoting Hinton and rebutting Musk were kept at C).
- Hawley's two B labels rest on an op-ed headline; the article was not read.
- Cruz: two posts attributing AI fears to Chinese-funded messaging were kept at D, not F.
- Original handoff questions 2 to 6 (bills and actions, co-signed letters, B/C boundary, staleness, quote length) are still open.
- Console cost for today's collection is still unconfirmed.
- The labelling code and rubric changes are not committed.

**Next steps**
1. Oz reviews `data/classify/review_queue.csv`: the 79 A, B and C posts first, then the 45 other flagged ones.
2. Commit.
3. Then either build the full Senate account list, or review theaipn.org quotes for pre-2025 statements.

## 2026-11-11 (end of day): third policy renamed; review page built

**Goal:** rename the third policy, and build senator pages that include the most relevant X quotes, so Oz reviews pages instead of all 623 labels.

**Decisions by Oz**
- The third policy is "International coordination with China on pacing/pausing". The word "adversaries" is not to be used.
- Oz will not review every label. He reviews the senator pages.

**What was done**
- Third policy renamed in `xrisk-record.html`, `HANDOFF.md` and `classify/rubric_prompt.md`. Wording used: "International coordination with China on pacing or pausing", defined as coordinating with China on the pace of frontier AI development, including a mutual slowdown or pause, through an agreement, treaty or direct talks.
- `xrisk-record.html` (the template) gained a "Posts on X" section on each senator page and a sentence about it in the methodology. The section is empty until the build fills it.
- New `site/build.py`. Command:
  `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --max-posts 10`
- Output: `site/index.html` (excluded from git as a generated file).
- Selection rule for "most relevant": posts labelled A, B, C or F; highest level first, then labels not flagged borderline or unsure, then newest; identical quotes shown once; at most 10 per senator.
- Checked by running the page's code in macOS's built-in JavaScript engine: all five senator pages, the index and the methodology page render, with 10, 4, 5, 2 and 6 posts shown for Sanders, Blumenthal, Hawley, Cruz and Slotkin. Not checked visually in a browser by the assistant.

**Known problems**
- The hand-written grades, position rows and "For review" notes on each page were not changed. They can now disagree with the X posts beside them: Cruz is drafted C but has two posts labelled B; Blumenthal is drafted B but his X posts reach only C.
- The hand-written text on the pages predates Oz's rulings and still describes some settled questions as open.
- The `intl` labels on posts were assigned under the old wording ("safety agreement that includes China"). Three Sanders posts tagged yes are about cooperation with China generally, not pacing or pausing.
- Sanders's ten shown posts are all from September and October 2026 because of the newest-first rule; his earliest A-level post (December 2025) is not shown.
- X's terms on displaying post text are still unread. The page is a local draft.

**Next steps**
1. Oz reviews `site/index.html`.
2. Update grades, position rows and notes on each page from the review.
3. Commit.

## 2026-11-11 (final entry of the day): one statement list, portraits

**Goal:** per Oz: no separate sections for article-sourced statements and X posts; every statement links to X and/or the news source; no letter grade per statement; a portrait on each senator's page.

**What was done**
- `xrisk-record.html`: the separate "Posts on X" section is gone. Hand-written statements and X posts are merged into one "Statements" list, newest first. Each shows its sources with a tier tag; x.com links are tagged "original post". Per-statement levels, flags and position tags are no longer shown. X posts picked by the build are marked "chosen by a language model".
- Two hand-written statements that cited X posts through news reports were matched to the collected posts and the wording checked against the API text:
  - Sanders, 12 Sep 2026: now links to both Newsweek and the post, marked "read at source". His two position rows that cited the Newsweek report now cite the post.
  - Cruz, 9 Sep 2026 ("We need guardrails. But America needs to lead."): the hand-written entry and its BizPac Review source were removed. The same post now appears through the build with the quote the labeller chose (legislation on catastrophic biological or nuclear risks).
- Portraits: `sh site/fetch_photos.sh` downloads official congressional portraits (public domain, from the unitedstates/images collection, keyed by Bioguide ID) to `site/img/`. All five downloaded. The assistant did not look at the images.
- `site/build.py`: skips posts already linked by hand in the template; no longer writes levels, flags or positions into the page. Selection rule unchanged. Command unchanged:
  `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --max-posts 10`
- Checked with macOS's JavaScript engine: all pages render; statement counts are Sanders 15, Blumenthal 7, Hawley 8, Cruz 5, Slotkin 9; each page has a portrait tag. Not checked visually by the assistant.

**Known problems**
- The context line under each model-chosen X post is the labeller's one-sentence reason. Some refer to rubric levels ("without the extinction framing") and should be rewritten as plain context after review.
- Grades, position rows and "For review" notes are still the original hand-written drafts (see previous entry).
- Portraits only load from `site/index.html`; opening the template `xrisk-record.html` directly shows no portrait.

**Next steps**
1. Oz reviews `site/index.html` and gives grade and position changes.
2. Commit (nothing since `7491721` is committed).

## 2026-11-11 (addendum): five statements per senator

**Goal:** per Oz: show at most five quotes per senator, the highest rated, also chosen for diversity.

**What was done**
- Assumption: five in total per senator, across hand-collected statements and X posts together.
- `xrisk-record.html`: `statements()` now picks the five. Rule: highest rubric level first (A and F rank together, then B, C, D). Among statements at the same level it prefers the one least like those already picked (overlap in wording, same month, same kind of source: X or not), then the newest. A quote sharing more than 60% of its words with a picked one is skipped. Model labels flagged borderline are slightly disfavoured.
- To rank hand-collected statements with X posts, the assistant assigned each of the 17 a level under rubric v0.2 (stored as the ninth item of each statement in the template; not shown on the page). These are the assistant's judgments and need Oz's check:
  - Sanders: CBS "greater than nuclear weapons" B; 12 Sep X post A; 3 Sep press release B; 11 May statement C; 29 Apr panel A.
  - Blumenthal: 23 Sep co-signed letter A; CNBC "losing control" B; 9 Sep letter to Altman D.
  - Hawley: hearing "I don't know if that's true" C; letter to Altman C; op-ed D.
  - Cruz: "killer robots" C; "China is not going to stop" D; summits D.
  - Slotkin: podcast C; press release C; "tech arms race" speech D.
- `site/build.py` now passes every X post labelled A, B, C or F to the page (the page picks); `--max-posts` removed. Command:
  `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025"`
- Checked with macOS's JavaScript engine: every page shows five statements and renders without errors.

**Problem found and fixed by hand**
- A Slotkin quote chosen by the labeller cut off the start of a sentence and reversed its meaning: "we should allow AI systems to get into war and kill people without a human being overseeing that". The post says "The average person does not think we should allow...". The quote in `data/classify/output/S001208_1.json` was edited by hand to the full sentence, then merge and build were rerun.
- The exact-quote check cannot catch this kind of error. Other excerpts may have the same problem; the 79 A, B and C quotes have not been checked for it.

**Known problems**
- Level-first selection drops some informative lower-level statements, for example Sanders's "greater than nuclear weapons" interview (B) and his 12 Sep treaty post.
- Cruz has only three statements above D, so two D-level hand-collected statements fill his five.

## 2026-11-11 (after Oz's page review): grades revised

**Oz's feedback on the five pages**
- Blumenthal: co-signing a letter counts; the 23 September letter itself is B, not A. Grade stays B.
- Hawley: C. No source found in which he says AI poses catastrophic risk.
- Cruz: C confirmed. He is "No" on coordination with China.
- Slotkin: D. She has discussed military use of AI only, not catastrophic risk.
- Sanders: A, looks good.

**What was done**
- `xrisk-record.html`: Hawley B to C and Slotkin C to D, with new summary text; "For review" notes removed for Blumenthal, Hawley and Cruz, shortened for Slotkin; Cruz's coordination with China set to No, citing The View and his summit remarks; Blumenthal's letter ranked B and both Slotkin military statements ranked D; the methodology's "open questions" replaced by a list of rulings plus two still-open items; the index's outdated "three of five grades are borderline" line removed and the count of empty position cells now computed (6 of 15).
- New `classify/overrides.csv` (post id, level, note) and `classify/merge.py --overrides`: levels set by a person replace the labeller's. 11 overrides: two Hawley headline posts B to C, two Cruz posts B to C, six Slotkin posts and one Sanders post on military AI C to D.
- `classify/rubric_prompt.md` and `HANDOFF.md`: the military AI ruling is reversed (now D unless a catastrophic consequence is named); co-signed letters and bills rulings added.
- Commands:
  `python3 classify/merge.py --input data/classify/input --output data/classify/output --review data/classify/review_queue.csv --overrides classify/overrides.csv`
  `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025"`
- Checked with macOS's JavaScript engine: all pages render. Grades shown: Sanders A, Blumenthal B, Hawley C, Cruz C, Slotkin D.

**Inferences the assistant made from the feedback, for Oz to confirm**
- Slotkin at D means the earlier ruling "military AI without human oversight is C" is reversed for everyone, not just for her.
- Hawley at C means a bill or investigation alone does not earn B.
- The two Cruz posts that mention catastrophic risk, and Hawley's op-ed headline posts, were set to C to match the senator's grade.
- Cruz's "No" on coordination with China rests on Oz's reading of his statements ("China is not going to stop", AI as a race to win), not on an explicit statement against coordination. The methodology says "No" requires a statement against the policy.

**Known problems**
- Slotkin's page now shows only her three hand-collected statements; her X posts are all D or off topic and D posts are never shown.
- Posts were not relabelled under the reversed military ruling; only the seven known military C labels were overridden.
- Model-chosen quotes still unchecked for misleading cuts.
- Nothing since `7491721` is committed.

## 2026-11-11 (main table rebuilt)

- Per Oz: the index table now leads with the senator, then a wide column headed "Acknowledgment of catastrophic AI risk" (grade stamp plus a short description of the grade), then a visually smaller group headed "Stated policy positions" with small chips. Slowdown now comes before pause in the table, on senator pages and on the methodology page.
- The short grade descriptions are new wording by the assistant (third item of each `RUBRIC` row in `xrisk-record.html`); Oz should check them.
- Rebuilt with the same `site/build.py` command. Checked with macOS's JavaScript engine that all pages render; not checked visually by the assistant.

## 2026-11-11 (fourth policy added)

- Per Oz: a fourth policy position, "Ban on self-improving AI" (recursive self-improvement), added to `xrisk-record.html` and `HANDOFF.md`. Definition (assistant's wording, for Oz to check): a ban on AI systems that improve themselves or carry out AI research without human direction; a ban on superintelligence alone does not count.
- All five senators are "No stated position". Evidence checked: a text search of the 623 collected posts for related phrases (recursive, self-improving, improve itself, AI research, intelligence explosion) found nothing relevant. No wider search of speeches, bills or press releases was done for the other four senators.
- Sanders: Semafor (23 Sep 2026, https://www.semafor.com/article/09/23/2026/progressive-democrats-push-superintelligence-ban) says his Ban Artificial Superintelligence Act would also ban "recursive self-improvement". His office's summary of the bill (read in full) does not mention it. The bill text was not read. If the text confirms it, he may be Yes, subject to whether a bill counts for a position.
- Found in passing, outside the five: Rep. Ro Khanna is reported to plan a House bill banning recursively self-improving AI (https://thenextweb.com/news/human-control-over-ai-act-khanna-self-improving-ai). Not verified.
- The post labelling instructions do not include this policy, so future X labels will not cover it until they are updated.

## 2026-11-11 (pipeline run on 25 senators; Oz away)

**Goal:** per Oz, run the whole pipeline on 25 senators for a bigger sample.

**Decisions made while Oz was away**
- "25 senators" read as 25 in total: the 5 pilot senators plus 20 new ones.
- The 20 were drawn at random (seed 20261111) from the 95 other current senators, so the sample is not biased toward senators known to talk about AI:
  `python3 -I data/sample/pick_senators.py --legislators <folder with the congress-legislators JSON files> --accounts data/accounts.csv --n 20 --seed 20261111` (run before the new rows were added to `data/accounts.csv`; rerunning now would draw from a different pool).
- New senators have no hand-written record, so `site/build.py` drafts one from X posts alone: grade = highest level any post reached (F only if nothing reached A, B or C; D if any post about AI; "–" if none); positions from the post labels; a "machine-drafted" banner on the page.
- The fourth policy (self-improving AI ban) is "No stated position" for everyone; it is not in the labelling instructions.

**What was done**
- Sample: Barrasso, Blunt Rochester, Collins, Coons, Cramer, Durbin, Darline Graham, Hagerty, Heinrich, Husted, Kaine, Kelly, Marshall, Moreno, Murphy, Murray, Schiff, Sullivan, Thune, Wicker.
- Accounts: `data/accounts.csv` now has a `batch` column (1 = pilot, 2 = this run) and 45 rows. Official accounts resolved by user id from congress-legislators; personal or campaign handles proposed from the assistant's memory and kept only when the X API profile identified the senator. Raw lookups in `data/raw/user_lookup_*`. No account found for Darline Graham. Marshall's listed official account is empty (0 posts), so only @RogerMarshallMD is used. Thune's official account is now @LeaderJohnThune.
- Collection: `python3 collector/search.py --accounts data/accounts.csv --batch 2 --db data/posts.sqlite --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 5000` returned 417 posts (one query of 869 characters). The database now holds 1,040 posts.
- Labelling: `classify/export_chunks.py` (same command as before) wrote 21 new chunk files; 7 Claude subagents (Fable 5.2) labelled them under the current rubric (v0.2 with the military ruling reversed). Their brief also asked that quotes not be cut in a way that reverses meaning.
- Merge and build (same commands as the previous entry). All checks passed; all 25 pages, the index and the methodology render in macOS's JavaScript engine. Not checked visually.
- Portraits: `site/fetch_photos.sh` now falls back to bioguide.congress.gov; all 25 downloaded (Graham and Husted from the fallback). Images not looked at.
- Template: index heading shows the record count; senators sorted by last name; "Bills and actions" hidden when empty; two outdated lines removed from "What this sample shows".

**Results (25 senators; 20 are machine-drafted and unreviewed)**
- Grades: A 5 (Sanders, Blunt Rochester, Coons, Murphy, Schiff), B 3 (Blumenthal, Kelly, Murray), C 3 (Cruz, Hawley, Heinrich), D 11 (Barrasso, Collins, Cramer, Durbin, Hagerty, Husted, Kaine, Marshall, Slotkin, Sullivan, Wicker), F 1 (Moreno), no statement 2 (Graham, Thune).
- New posts per senator: Kelly 80, Husted 68, Murphy 69, Coons 44, Schiff 39, Murray 24, Durbin 17, Blunt Rochester 15, Cramer 14, Heinrich 12, Hagerty 10, Moreno 9, Kaine 5, Wicker 5, Marshall 3, Sullivan 3, Barrasso 1, Collins 1, Thune 0, Graham 0 (no account).
- Positions among the 20 new: Blunt Rochester yes on slowdown; Schiff mixed on slowdown and yes on coordination with China; Coons yes on coordination with China. 87 of 100 position cells are "No stated position".
- Estimated X cost of this run at the reported rates: about $2.10 for posts plus about $0.45 for user lookups. Not confirmed in the console. Estimated total for the day: about $6.

**Draft grades that most need Oz's judgment**
- Murphy (A): one post endorses a warning about "a blind race to build a death machine"; an earlier post says AI "isn't going to become omnipotent and evil and murder us all" and was labelled F. Many posts warn of "societal collapse" from job loss, which is D.
- Moreno (F): two near-identical posts call AI warnings "doomsday scenarios" and "fueling panic"; the main charge is hypocrisy, so D is arguable.
- Kelly (B): rests on one post saying an AI-written false intelligence report "could've escalated into a war with China". Military use is D unless a catastrophic consequence is named.
- Murray (B): rests on a relayed "experts are warning powerful AI could mean catastrophe" judged as endorsed.
- Schiff (A): two of four A posts relay an "existential threat to humankind" warning with mild endorsement.
- Coons (A): "the existential threat posed by AI" in his own words; a second A post is a relayed warning.
- Blunt Rochester (A): "Even if there was a 1% chance AI could wipe out human life, we should be pumping the brakes".
- Heinrich (C): endorses "a real warning" that is only in a link.
- Murphy also has a D-labelled post saying companies "rush out dangerous models that can escape human control" (the only stated consequence is attacks on networks).

**Known problems**
- X posts only for the 20 new senators: a D or "no statement" grade means nothing was found on X, not that the senator has never spoken about catastrophic risk elsewhere.
- Senators graded D show no statements on their page, since D posts are never shown.
- Thune has two accounts and zero matching posts in 22 months; not checked whether the search missed posts.
- One labeller per post; model-chosen quotes unchecked by a person.
- The 623 pilot posts were labelled before the military ruling was reversed and corrected only through the 11 overrides.
- Nothing since `7491721` is committed.

**Next steps for Oz**
1. Review the pages for the eight senators listed above, then skim the D pages.
2. Check the console total against the estimate.
3. Confirm or correct the assumptions listed here and in the earlier entries (25 in total, definition of the fourth policy, short grade descriptions).
4. Say whether to commit.

## 2026-11-11 (news searches for the 20 new senators; senators-elect and lame ducks) — UNFINISHED, stopped by usage limit

**Goal:** per Oz, run news searches for the 20 new senators, add senators-elect, and label lame-duck senators.

**What was done**
- `classify/news_search_brief.md`: instructions for one web-search agent per politician; output `data/news/<bioguide>.json`. 20 agents launched (Claude subagents). 16 had reported when work stopped; Coons, Kelly, Murphy, Murray and an election-results lookup were still running.
- `classify/check_news_quotes.py` (new, NOT YET RUN): downloads each linked page and checks the quote is on it.
- `site/build.py`: new options `--news`, `--quote-check`, `--status`; merges news findings into drafted records. NOT YET RUN after the change.
- `xrisk-record.html`: "Senator-elect" / "Lame duck" labels from a `STATUS` placeholder filled from `data/status.csv` (file NOT YET CREATED). Not yet rendered or checked.

**Results so far (agents' suggested grades from news only, unreviewed)**
- D: Barrasso, Hagerty, Wicker, Collins, Cramer, Husted, Durbin, Marshall, Heinrich. None: Darline Graham. C: Sullivan (borderline D), Schiff, Thune, Blunt Rochester, Moreno (5 F statements plus 1 borderline C). Kaine: agent said A from the 23 Sep 2026 co-signed letter; Oz's ruling makes that letter B, to be applied at merge (not yet done).

**Known problems**
- The session's web search allowance (200 calls) ran out part-way. Searches are incomplete for most; badly for Collins (4 searches), Marshall (3), Thune (2), Moreno (1), Schiff (5). These need rerunning.
- Signers of the 23 Sep 2026 letter: agents read the PDF and report Kaine signed; Durbin and Heinrich did not. Full list of 17 not yet extracted (the PDF is scanned images).
- Election results seen only in search excerpts (unverified): lame ducks among our 25 would be Collins, Husted, Marshall, Darline Graham (lost) and Durbin (retiring). Senators-elect reported: Turek (IA), Brown (OH), Talarico (TX), Cooper (NC), Jackson (ME), Pappas (NH), Andrews (SC), Stratton (IL), Flanagan (MN), El-Sayed (MI), Hamilton (KS), Moore (AL), plus others not yet identified; Mississippi and Alaska reportedly uncalled.

**Next steps**
1. Collect the last agent reports; rerun the incomplete searches when search allowance is available.
2. Cap statements from the 23 Sep letter at B; run the quote check; create `data/status.csv` from verified election results; add senators-elect to `data/accounts.csv` and run the X and news pipeline for them; rebuild and check rendering.

## 2026-11-11 (news searches, senators-elect and lame-duck labels: finished; supersedes the "UNFINISHED" entry above)

**Goal:** per Oz: news searches for the 20 new senators; include senators-elect; label lame-duck senators.

**What was done**
- News search: one Claude subagent per person, following `classify/news_search_brief.md`, wrote `data/news/<id>.json` (37 files: the 20 batch-2 senators and the 17 senators-elect). Five thin searches (Collins, Thune, Marshall, Moreno, Schiff) were rerun; Collins and Thune are now complete.
- Quote check: `python3 classify/check_news_quotes.py --news data/news --out data/news/quote_check.csv` downloads each linked page and looks for the quote. Result: 80 found, 11 not found, 4 pages could not be downloaded (95 statements).
- 23 September 2026 letter: all 17 signers read from Sen. Van Hollen's press release (https://www.vanhollen.senate.gov/news/press-releases/van-hollen-more-than-15-senate-democrats-push-trump-to-negotiate-ai-guardrails-with-xi): Van Hollen, Murray, Cantwell, Merkley, Blumenthal, Hirono, Kaine, Warren, Duckworth, Cortez Masto, Smith, Rosen, Luján, Padilla, Warnock, Welch, Alsobrooks. `site/build.py` applies Oz's ruling (the letter is B) to any statement quoted from it.
- Election results (CBS News live results, Roll Call 4 Nov 2026, Wikipedia; read through a page-summarising tool): 17 senators-elect; Alaska (Sullivan v. Peltola) and Mississippi uncalled as of 11 Nov. `data/status.csv` marks the 17 senators-elect and 5 lame ducks in our sample (Collins, Husted, Marshall, Darline Graham lost; Durbin retired). Sullivan is not marked. Klobuchar and Blackburn (elected governor) and other departing senators are not in our sample.
- Senators-elect added to `data/accounts.csv` as batch 3 (23 accounts). Those who never served in Congress have no Bioguide ID; a made-up key of the form `ELECT-<state>-<NAME>` is used in that column. Accounts confirmed with `collector/lookup_users.py` (new; profiles identify each person; Turek and Jackson handles taken from their campaign sites). Raw lookups in `data/raw/user_lookup_names_20261111T22*.json`.
- Collection: `python3 collector/search.py --accounts data/accounts.csv --batch 3 --db data/posts.sqlite --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 3000` returned 159 posts (about $0.80 at the reported rate, plus about $0.31 of lookups; not confirmed in the console). Turek and Hamilton: no matching posts.
- Labelling: 3 subagents, 15 new chunk files; `classify/merge.py` (same command as before) passed: 1,199 posts.
- Build: `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --news data/news --quote-check data/news/quote_check.csv --status data/status.csv`
- Render check (new script): `python3 site/render_check.py site/index.html` -> "42 people rendered, plus index and methodology; 17 senators-elect, 5 lame ducks". Not checked visually.
- Portraits: `sh site/fetch_photos.sh`; the 10 senators-elect who never served in Congress have none.

**Results (draft grades, machine-drafted, unreviewed; grade = highest level in X posts or news statements)**
- Sitting senators: A Sanders, Blunt Rochester, Coons, Murphy, Schiff, Kelly; B Blumenthal, Murray, Kaine; C Cruz, Hawley, Heinrich, Marshall, Moreno, Sullivan, Thune; D Barrasso, Collins, Cramer, Durbin, Hagerty, Husted, Slotkin, Wicker; none Darline Graham.
- Senators-elect: A El-Sayed, Hamilton, Pappas; B Flanagan, Cooper; D Moore, Stratton, Turek, Barr, Letlow, Jackson, Alme, Brown, Hern, Andrews, Talarico, Hageman.
- Positions among senators-elect: El-Sayed yes on all four (first yes on the self-improving AI ban, from his campaign plan: "That means banning recursive self-improvement"); Cooper mixed on slowdown, yes on coordination with China (debatable: he said people need "to meet with the Chinese leader" about AI, not about pace).
- Changes from adding news to the 20 batch-2 senators: Kelly B->A, Kaine D->B, Marshall D->C, Moreno F->C, Sullivan D->C, Thune none->C.

**Known problems**
- Web search allowance: 200 searches per session shared by all subagents, refilling about 100 an hour. It ran out twice. For 14 of the 17 senators-elect no web search ran at all; their results come from official and campaign sites and local news sites opened directly. Marshall, Moreno and Schiff remain partly searched. Treat every D or "none" among senators-elect as provisional.
- Leads not followed: Louisiana Illuminator, 5 Oct 2026 (https://lailluminator.com/2026/10/05/ai-apocalypse-most-louisiana-candidates-for-congress-stay-vague-on-regulation) reportedly says Letlow doubted AI poses a true threat to humankind (seen in a search summary only; page would not download; could be F). Thune's reply on existential threat (Axios, 14 Sep 2026, not opened). Turek C-SPAN clip, 21 Sep 2026. Pappas WMUR debate, 28 Oct 2026 (video). Marshall's 2023 bioweapons remark (out of period).
- Draft grades resting on one sentence or a judgment call: Hamilton A ("This is a potential existential threat to the human race", KCUR, AI by context only), Pappas A (endorsed relayed warning, NHPR), Kelly A (relayed warning in floor speech), Coons A ("risk for us as a species"), Flanagan B (one Pioneer Press quote), Cooper B/C ("negative potential for the human race" was graded C by the searcher, arguably A), Moreno C (five F statements, one borderline C), Sullivan C and Marshall C (borderline D), Murphy (news B, X A).
- The 23 Sep letter is quoted as saying frontier AI "poses an existential threat" and threatens "humanity writ large"; Oz ruled it B. Worth a second look.
- The draft-grade rule (highest level wins) hides dismissals: Moreno and Murphy both have F-level statements under a higher grade.
- News "No" positions (e.g. Moreno no on pause, Coons no on pause from paraphrases) were set by the searchers and are unreviewed.
- Quotes: 15 of 95 not confirmed by the automatic check (scanned letters, blocked pages). Many pages were read through a tool that summarises; a person must still check every quote.
- Election results not certified; Arkansas from Wikipedia only (not in our sample).
- Nothing since `7491721` is committed.

**Next steps for Oz**
1. Review the pages flagged above, then the rest.
2. Decide how a record with both acknowledgment and dismissal should be graded (Moreno, Murphy).
3. Say whether to rerun the unsearched senators-elect in a fresh session (search allowance), and whether to commit.

## 2026-11-11 (page simplification and per-person summary sentences)

- Per Oz: removed the statistics paragraph under the grade, the explanatory paragraph in the Statements section (now on the methodology page under "How statements are collected and chosen"), and the extra text on policy rows with no stated position.
- Per Oz: the line after the grade is now a sentence specific to each person, not the rubric criterion. The five hand-written records use their existing `why` text; the other 37 come from `data/summaries.csv`, written by the assistant from the statements found (unreviewed; quoted fragments are taken from the collected statements). `site/build.py` now requires `--summaries` and stops if a drafted record has none. The sentences must be revised whenever a grade or the evidence changes.
- Build command: `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --news data/news --quote-check data/news/quote_check.csv --status data/status.csv --summaries data/summaries.csv`; render check passed (42 people). Not checked visually.
- Later the same day, per Oz: all 42 summary sentences reworded to open with "Senator X has / has not acknowledged catastrophic risk from AI", followed by what they have said (the five hand-written ones in `xrisk-record.html`, the rest in `data/summaries.csv`). Rebuilt; render check passed. Not checked visually.
- Later the same day, per Oz: new visual design in `xrisk-record.html` (styles only; no change to content or structure): white page, serif headlines and quotes (Newsreader), Source Sans 3 text, hairline rules instead of boxes, plum accent and grade ramp, round grade stamps. Rebuilt; render check passed; checked by the assistant in headless Chrome screenshots (index, Kelly and El-Sayed pages; light and dark).
- Later the same day: Oz noticed Barr's page said he wants to win the AI race with China but showed no evidence. Cause: posts labelled D were never displayed, so D records built from X posts alone had empty Statements sections. Fix in `site/build.py`: when nothing stronger (A, B, C or F) was found anywhere for a person, their D posts are shown, quoting the whole post if it is 300 characters or less, otherwise its first sentence that mentions AI. These quotes are picked by rule, not by a model, but still carry the "chosen by a language model" tag (the level was). Rebuilt; render check passed.
- Later the same day: per Oz, trivial posts (e.g. Barr congratulating a school on an AI competition) should not be shown. Replaced the first-sentence rule with a relevance pass: `classify/export_relevance.py` (command in its header) exported the 227 D posts of the 19 people with nothing stronger; 2 Claude subagents judged each under `classify/relevance_prompt.md` (show or not, plus the quote), output in `data/classify/relevance/output/` (178 shown, 49 dropped; quotes validated as exact substrings by the subagents and again by `site/build.py`). `site/build.py` now requires `--relevance data/classify/relevance/output` and stops if a needed post has no decision. Known judgment calls: Brown's campaign attacks on Husted about data centers are mostly shown; Alme's two posts were both dropped; near-duplicates are left to the page's own selection. Rebuilt; render check passed.

## 2026-11-11 (night): remaining 75 senators — IN PROGRESS; letter ruling changed; search box and map

**Goal:** per Oz: run the collection for the 75 senators not yet covered; later the same evening, treat the 23 September letter as A, and add a search box and a US map to the index.

**What was done**
- Accounts: `python3 -I data/sample/add_batch4.py --legislators <folder with the congress-legislators JSON files> --accounts data/accounts.csv --lookups data/raw/user_lookup_names_20261112T003306.json data/raw/user_lookup_names_20261112T003319.json data/raw/user_lookup_names_20261112T003337.json` added 135 accounts for 75 senators as batch 4 (handles proposed from the assistant's memory, kept only when the X profile identified the senator; four names then shortened by hand: Mike Crapo, Chuck Grassley, Alex Padilla, Jack Reed). Only a personal or campaign account found for Justice and Sheehy.
- Collection: `python3 collector/search.py --accounts data/accounts.csv --batch 4 --db data/posts.sqlite --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 4000` returned 1,653 posts in 4 queries (database: 2,852). No matching posts: Justice, Murkowski, Ron Johnson. Estimated cost about $8.30 plus about $1.50 of lookups (not confirmed in the console); running estimate about $19 of the $65 cap.
- Labelling: `classify/export_chunks.py` (same command) wrote 79 new chunk files; 17 Claude subagents labelled them; `classify/merge.py` (same command, with `--overrides`) passed on all 2,852 posts.
- News: `classify/news_search_addendum.md` (new) adds the verified letter signers and the search-limit rule to the brief. One subagent per senator. 30 finished with their full six or more web searches; 17 ran with one web search or none after the shared allowance ran out (Cortez Masto, Hyde-Smith, Johnson, Justice, Kennedy, Kim, King, Klobuchar, Lankford, Lee, Luján, Lummis, Markey, McConnell, McCormick, Merkley, Moody: own website only, MUST BE RERUN); 28 not started (Moran through Young).
- `data/status.csv`: 12 more lame-duck rows (Armstrong, Cassidy, Cornyn, Daines, Ernst, Lummis, McConnell, Peters, Shaheen, Smith, Tillis, Tuberville), taken from the senators-elect notes already in the file. Blackburn and Klobuchar (elected governor) not labelled.
- `site/build.py`: two people with the same last name get first-and-last page ids (rick-scott, tim-scott).
- Letter ruling: Oz now treats the 23 September 2026 letter as A (was B). `site/build.py` sets every statement quoted from it to A; Blumenthal's hand-written grade changed B to A with a new summary sentence; Kaine and Murray sentences reworded; `HANDOFF.md` updated.
- Search box and map: `xrisk-record.html` has a search box in the header (name, state, party, status, "grade a"; a full state name matches that state only) and a map on the index (each state split in two colours for its two sitting senators; hover or focus lists everyone from the state; click filters the table). State outlines: `python3 site/make_map.py --topojson <states-albers-10m.json from https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/> --out site/us_states.json`; `site/build.py` now requires `--map site/us_states.json`. `site/render_check.py` also checks a filtered index.

**Results**
- Not yet built: `site/index.html` still shows 42 people with the old design of the index. A test page with the new template and the 42 existing records was checked in headless Chrome (map, simulated hover, search for "ohio"); hover not tried in a real browser.
- Early draft grades from finished news searches are in the agents' files under `data/news/`; nothing reviewed.

**Open questions / known problems**
- The web search allowance (about 100 an hour) is the bottleneck: about 270 more searches needed.
- Many agents read pages through a summarising tool; quotes need the automatic check and a person.
- Co-sponsorship of the Ban Artificial Superintelligence Act could not be checked for anyone (congress.gov refuses downloads).

**Next steps**
1. Rerun the 17 thin searches and run the 28 not started, as the allowance refills.
2. Quote check, relevance pass for people with only ordinary AI posts, 75 summary sentences (and revise sentences for letter signers), rebuild with `--map`, render check, look at the pages.

## 2026-11-11 (late night): all 100 senators and 17 senators-elect built (supersedes the "IN PROGRESS" entry above)

**Goal:** finish the collection for the 75 remaining senators and rebuild the site with the search box and map.

**What was done**
- News searches: after Oz raised `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, the 28 not-yet-started searches ran and the 17 thin ones were rerun (each rerun agent read the earlier file, ran the six required searches and rewrote the file); Ossoff, Schumer and Tim Scott were also rerun after partial searches. Some searches were still refused in bursts when 20 agents started at once. Left as they are with one search refused: Schmitt (6 ran), Tina Smith (5 ran), Rounds (6 ran). `data/news/` now has 112 files.
- Two statements with an empty quote (Gillibrand, Tillis; both level D) were moved from `statements` to `notes` in their news files so the build's check passes.
- Quote check: `python3 classify/check_news_quotes.py --news data/news --out data/news/quote_check.csv` -> 373 statements: 323 found word for word on the linked page, 24 not found (several are PDFs), 26 pages could not be downloaded.
- Trivial-post filter: `python3 classify/export_relevance.py --labels data/classify/review_queue.csv --news data/news --template xrisk-record.html --out data/classify/relevance/input --done data/classify/relevance/output --chunk-size 125` wrote chunks 3 to 5 (275 posts); 3 subagents judged them (214 shown, 61 not).
- Summary sentences: `python3 classify/export_summary_digest.py --labels data/classify/review_queue.csv --news data/news --accounts data/accounts.csv --batch 4 --parts 4 --out data/classify/summary_digest` wrote an evidence digest per person; 4 subagents drafted the 75 sentences under `classify/summary_prompt.md` (new), each checking that quoted fragments appear in that person's collected quotes. Merged into `data/summaries.csv` (112 rows). Edited by the assistant: the two Scotts named in full; Warner's sentence now mentions "over the top". All 75 were read once by the assistant, not by Oz.
- Template: direct links to pages with accented names now work (`#luján`).
- Build: `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --news data/news --quote-check data/news/quote_check.csv --status data/status.csv --summaries data/summaries.csv --relevance data/classify/relevance/output --map site/us_states.json`
- Render check: `python3 site/render_check.py site/index.html` -> "117 people rendered, plus index and methodology; 17 senators-elect, 17 lame ducks". Index and Ron Johnson's page looked at in headless Chrome screenshots (dark mode). Map hover not tried with a real mouse.
- Portraits: `sh site/fetch_photos.sh` -> 106 images; the 10 senators-elect who never served in Congress and Alan Armstrong have none.

**Results (draft grades; machine-drafted and unreviewed except the five pilot records; letter of 23 September counted as A)**
- Sitting senators (100): A 28, B 16, C 19, D 32, F 4, no statement 1. Senators-elect (17): A 3, B 2, D 12.
- Among the 95 machine-drafted sitting senators by party: Democrats A 24, B 9, C 6, D 4; Republicans A 2 (Ron Johnson, Rick Scott), B 6, C 11, D 27, F 4 (Cornyn, Paul, Schmitt, Sheehy), none 1; Independent B 1 (King).
- Of the 28 A grades, these rest only on the co-signed letter (own words lower): Alsobrooks, Cantwell (own words B), Cortez Masto, Duckworth, Hirono, Kaine, Merkley, Murray, Padilla, Smith, Warnock, Welch, and Blumenthal.
- Positions among drafted records: slowdown yes 23, mixed 7, no 9; pause yes 2, mixed 16, no 8; coordination with China yes 21, mixed 4, no 1; self-improving AI ban yes 1 (El-Sayed).

**Open questions / known problems**
- Records with both acknowledgment and dismissal now include Ron Johnson (A with "fear-mongering"), Warner, Fetterman, McCormick, Daines, as well as Moreno and Murphy. The highest-level rule still decides the grade.
- F grades on thin evidence: Sheehy (one post about "hysteria"), Schmitt, Paul. Cornyn's F rests on Fox News quotes read in fragments.
- Judgment calls flagged by searchers: Markey B (nuclear launch letter under the military ruling), Reed C ("humanity itself", arguably A), Schatz B (arguably A), Kennedy and King B (arguably A), Lankford C (co-signed letter only), Cassidy B (posts summarising someone else's article), Blackburn C (her office's bill summary).
- Many quotes were read through a tool that summarises pages; 50 of 373 are not confirmed by the automatic check. Every quote still needs a person.
- Co-sponsorship of the Ban Artificial Superintelligence Act is unverified for everyone.
- The index sorts by page id, so Van Hollen is under H, Cortez Masto under M and Blunt Rochester under R.
- The map colours sitting senators only; senators-elect appear in the hover box.
- X spend for this run about $9.80 at reported rates (not confirmed in the console); running estimate about $19 of $65.
- X terms on displaying post text still unread. Almost nothing is committed.

**Next steps for Oz**
1. Review pages, starting with the A, B and F grades and the judgment calls above.
2. Decide how to grade records with both acknowledgment and dismissal.
3. Check the X console total; say whether to commit.

## 2026-11-11 (late night, addendum): the three missing searches

- Per Oz, the one refused search each for Schmitt (extinction or existential risk), Tina Smith ("AI safety") and Rounds (AI agreement with China) was run by a subagent each (Rounds's first attempt died when the computer slept and was restarted). No grade or position changed. Rounds gained one level D statement (Fox News, 30 May 2025). Every one of the 112 news files now has all its required searches.
- Quote check rerun on all files, then the site rebuilt with the same command as the entry above; render check passed (117 people).

## 2026-11-12: Oz's grade rulings; search hides the map; current/next Senate toggle; bar chart; surname sorting

**Goal:** Apply Oz's decisions on the mixed records, and four page changes: hide the map while searching, a toggle between the current Senate and the next one, a bar chart of grades with the same toggle, and correct sorting of multi-word last names. Then commit.

**What was done**
- New file `data/grade_overrides.csv` holds grades ruled by a person; `site/build.py` takes it with `--grade-overrides`, replaces the drafted grade and says so in the record's "For review" note. Rulings (Oz, 12 November 2026): Warner B, Fetterman B, McCormick B, Daines B (all four the same as the machine draft), Moreno F (draft was C), Murphy A (same as draft). Moreno's sentence in `data/summaries.csv` was rewritten to match F.
- Two rulings recorded in `HANDOFF.md`, and "Recent statements" added to the rulings on the methodology page: 2026 statements count for much more than 2025 ones. This is NOT built into the drafted grades as a rule.
- `xrisk-record.html`: map and chart are hidden while the search box has text (clicking a state searches for it, so it also hides the map); toggle "Current Senate / Next Senate, from 3 January 2027" (next = sitting senators minus the 17 lame ducks plus the 17 senators-elect); bar chart of senators per grade below the map, following the toggle; index and previous/next links sorted by last name, with Blunt Rochester, Cortez Masto and Van Hollen listed as multi-word last names.
- `site/render_check.py` gained checks: sort order of those three names, both Senates have 100 members and two per state, map absent while searching.
- Build: `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --news data/news --quote-check data/news/quote_check.csv --status data/status.csv --summaries data/summaries.csv --relevance data/classify/relevance/output --map site/us_states.json --grade-overrides data/grade_overrides.csv`, then `python3 site/render_check.py site/index.html`.

**Results**
- Render check passed: 117 people; 17 senators-elect, 17 lame ducks.
- Current Senate: A 28, B 16, C 18, D 32, F 5, none 1. Next Senate: A 30, B 16, C 14, D 36, F 4, none 0. (Read from the built page.)
- Checked in headless Chrome: screenshots of both Senates in dark and light themes, and a scripted click on the toggle followed by typing "ohio" (chart switched to the next Senate's numbers, map gone, 3 rows). Not tried by hand with a mouse.
- If only 2026 statements counted for people who have any, four drafted grades would drop: Lankford C to D, Risch C to D, Blackburn C to D, Budd B to D. Not applied.

**Open questions / known problems**
- Ron Johnson is still A, undecided. Oz could not open the Raw Story page (https://www.rawstory.com/ai-trump-warning/); it downloaded here on 12 November 2026. The passage: "They want to preempt a predatory capture by having regulations written to their benefit and exclusion of potential competition. I'm highly skeptical," ... "There's fear-mongering. I'm not buying it," ... "I think they let them loose. True or not? I don't know, but I'm highly skeptical." The article says he likened AI fears to those raised around COVID and climate change. That is 23 September 2026, three weeks after his Breitbart remarks about AI destroying the human race.
- Whether to apply the 2026 rule to the four records above.
- The table below the map still lists all 117 people whichever Senate is chosen.
- Unchanged: every quote needs a human check; X console total unconfirmed; X display terms unread.

**Next steps**
1. Oz to rule on Ron Johnson and on the four records affected by the 2026 rule.
2. Review of the remaining machine-drafted pages.

## 2026-11-12 (addendum): Lankford, Risch, Budd to D; misuse-only ruling

- Per Oz: Lankford D (the letter's "public safety" line is not about catastrophic risk), Risch D and Budd D (their statements date from 2025). Added to `data/grade_overrides.csv`; summaries rewritten. Blackburn (C, from a December 2025 bill summary) was not mentioned by Oz and is unchanged.
- Per Oz: a record whose only named catastrophic risk is misuse of AI by people (bio, cyber) must say so in its summary, and Oz is hesitant to give it B. Recorded in `HANDOFF.md`. I read the strongest statements of all 15 B records and judged four to be misuse-only or mainly misuse: Daines and Ossoff (only misuse), Fetterman and McCormick (mainly; their op-ed also mentions "when a model goes rogue" once, checked on the Senate page on 12 November 2026). Their summaries now say so. Grades left at B, pending Oz, because Oz ruled Daines, Fetterman and McCormick B earlier the same day.
- Rebuilt with the command in the entry above; render check passed (117 people). Current Senate: A 28, B 15, C 16, D 35, F 5, none 1. Next Senate: A 30, B 15, C 12, D 39, F 4.
- Not committed (last commit `a24bcf3`).

## 2026-11-12 (second addendum): misuse-only records to C, Blackburn D, Johnson B

- Per Oz: Daines, Fetterman and McCormick drop from B to C (misuse only). Oz said "all 3"; I had listed four, and I also dropped Ossoff to C because he is the clearest misuse-only case. ASSUMPTION, to be confirmed by Oz.
- Per Oz: Blackburn D; summary now says the bill is from December 2025 and that she has made no significant statement about AI risk in 2026 (her two 2026 statements in `data/news/B001243.json` are both level D).
- Per Oz ("B I guess"): Ron Johnson A to B; summary rewritten. Oz floated a general rule, "maybe a dismissive statement should be minus one letter grade". Recorded in `HANDOFF.md` as tentative and NOT applied generally. If it were, among people with a dismissive statement and a grade above F: Warner B to C; Daines, Fetterman and McCormick C to D; Murphy's dismissive post is from 2025 and Oz already ruled him A.
- All in `data/grade_overrides.csv` (12 rulings). Rebuilt with the same command; render check passed (117 people). Current Senate: A 27, B 12, C 19, D 36, F 5, none 1. Next Senate: A 29, B 13, C 14, D 40, F 4, none 0.
- Not committed (last commit `a24bcf3`).

## 2026-11-12 (third addendum): Ossoff confirmed, penalties do not stack, Warner to C; committed

- Oz confirmed Ossoff at C and said not to stack the misuse and dismissal penalties. I read that as adopting the "dismissive statement lowers the grade one letter" rule, so Warner goes B to C (he was the only record it changes once stacking is ruled out); summary rewritten. Daines, Fetterman and McCormick stay C. To be confirmed by Oz, since Oz called Warner "a solid B" earlier the same day.
- Rebuilt with the same command; render check passed.
