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

## 2026-11-12 (evening): House of Representatives started — IN PROGRESS

**Goal:** Build the same record for every member of the House, using subagents on Opus 5.5 (Oz's instruction).

**What was done**
- `data/house/make_roster.py` lists sitting voting House members from the public unitedstates/congress-legislators files (downloaded 11 November 2026, kept in the session scratchpad, not in the project): `python3 -I data/house/make_roster.py --legislators <folder> --out data/house/roster.csv`. Result: 433 members (two seats vacant in that file), 23 without an X handle on file. Delegates left out.
- `classify/news_search_house.md`: House instructions on top of the Senate brief, including Oz's rulings of 11 and 12 November (misuse only is C; 2026 outweighs 2025; a dismissive statement lowers one letter, no stacking; general "public safety" mentions are D).
- Pilot: 19 news-search subagents launched on Opus 5.5, one per representative, writing to `data/news_house/<bioguide>.json`. Five chosen because they are known for AI work (Obernolte, Lieu, Foster, Casar, Beyer), 14 drawn at random (seed 0; the draw's 15th, Pappas, was skipped because he already has a file as a senator-elect).

**Not started / needs Oz**
- X posts for the House: not started. Rough cost at the reported rates: account lookups about $4 to $9, posts about $22 to $54 (guess of 10 to 25 matching posts per member; senators averaged 24). That could pass the $65 cap given about $19 already spent (unconfirmed in the console).
- Representatives-elect (winners on 3 November 2026 who are not sitting members) are not in the roster.
- The page (`site/build.py`, `xrisk-record.html`) handles senators only so far.

**Next steps**
1. Check the pilot files for quality, then run the remaining ~410 members in groups of 20.
2. Oz to decide on X spend for the House and on representatives-elect.

## 2026-11-12 (night): House pilot of 19 finished; X posts for the pilot; next 60 launched — IN PROGRESS

**What was done**
- Pilot news searches: all 19 files in `data/news_house/`. Not yet run through the automatic quote check.
- X posts for the pilot (Oz: "start with a subset"): `python3 collector/lookup_users.py --raw-dir data/raw <19 handles>` (raw: `data/raw/user_lookup_names_20261113T020122.json`; 17 found, RepFeenstra and RepEdwards do not exist), accounts in `data/house/accounts.csv` (batch h1, official accounts only), then `python3 collector/search.py --accounts data/house/accounts.csv --batch h1 --db data/house/posts.sqlite --raw-dir data/raw --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 1500` -> 472 posts. Cost about $2.55 at reported rates (unconfirmed); running estimate about $22 of $65.
- Labelling: `python3 classify/export_chunks.py --db data/house/posts.sqlite --accounts data/house/accounts.csv --out data/house/classify/input --chunk-size 65` (18 files), five Opus 5.5 subagents, then `python3 classify/merge.py --input data/house/classify/input --output data/house/classify/output --review data/house/classify/review_queue.csv` -> "472 posts written".
- House letters: five letters signed by many members turned up (10 Aug to Speaker Johnson, Casar and Ramirez, 18 signers; 10 Aug to OpenAI, Casar; 15 Sep to Speaker Johnson, 107 signers; 16 Sep, Beyer and about nine others; 18 Sep on China talks, Meeks, Jacobs, Bera, 29 signers). Pilot searchers graded the same letter differently, so `classify/news_search_house.md` now tells searchers to leave these letters out; a subagent is building a checked catalogue `data/house/letters.json` (text, quotes, signers matched to bioguide ids) to be applied to signers by the build. I read the 107-signer letter's signed PDF myself: dated 15 September 2026, 107 names, saved in `data/house/letter_2026-09-16_signers.txt`. The PDF says "keep the House ... in session"; press releases of 16 September say "immediately reconvene".
- Next 60 members (roster order, AK to CA-46) launched as one Workflow run on Opus 5.5 (run id wf_46c47a5e-cd4). The six House members who are senators-elect already have files in `data/news/` and are skipped.

**Results (pilot, own words only, letters left out; machine-drafted, unreviewed)**
- A: Casar, Beyer, Jacobs. B: Obernolte, Lieu (his one A post is from 2025), Foster, Trahan, Thompson, Pat Ryan, Harder. C: Vasquez, Matsui, Tlaib. D: Morelle, Sylvia Garcia, Garamendi, Feenstra. Nothing found: Velázquez, Edwards.
- Harder's B is a post about bioweapons reaching "bad actors", which is misuse only and so C under Oz's ruling. The X post labelling instructions do not carry that ruling; it must be applied when grades are drafted.
- Casar is "yes" on all four policies (lead House sponsor of the Ban Artificial Superintelligence Act).

**Open questions / known problems**
- Oz to rule on the level of each House letter (see catalogue when ready).
- Foster: his office reposted September 2026 video interviews about catastrophic AI risk that have no transcripts; a person should watch them.
- congress.gov refuses downloads, so co-sponsors of H.R. 10538 come from a third-party list (FastDemocracy, 12 names).
- Member names in pilot files are written inconsistently; the build should take names from the roster.
- Only official X accounts were searched for the House; personal and campaign accounts were not looked up.
- The page still handles senators only.

## 2026-11-13 (early morning): House news searches — all 427 files written, but 325 are INCOMPLETE (search limit ran out)

**What was done**
- Run of 60 members (Workflow run wf_46c47a5e-cd4, Opus 5.5): finished in 14 minutes, about 4.1 million tokens, no search refused.
- Run of the remaining 348 members (Workflow run wf_c21758e5-ca2, Opus 5.5): finished in about 2 hours 8 minutes, about 21.5 million tokens. The work list was `house_todo.json` in the session scratchpad.
- The session's shared web search allowance ran out after roughly the first 25 to 30 members of the second run. Searchers followed the instructions (no workarounds) and read the member's official site instead.
- `data/house/search_status.csv` (new) lists, for each of the 348, how many searches the searcher says ran and whether the search was complete (6 or more ran). Built from the run's log of final reports.

**Results**
- `data/news_house/` has 427 files, one for every sitting voting member except the six who are senators-elect (their files are in `data/news/`). All pass the format check except five quote-less statements (in G000597 twice, J000305, L000397, P000034) to be moved into notes.
- Complete searches: 19 (pilot) + 60 + 23 = 102 members. Incomplete: 325 members, of whom about 196 had no search run at all and about 85 had one to three.
- Suggested grades across all 427 files (news only, no X posts, no letters, unreviewed; 325 rest on official sites only): A 11, B 12, C 24, D 195, nothing found 185. These are NOT reportable as findings for the House: an incomplete search biases towards "nothing found".

**Mistake to record**
- I said I would run in groups and check for refusals between them, then launched all 348 at once because the 60-member run had no refusals. The allowance is per session, not per minute, so a clean small run said nothing about the large one. About 20 million tokens went on searches that could not search.

**Next steps**
1. Oz to raise the web search limit again (or start a new session), then rerun the 325 members marked "no" in `data/house/search_status.csv`, in groups of about 40 with a refusal check after each. About 7 searches per member means roughly 2,300 searches.
2. Oz's rulings on the five House letters (`data/house/letters.json`).
3. Quote check on House files; House pages on the site; X posts beyond the pilot subset.

## 2026-11-13: House search rerun — stopped by the search limit again after 88 members

- Per Oz ("restart the search"), reran the 325 incomplete members in groups of 40 with a stop rule (Workflow run wf_e4165374-f46, Opus 5.5, about 7.4 million tokens, 16 minutes). Groups 1 and 2 ran clean; in group 3, 32 of 40 had searches refused, so the run stopped itself after 120 members. Searchers whose first two searches were refused left the existing file unchanged.
- 88 members now have complete searches; `data/house/search_status.csv` updated from the run's structured reports. Complete: 190 of 427. Still incomplete: 237. All 427 files pass the format check.
- The allowance seems to be about 600 to 650 searches per raise (88 members at about 7 each). The remaining 237 need about 1,700.

## 2026-11-14: House search reruns — 277 of 427 complete, 150 left, search limit still in the way

- Second rerun (Workflow run wf_e8580058-074, 237 members): groups 1 and 2 clean, stopped in group 3; 87 more complete. `data/house/search_status.csv` updated.
- Third rerun (run wf_45a980f1-cf2, 150 members), started minutes later: all 40 of the first group had their first two searches refused; stopped at once, files unchanged. About 2 million tokens spent finding that out.
- One test search from the main session, between the two runs, went through. So the limit is not a fixed total; it looks like an allowance of roughly 600 searches that refills over some period I do not know (the first rerun was on 13 November, the second on 14 November). Not verified.
- Remaining list: `house_redo_list3.json` in the session scratchpad; it can be rebuilt from the rows with search_complete = no in `data/house/search_status.csv`.
- Next: wait for the allowance to refill (or Oz raises it), then rerun the 150 with the same script. Before launching, test with a handful of searches, not one.

## 2026-11-14 (later): House news searches COMPLETE for all 427 sitting voting members

**What was done**
- Oz raised `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` from 600 to 3000 in `~/.claude/settings.json` and restarted. Three test searches passed, then the last 150 members ran (Workflow run wf_c96780e9-882, Opus 5.5, about 9.9 million tokens, 26 minutes) with no search refused.
- `data/house/search_status.csv`: all rows now "yes". Six quote-less statements moved from `statements` into `notes` in their files.

**Results**
- 427 files in `data/news_house/`, all passing the format check, all listing six or more searches, all member names matching the roster. The other six House members are senators-elect with files in `data/news/`.
- Suggested grades from the news searches alone (no X posts except nothing, no letters applied, unreviewed): A 12, B 12, C 31, D 232, F 1, nothing found 139. By party: Democrats A 11, B 10, C 19, D 113, none 60; Republicans A 1, B 2, C 11, D 119, F 1, none 79; Independent C 1.
- These are searchers' suggestions, not grades. They will change when the five letters are applied (the 107-signer letter alone covers about a quarter of the House) and when X posts are added.
- Total subagent tokens for House news searches across all runs: about 53 million, of which roughly 22 million went on searches cut short by the limit.

**Open questions / known problems**
- Oz's rulings on the five House letters (`data/house/letters.json`). Reports say Rep. Sam Liccardo drafted the 107-signer letter (Axios, 11 September 2026); not yet added to the catalogue.
- Co-sponsors of H.R. 10538: third-party trackers disagree (six, nine, ten or twelve names). Treat as unverified unless a press release names the member.
- Automatic quote check not yet run on House files. X posts collected for 17 accounts only. The page handles senators only. Representatives-elect not listed. Nothing from the House is committed.

## 2026-11-14 (afternoon): House X posts collected and labelled, quote check run, House added to the site

**Goal:** Per Oz: scrape X for House members (budget raised to about $90 in total), run the quote check, add the House to the site.

**What was done**
- X accounts: looked up the 385 handles on file not yet collected (raw: `data/raw/user_lookup_names_20261114T15552{8,9}.json`, `...15553{0,1}.json`); 378 found. Kept 377 whose profile names the member (dropped Pou: the handle on file is a House administrative office). Added to `data/house/accounts.csv` as batch h2. Not found: RepMikeJohnson, RepKClark, RepTomEmmer, RepMalliotakis, JohnMannionNY22, RepCloudTX, RepWesleyHunt (plus RepFeenstra, RepEdwards from the pilot). 23 members have no handle on file. Official accounts only.
- Posts: `python3 collector/search.py --accounts data/house/accounts.csv --batch h2 --db data/house/posts.sqlite --raw-dir data/raw --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 12000` -> 3,366 posts. `data/house/posts.sqlite` now holds 3,838 posts from 344 accounts.
- Cost of this run at reported rates: 378 lookups ($3.78) + 3,366 posts ($16.83) = about $20.60. Running estimate about $43 of $90 (unconfirmed in the X console).
- Labelling: pilot labels set aside (`data/house/classify/*_pilot`), all posts re-exported (350 files) and labelled by 51 Opus 5.5 subagents (Workflow run wf_c322b4f6-2a4, about 3.3 million tokens) using `classify/rubric_prompt.md` plus new `classify/rubric_house_addendum.md` (misuse only is C with flag `misuse_only`; general "public safety" mentions are D). `classify/merge.py` now allows the flag `misuse_only`. `python3 classify/merge.py --input data/house/classify/input --output data/house/classify/output --review data/house/classify/review_queue.csv` -> "3838 posts written".
- Quote check: `python3 classify/check_news_quotes.py --news data/news_house --out data/news_house_quote_check.csv`.
- Site: new `site/house_records.py` drafts one record per House member (grade by rule, see its docstring); `data/house/letter_levels.csv` holds the PROVISIONAL letter levels (mine, not Oz's: 107-signer letter B; hearings letter C; OpenAI letter D; "warning shots" letter C; China talks letter C and not counted as a China position). `site/build.py` takes `--house site/house_records.json`. `xrisk-record.html` has a Senate / House of Representatives switch; the House view has the bar chart and table but no map; search lists both chambers; previous/next stay within a chamber; house.gov pages count as official records; menu item renamed "Members". `site/render_check.py` checks the House index and that each chamber's index lists only its own members.
- Commands: `python3 site/house_records.py --roster data/house/roster.csv --news data/news_house --letters data/house/letters.json --letter-levels data/house/letter_levels.csv --quote-check data/news_house_quote_check.csv --labels data/house/classify/review_queue.csv --out site/house_records.json`, then the usual build command with `--house site/house_records.json`, then `python3 site/render_check.py site/index.html`.

**Results**
- Post labels: A 43, B 40, C 201, D 3,173, F 12, off topic 369; 13 flagged misuse only. The 472 pilot posts were labelled twice by different subagents: 443 (94%) got the same level; most changes were between C and D or B and C. That is a rough measure of how repeatable the labels are.
- Quote check: 495 House news statements; 469 found word for word on the linked page, 25 not found, 1 page not downloadable.
- Draft House grades (427 members; machine-drafted by rule, unreviewed, letter levels provisional): A 29, B 91, C 42, D 211, F 7, nothing found 47. Democrats A 27, B 88, C 25, D 60, none 13; Republicans A 2 (Crane, Barrett), B 3, C 16, D 151, F 7 (McClintock, Steube, McCormick, Stutzman, Massie, Mike Johnson, Fallon), none 34; Independent C 1.
- 88 members' top level comes only from a co-signed letter (77 at B from the 107-signer letter, 11 at C). Three were lowered a letter for a dismissive statement (Cammack, Mace, Ogles).
- Positions: slowdown yes 22, mixed 4, no 10; pause yes 3, mixed 14, no 11; China coordination yes 9, mixed 1, no 2; self-improving AI ban yes 11, mixed 1.
- Render check: "427 House records; 117 Senate-side records; 544 people rendered". Checked in headless Chrome: clicking the House switch shows 427 rows, no map, and the House chart; one member page (Liccardo) screenshotted.

**Open questions / known problems**
- Oz's rulings on the five letters; until then House grades resting on letters are provisional (about 90 members move with the 107-signer letter).
- House records have a generic sentence after the grade, not a written summary like the senators'.
- No House portraits fetched. No "lame duck" or "representative-elect" marks for the House. The six senators-elect who sit in the House appear only on the Senate side.
- The House grade rule is applied by code; the Senate rulings were applied by hand. The two could differ in edge cases.
- Self-improving AI ban "yes" for 11 members mostly rests on co-sponsoring H.R. 10538, known only from third-party trackers that disagree.
- 32 House members have no usable X account on file; personal and campaign accounts not searched.
- Every quote still needs a human check. Nothing from the House is committed.

**Next steps**
1. Oz rules on the letters; rerun `site/house_records.py` and the build.
2. Decide how to spend the remaining X budget (about $47): missing accounts and personal or campaign accounts.
3. Written summaries and portraits for the House; commit.

## 2026-11-14 (evening): representatives-elect sourced, searched and added to the site

**Goal:** Per Oz ("Continue, source the members elect"): find the winners of the 3 November 2026 House elections who are not sitting members and give them records.

**What was done**
- Election results: 17 Opus 5.5 subagents, one per group of states (Workflow run wf_92e09006-a64, about 1.4 million tokens), following new `classify/house_election_brief.md`, wrote `data/house/elections/group_01..17.json`: one row per district with winner, party, status and a source link.
- `data/house/merge_elections.py` (new) combines and checks them: `python3 data/house/merge_elections.py --results data/house/elections --roster data/house/roster.csv --out data/house/election_2026.csv --elect data/house/members_elect.csv --leaving data/house/not_returning.csv`. NOTE: rerunning it rewrites `members_elect.csv` without the `id` column that was added afterwards by hand-run code; write `--elect` to a scratch path unless the ids are regenerated (ids are ELECT-<state>-<district>-<LASTNAME>).
- News searches for the 108 representatives-elect (run wf_063d128d-a47, Opus 5.5, about 7.1 million tokens, no search refused), with a new section in `classify/news_search_house.md`. Files: `data/news_house/ELECT-*.json`; all pass the format check and list six or more searches.
- Site: `site/house_records.py` takes `--elect` and `--leaving` and marks "representative-elect" and "lame duck"; `site/build.py` passes those marks to the page; the House view has a current/next House choice for the bar chart. Build as before, with `--elect data/house/members_elect.csv --leaving data/house/not_returning.csv` added to the `house_records.py` command.

**Results**
- 435 districts, each once: 426 called (257 Democrat, 169 Republican), 7 uncalled (AK at large, CA-23, MN-1, NC-5, NC-7, NC-10, TN-4), 2 runoffs (LA-5, LA-6). Unofficial results. Searchers' cautions: 13 Florida seats rest on one law-firm summary with at least one error; some KY, IN, SC rows come from search excerpts; Illinois count of new members disagrees with one news report (5 vs 6).
- 108 representatives-elect; 318 sitting members returning; 115 sitting members not among the winners, of whom 9 sit in undecided districts and are left unmarked, and 6 are senators-elect. 101 House records are marked lame duck.
- Members-elect draft grades (news only, no X posts): A 2 (Will Lawrence MI-7, Sam Forstag MT-1), B 2 (Scott Wiener CA-11, Micah Lasher NY-12), C 1 (Manny Rutinel CO-8), D 46, nothing found 57.
- House page totals (535 records): current House A 29, B 91, C 42, D 211, F 7, none 47; next House (434 listed) A 29, B 82, C 33, D 192, F 6, none 92.
- Render check: "652 people rendered; Senate: 17 senators-elect, 17 lame ducks; House: 108 representatives-elect, 101 lame ducks". Clicked through to the next House in headless Chrome.

**Open questions / known problems**
- The election table is a working list, not a verified roster; a person should check it against certified results, and the 9 undecided seats need revisiting.
- No X posts for members-elect (no account list). Quote check for the 108 new files was started and is applied on the next build.
- Still open from before: Oz's rulings on the five letters; remaining X budget (about $47); written summaries and portraits for the House; nothing from the House is committed.
- Quote check rerun on all House files including members-elect (replaces the earlier output at data/news_house_quote_check.csv); site rebuilt and render check passed.

## 2026-11-14 (night): second check of unverified quotes

- Per Oz: 13 Opus 5.5 subagents (Workflow run wf_3c1c9120-6a8, about 0.7 million tokens) rechecked the 60 quotes the automatic check had not confirmed (31 Senate, 28 House, plus one never-checked quote in Slotkin's hand-written record). Each downloaded the page itself and checked the wording in the raw text by script; summaries from fetch tools were not accepted.
- Results in `data/quote_review/group_*.json`, combined in `data/quote_review/results.csv`: 53 confirmed, 4 wording differs, 3 could not be opened.
- Why the automatic check missed the confirmed ones: PDFs it does not read, pages it failed to download, line wrapping, invisible characters inside the text, a script tag with a space that made the tag-stripper drop the article. Moreno's four quotes are from a scanned letter read by character recognition; worth a human look.
- Both build scripts take `--quote-review data/quote_review/results.csv` and label these 53 "found on the page by a second check run by a language model". Site rebuilt; render check passed (652 people).
- NOT yet changed, awaiting Oz: the 4 wording corrections (Khanna drops the word "also"; Frankel's quote stops mid-sentence; Scalise and Watson Coleman have a full stop where the page has a comma); Khanna's "civilizational extinction risk" date (source says 28 September 2026, record says 29, and the source is second-hand); the 3 that could not be opened (El-Sayed campaign page, Thune in Axios, Valdez on nysenate.gov), which need a person with a browser.
- Things the checkers noted about attribution: Blackburn's two quotes are from her office's bill summary; Kaine's, Schiff's and Frankel's are from joint letters; Capito's two quotes are cut from longer sentences.

## 2026-11-14 (late night): missing X accounts found, posts collected and labelled

- Per Oz: 24 Opus 5.5 subagents (Workflow run wf_8662e1a0-26a, about 1.6 million tokens) looked for X accounts of 141 people (108 representatives-elect, 33 sitting members without a working account). A handle counted only if a page the subagent opened linked it to the person. Results: `data/house/x_accounts_found/group_*.json`, 155 handles for 131 people; none found for 10 (Christopher H. Smith, and members-elect Dandiya, Cowan, LePage, Benitez-Thompson, Constantino, Leonard, Tedford, Gutierrez, Haynes).
- X lookup of the 155 (raw: `data/raw/user_lookup_names_20261115T030050.json`, `...030051.json`): 150 exist; 149 passed the automatic name check and DarializaforNY was added by hand. Not on X: repfeenstra, MannionforNY, wewill2026, jefferson_cyril, ChuckGrayWY. Added to `data/house/accounts.csv` as batch h3 (official, personal and campaign accounts).
- Posts: `python3 collector/search.py --accounts data/house/accounts.csv --batch h3 --db data/house/posts.sqlite --raw-dir data/raw --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 8000` -> 901 posts. Database: 4,739 posts from 455 accounts.
- Cost of this step: 155 lookups ($1.55) + 901 posts ($4.50), about $6.05. Running estimate about $49 of $90 (unconfirmed in the console).
- Labelling: 98 new files, 12 Opus 5.5 subagents (run wf_ffdc0676-9a1); earlier labels were checked to still match their inputs; merge -> "4739 posts written". House records redrafted, site rebuilt, render check passed (652 people).
- Results: 48 House grades changed, almost all upward from "nothing found" to D. Members-elect: A 7 (Wiener, Villegas, Kiros, Rutinel, Lander, Lawrence, Forstag), B 1, C 7, D 61, nothing found 32. Current House (427): A 32, B 89, C 45, D 216, F 7, none 38. Next House (434 listed): A 36, B 79, C 42, D 210, F 6, none 61.
- Known problem: subagents working at the same time shared one scratch folder, and three reported running or overwriting another's helper script. The merge check (every post present once, ids in order, quotes exact) passed, so files are well formed, but it cannot prove each file holds the labels its own subagent intended. Give each subagent its own scratch folder next time.

## 2026-11-15: Oz's rulings on two House letters

- **Goal:** apply Oz's levels for two of the five co-signed House letters.
- **What was done:** in `data/house/letter_levels.csv`, the China talks letter (18 Sep 2026, 29 signers) went from C to B and the letter to OpenAI (10 Aug 2026, 32 signers) from D to C, both marked "Oz, 15 November 2026". Reran `site/house_records.py` and `site/build.py` (same commands as the previous entry) and `python3 site/render_check.py site/index.html`.
- **Results:** render check passed (652 people). House grades are now A 39, B 95, C 47, D 277, F 7, none 70. Five members moved from C to B, all through the China letter: Jim Costa, Debbie Wasserman Schultz, Bradley Scott Schneider, Dina Titus, Gregory W. Meeks. The OpenAI letter changed no grade: every signer already had C or higher from something else.
- **Open questions:** the other three letter levels are still provisional (107-signer letter B, hearings letter C, warning-shots letter C). Whether the China letter counts as a position on coordinating with China is still my provisional "no"; its full text has not been read (download refused). Nothing since commit `36801e9` is committed.
- **Next steps:** Oz to rule on the remaining three letters; quote wording fixes; decide on commit.

## 2026-11-15 (later): remaining letter levels confirmed, House work committed

- **What was done:** Oz confirmed the other three letter levels (107-signer letter B, hearings letter C, warning-shots letter C); `data/house/letter_levels.csv` now marks all five as Oz's. The note on each House page now says the letter levels were set by Oz. Redrafted and rebuilt with the same commands; render check passed (652 people); grades unchanged (A 39, B 95, C 47, D 277, F 7, none 70). Committed the House work.
- **Left out of the commit, as on the Senate side:** `data/house/classify/` (X post text and labels) and `site/house_records.json` (generated; contains X post text), both added to `.gitignore`, alongside the already ignored database, raw downloads and built page. They can be regenerated only from the local database and label files, which exist only on this machine.
- **Open questions:** whether the China letter counts as a position on coordinating with China (currently no); quote wording fixes; three quotes whose pages could not be opened; X display terms still unread.

## 2026-11-15 (afternoon): policy position chart and zip code lookup

- **Goal:** a bar chart of stated policy positions with a switch between the four policies, and a zip code lookup ("See where your members of Congress stand").
- **What was done:**
  - `xrisk-record.html`: `viewPolicyHist()` (bars for Yes / No / Mixed / Not stated; buttons `data-policy` choose the policy; follows the chamber switch and the current/next switch). Zip code box on the index page, and the search box also accepts a five-digit zip code (`zipDistricts`, `matches`).
  - `site/make_zip_districts.py` (new) turns the Census Bureau table of zip code areas against districts of the current (119th) Congress into `site/zip_districts.json`. Download: `curl -o data/raw/census/tab20_cd11920_zcta520_natl.txt https://www2.census.gov/geo/docs/maps-data/data/rel2020/cd-sld/tab20_cd11920_zcta520_natl.txt` (kept in the ignored `data/raw/`). Command: `python3 site/make_zip_districts.py --table data/raw/census/tab20_cd11920_zcta520_natl.txt --min-share 0.01 --out site/zip_districts.json`. Output: "33585 zip codes written ... 5140 are in more than one district | 871 small overlaps left out".
  - `site/build.py` has a new required `--zips site/zip_districts.json` (add it to the build command in earlier entries). `site/render_check.py` now checks that the policy bars add up to the members shown for each chamber, Senate/House and policy, and that zip codes 10001, 99501, 05401 and 90210 list two sitting senators and the expected number of representatives, with no representative-elect, and that an unknown zip code is handled.
- **Results:** render check passed (652 people). Looked at screenshots of the policy chart and of a lookup for 90210 (Padilla, Schiff, Lieu, Sherman). Current Senate: slowdown yes 23 / no 10 / mixed 7 / not stated 60; pause 2 / 9 / 17 / 72; coordination with China 21 / 2 / 4 / 73; self-improving AI ban 0 / 0 / 0 / 100. Current House (427): slowdown 23 / 10 / 4 / 390; pause 3 / 11 / 14 / 399; China 9 / 2 / 1 / 415; self-improving AI ban 11 / 0 / 1 / 415. Built page grew from 2.2 to 2.8 MB.
- **Open questions / known problems:**
  - A zip lookup shows sitting representatives only. Representatives-elect are left out because the table has the current district lines and some states used new lines in the 2026 elections; which states is not something I have verified. Senators-elect are shown (statewide).
  - Census zip code areas are not exactly postal zip codes; post-office-box-only zip codes are missing. About 15% of zip codes are in more than one district, and the page then lists every district's representative and says so. Overlaps under 1% of a zip code's area are dropped (my choice of threshold).
  - A zip code in the district of one of the six House members who are senators-elect shows them as a senator-elect, not as the sitting representative.
  - Not committed.

## 2026-11-15 (later afternoon): charts side by side; why no senator has a self-improving AI ban position

- **What was done:** `xrisk-record.html`: grade chart and policy chart now sit side by side (`.charts` grid; one column under 820px wide), captions moved above the bars so both charts share a baseline. Rebuilt with the same command (including `--zips`); render check passed (652 people); looked at a screenshot.
- **Self-improving AI ban, Senate (all 100 sitting senators "not stated"; only senator-elect El-Sayed is "yes"):**
  - The Senate news searches did ask about this policy and found nothing for 111 of 112 people. The Senate X post labels never covered it (no column for it).
  - Sanders: read the text of his Ban Artificial Superintelligence Act (S. 5493; PDF from sanders.senate.gov, text extracted with PyMuPDF into the session scratchpad). The words "recursive self-improvement" appear once, inside the definition of a "mandatory pause". But the bill lists "the capacity to automate or greatly accelerate the process of artificial intelligence research and development" as a "superintelligence precursor characteristic", bars deploying or releasing systems that may foreseeably be modified to show such characteristics, and has the Secretary pause any system showing them and render it inoperative within 30 days if that cannot be fixed (section 10). No quote of Sanders's own about self-improving AI was found (Semafor, Common Dreams, his press release); Rep. Casar says "Our bill bans recursive self-improvement" (X, 23 Sep 2026).
  - Inconsistency found: the House side counts co-sponsoring H.R. 10538, the House version of this same bill, as "yes" (most of the 11 House "yes"), while Sanders, its Senate sponsor, is "not stated". Senate co-sponsors of S. 5493 are unknown (congress.gov refuses downloads).
  - Text search of all collected posts found one senator post: Cassidy, 12 Oct 2026, "Restrict recursive self-improvement, self-generated goals, and open-ended autonomy." https://x.com/SenBillCassidy/status/2109671658340429847 . In the House posts: Foster, Krishnamoorthi, Harrigan (monitoring bill, not a ban) and Casar.
- **Open questions for Oz:** does sponsoring or co-sponsoring this bill count as "yes" on the self-improving AI ban (then Sanders is yes, and Senate co-sponsors need finding)? Is Cassidy's "restrict" a yes or mixed? Nothing changed in the records yet.

## 2026-11-15 (evening): Oz's rulings on the self-improving AI ban

- **Rulings (Oz, 15 Nov 2026):** sponsoring or co-sponsoring the Sanders–Casar Ban Artificial Superintelligence Act (S. 5493 / H.R. 10538) counts as "Yes" on the self-improving AI ban, with the note saying it rests on the bill. Cassidy's "Restrict recursive self-improvement" post is "Mixed".
- **What was done:** Sanders' entry in `xrisk-record.html` changed from not stated to Yes (sources: bill text, Casar's post, Semafor). `data/news/C001075.json` (Cassidy) position changed to Mixed with the post as source. Rebuilt with the same command; render check passed (652 people).
- **Results:** current Senate on this policy: yes 1 (Sanders), mixed 1 (Cassidy), not stated 98.
- **Open questions:** Senate co-sponsors of S. 5493. Third-party bill trackers found by one web search name Sanders alone, but congress.gov could not be opened, so this is not verified. Any co-sponsor would become "Yes" under the ruling.
- **Update, same day:** Oz checked congress.gov: S. 5493 has no Senate co-sponsors. Sanders stays the only senator at "Yes" on the self-improving AI ban. Not committed: the policy chart, zip code lookup, side-by-side charts, and the Sanders and Cassidy changes.

## 2026-11-15 (night): Oz's sign-off decisions applied

- **Rulings (Oz, 15 Nov 2026):** Warner stays C. Methodology must say a dismissive statement costs one letter. Apply the four quote wording fixes. Khanna's date left as is. Oz opened and confirmed the three quotes whose pages would not download (El-Sayed, Thune, Valdez). The China talks letter counts as Mixed on coordination with China for its signers. X display terms: Oz says it is OK. X spend confirmed by Oz: $45 of $90. Oz checked the new House A grades and signs off on the House; methodology to say Senate grades were all reviewed by a person and House members only roughly checked. Ossoff is B on the strength of his 13 Sep 2026 rally speech (https://x.com/Acyn/status/2099232674850517158).
- **What was done:**
  - `xrisk-record.html`: banner and methodology reworded (rulings on dismissal and misuse-only added; "What a person has reviewed" paragraph).
  - `data/quote_review/results.csv`: the four "wording differs" rows now hold the corrected quote and are "confirmed"; the three "could not open" rows are "confirmed_by_person". The four news files (Frankel, Khanna, Scalise, Watson Coleman) carry the corrected wording. `site/build.py` and `site/house_records.py` show "checked against the source by a person" for the three.
  - `data/house/letter_levels.csv` has new columns `position_field`, `position_value`, `position_note`; `site/house_records.py` gives signers that position when they have none of their own (own stated position is kept). Result: coordination with China in House records is now yes 11, no 2, mixed 23, not stated 499.
  - Ossoff: post text read through the X API (one post lookup); statement added to `data/news/O000174.json` at level B; `data/grade_overrides.csv` and `data/summaries.csv` updated. The model did not watch the video; the transcript is the poster's.
  - Record notes: Senate drafted records now say the grade was reviewed by a person; House records say "only roughly checked by a person".
- **Results:** render check passed (652 people). House grades unchanged (A 39, B 95, C 47, D 277, F 7, none 70).

## 2026-11-15 (late): portraits; zip lookup now covers representatives-elect

- **Portraits:** `sh site/fetch_photos_house.sh` (new; same sources as the Senate script) downloaded official portraits for all 433 sitting House members (415 from unitedstates/images, 12 from the Biographical Directory, 6 already there) into `site/img/`. Representatives-elect have none. The assistant did not look at the images. NOT committed (about 70 MB); Oz to decide.
- **Which states redrew districts for 2026** (subagent; Census Bureau congressional districts page plus a block-by-block comparison of the Census block assignment files for the 119th and 120th Congress): Alabama, California, Florida, Louisiana, North Carolina, Ohio, Tennessee, Texas, Utah. Missouri's new map was blocked and its 2026 elections used the old lines. No Census zip code table for the 120th Congress exists yet ("coming in 2027").
- **Next-House zip table:** `site/make_zip_districts_blocks.py` (new) adds up census block areas using the Census block-to-zip-code-area table and the 120th Congress block assignment file (download commands in the script's header; raw files in the ignored `data/raw/census/`, about 1.6 GB). Command: `python3 site/make_zip_districts_blocks.py --blocks-to-zips data/raw/census/tab20_zcta520_tabblock20_natl.txt --block-districts data/raw/census/bef_cd120/NationalCD120.txt --min-share 0.01 --out site/zip_districts_next.json`.
  - Method check: the same script run on the 119th Congress block file reproduces `site/zip_districts.json` exactly (all 33,585 zip codes, same districts).
  - 3,032 zip codes change districts in the next House: Texas 786, California 633, Ohio 334, Florida 333, Tennessee 292, Louisiana 217, Utah 207, Alabama 125, North Carolina 100, plus 5 border zip codes filed under Nevada and Idaho that reach into Utah.
- **Site:** `site/build.py` has a new required `--zips-next site/zip_districts_next.json` (only the differing zip codes go on the page). A zip lookup now lists sitting representatives by current district and representatives-elect by the district used in the 2026 election, and says when the zip code's district changes. `site/render_check.py` also checks that every representative-elect can be reached from some zip code. Render check passed (652 people).
- **Full build command is now:** `python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --news data/news --quote-check data/news/quote_check.csv --quote-review data/quote_review/results.csv --status data/status.csv --summaries data/summaries.csv --relevance data/classify/relevance/output --map site/us_states.json --grade-overrides data/grade_overrides.csv --house site/house_records.json --zips site/zip_districts.json --zips-next site/zip_districts_next.json`
- **Returning members in redrawn states:** `site/house_records.py` has a new `--election data/house/election_2026.csv` (add it to the House command), which records the district each returning member won ("next" in the record; 318 members, 10 of whom won a different district number, e.g. Casar Texas 35 to 37, Maloy Utah 2 to 3). A zip lookup lists a returning member for the zip codes of the district they won as well as their current one. This rests on the election table, whose check is still running.

## 2026-11-15 (late): election table checked against an independent listing

- **What was done:** a subagent compared `data/house/election_2026.csv` with Wikipedia's 2026 House election articles (plus news pages for a few seats) and looked up the nine undecided districts. Output: `data/house/election_check.json`. The table itself was not changed.
- **Results:** 363 of 435 districts cross-checked. Winner and party agree in all 346 districts where Wikipedia names a winner. Five disagreements, all about whether a race is called, none about who won: MN-1 (Wikipedia marks the leader elected; news says uncalled, as in our table), CA-4, CA-7, FL-7 (Wikipedia says undecided; news reports calls, as in our table; for CA-7 and FL-7 the only second source is the table's own), AR-4 (Wikipedia field not filled in). Party totals match (257 D, 169 R, 9 undecided).
- **All nine undecided seats are still undecided on 15 Nov 2026:** AK at large (ranked-choice count 18 Nov), CA-23, MN-1 (canvass 19 Nov, recount expected), NC-5 (recount requests due 17 Nov), NC-7, NC-10, TN-4 (state count projects Broderick; not called by AP as far as found), LA-5 and LA-6 (runoffs, 12 Dec).
- **Known limits:** 72 districts could not be checked because Wikipedia's winner fields were blank (HI, most of IL, KS, MA, MS, NH, NM, parts of OR, PA, TX 26-38, VA-3, WA); they are mostly safe seats but unverified. Wikipedia is not official, and the pages were read through a tool that summarises them. The undecided seats need rechecking after 19 Nov and again after 12 Dec.

## 2026-11-15 (late): draft and "for review" wording removed from the site

- **Goal (Oz):** start removing the draft and for-review markers now that the content is converging.
- **What was done** (`xrisk-record.html`, `site/build.py`, `site/house_records.py`): top banner changed from "Draft for review ... Do not circulate" to a short "How this record is made" note linking to Methodology; footer now "Last updated 15 November 2026" (hand-written date; update it on each release); "drafted" dropped from the index labels and chart captions; per-record note heading "For review" is now "About this record" and no longer starts "Machine-drafted record"; methodology label is "Rubric version 0.2", "Still open" is "Known limits", and the line that every quote needs a human check before publication now says what checks quotes have had. Page text that named Oz now says "a human reviewer" (my choice, since the page is public; the data files' `ruled_by` columns still name him). Rebuilt; render check passed (652 people).
- **Kept on purpose:** each record's note on how it was made and what was checked; the Known limits section; Slotkin's "Possibly out of date ... needs a deeper search" note.
- Not committed.

## 2026-11-15 (evening): campaign and personal X accounts for sitting House members

- **Goal (Oz said yes to spending the remaining X budget; Oz reports actual spend was $45 of $90 before this step):** find campaign or personal accounts for the 401 sitting members who had only an official account, and collect their posts.
- **What was done:**
  - Pilot of 10 members (one subagent), then 40 Opus 5.5 subagents in waves of eight (Workflow run wf_6368a791-7d1, about 2.7 million tokens, one web search per person, 401 searches, none refused). A handle counted only if a page the subagent opened linked it to the person, in most cases the member's own campaign site. Results: `data/house/x_accounts_personal/group_*.json`; 309 new handles for 305 members (`new_handles.json`).
  - X lookup (raw: `data/raw/user_lookup_names_20261115T1741*.json`): 305 exist; not on X: EdCaseHawaii, foxxforcongress, BWatsonColeman, RonnyJackson4TX. Name check (`lookup_check.json`): 304 passed; TeamAOC failed the automatic check and was added by hand. Dropped by me as doubtful: MayorStanton (80 followers, found only on a third-party directory) and dannykdavis7 (7 followers). 303 accounts added to `data/house/accounts.csv` as batch h4.
  - Posts: `python3 collector/search.py --accounts data/house/accounts.csv --batch h4 --db data/house/posts.sqlite --raw-dir data/raw --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 6000` -> 793 posts. Database: 5,532 posts from 573 accounts.
  - Cost of this step by the reported rates: 309 lookups ($3.09) + 793 posts ($3.97) + one post lookup for Ossoff, about $7.10. Estimated total about $52 of $90; not confirmed in the console.
  - Labelling: the new posts were written to their own input files (`data/house/classify/input/<bioguide>_h4_<n>.json`, 120 files for 118 members) so existing labels are untouched; 11 Opus 5.5 subagents, each with its own scratch folder (run wf_bc6007aa-308).
- **Known limits:** every campaign-site link was labelled "campaign", though some are really personal accounts. About 96 members had no second account found; that means none was found, not that none exists.

## 2026-11-15 (night): new posts labelled; House summaries written

- **Labels:** 11 subagents labelled the 793 new posts (all check scripts passed); `python3 classify/merge.py --input data/house/classify/input --output data/house/classify/output --review data/house/classify/review_queue.csv` -> "5532 posts written".
- **Grades after the new posts:** A 40, B 94, C 48, D 279, F 7, none 67. Four changed: Patrick Ryan B to A ("a technology that could kill us all", campaign account, 6 Nov 2026), Brendan Boyle none to C, Keating and Gluesenkamp Perez none to D. Six positions changed: Liccardo slowdown none to no and China yes to mixed; McCollum slowdown yes, pause mixed; Deluzio China yes; Mace China no. Not reviewed by a person.
- **House summaries:** `classify/export_house_summary_digest.py` (new) wrote 12 digest files for the 468 House records with a grade (the 67 with nothing found keep the rule sentence); 12 Opus 5.5 subagents wrote the sentences following `classify/summary_prompt.md` plus `classify/summary_prompt_house.md` (new) (run wf_48553077-9b6); `python3 data/house/merge_summaries.py --parts data/house/summaries --digests data/house/classify/summary_digest --out data/house/summaries.csv` checked every row (name form, quoted words found in that member's statements, 20 to 70 words): 468 kept, 0 left out. `site/house_records.py` has a new `--summaries data/house/summaries.csv`; a sentence is used only while the record's grade is the one it was written for.
- **House command is now:** `python3 site/house_records.py --roster data/house/roster.csv --news data/news_house --letters data/house/letters.json --letter-levels data/house/letter_levels.csv --quote-check data/news_house_quote_check.csv --quote-review data/quote_review/results.csv --labels data/house/classify/review_queue.csv --elect data/house/members_elect.csv --leaving data/house/not_returning.csv --election data/house/election_2026.csv --summaries data/house/summaries.csv --out site/house_records.json`
- **Results:** render check passed (652 people). Read nine summaries; they matched their grades. The summaries have not been read by a person.
- **Known problems:** summaries use "they" for most members because the writers were told not to guess he or she. Writers flagged about 45 sentences they were unsure of (listed in the workflow result), mostly thin evidence behind a grade, e.g. representative-elect Constantino is D but said "I don't like the fear-mongering about it", which might be F; Ocasio-Cortez's "existential harm" names only everyday harms. If labels change, rerun the digest and summaries for the people whose grade moved.
- **Not committed:** everything since `a03da24` (zip lookup for the next House, draft wording removal, portraits, h4 accounts, summaries).

## 2026-11-15 (night): layout changes asked for by Oz

- `xrisk-record.html`: the "How this record is made" box moved from the top of every page to below the map and charts on the index page (it is not shown on member pages, the methodology page, or while searching). The grey method paragraph at the top of the House index is removed; its content about representative-elect and lame duck marks, uncalled seats and the six senators-elect now sits in the note under the House table. The "About this record" box is removed from every member page (the per-record notes are still in the data as `flag`, just not shown; this includes Slotkin's "possibly out of date" note). Rebuilt; render check passed (652 people); looked at screenshots of the House index and one member page. Not committed.

## 2026-11-15 (night): methodology page edits asked for by Oz

- `xrisk-record.html`: "Silence is not dismissal." removed from the no-statement rubric row; "It does not rate whether their policies are good." removed from the intro; "Grades are then reviewed by a human." added after the sentence on the language model; the "Known limits" (formerly "Still open") bullets removed; new "Contact" section ("Found a mistake? Or think we've missed something? Let us know") with the PLACEHOLDER address contact@example.com (constant `CONTACT_EMAIL`; Oz will supply a real one) and a credit line linking https://ozamram.github.io/. Constantino stays D (Oz). Rebuilt; render check passed. Not committed.
- **Follow-up, same evening (Oz):** methodology intro line no longer wraps on a desktop-width screen (it still wraps on narrow screens); the post count now covers both chambers (8,384 = 2,852 Senate + 5,532 House; `site/house_records.py` stores each member's post count as `posts`); the source policy names house.gov beside senate.gov; the "reviewed by a human" sentence now says every Senate grade is reviewed by a person and House grades are worked out by rule and only roughly checked. Rebuilt; render check passed; looked at screenshots of the whole methodology page including the new Contact section. Not committed.
- **Further edits (Oz):** removed from the methodology page the grade-colour note, the count of quotes resting on an "other outlet" source, and the line that such quotes must be replaced before publication. The "Other outlet" line now ends "Used where no better source was found." (my wording, replacing "Usable as a lead only", which no longer matched the site). Rebuilt; render check passed. Not committed.
- **Further edits (Oz):** methodology no longer says hand-changed Senate records "say so" (the per-record box was removed, so they do not). Ossoff's stored reason in `data/grade_overrides.csv` shortened to the rally-speech sentence. Rebuilt; render check passed. Not committed.

## 2026-11-15 (night): Senate records compared with another site (legimon.pages.dev)

- **Goal (Oz):** double-check our Senate quotes and grades against https://legimon.pages.dev/ (a trading-card site covering the January 2027 Senate, with a 1-5 "stance" level, a summary and one quote per senator). Nothing on our site was changed.
- **What was done:** downloaded the page (its data is embedded in the HTML; 98 people) into the session scratchpad and compared with our 117 Senate-side records by script. Their scale is not ours: it runs from "Dismisses the risk" (1) to "A top priority" (5) and rewards legislating; I mapped under 2 to F, 2 to D, 2.5-3 to C, 3.5-4 to B, 4.5-5 to A (my mapping).
- **Results:**
  - 96 people matched. Same band for 46, within one band for 76. We are two or more bands higher for 20, nearly all Democrats who signed the 23 Sep 2026 letter (we count it as A; they give 3 and note the words are the letter's). We are never two or more bands lower.
  - Notable individual gaps: Rick Scott (ours A on one post, theirs 2), Murphy (A vs 2; theirs rests on 2023), Cooper (B vs 2), Pappas (A vs 2.5), Fetterman (C vs 1), Hawley (C vs 4), Reed (C vs 4), Schatz (B vs 5), Warner (C vs 4), Slotkin, Britt, Budd, Hassan, Jackson (D vs 3), Paul, Schmitt, Sheehy (F vs 2, they found no dismissal).
  - Quotes: of their 55 quotes for matched senators, we have 37 word for word, 1 is a trimmed version of ours (Kennedy), and 17 are not in our records. No quote of theirs contradicts ours. Ones we lack that matter: Flanagan "an existential threat to us if it gets out of control" (MPR News debate, 27 Jul 2026; we have her at B); Sanders "Scientists have been clear: AI is an existential threat to humanity" (joint release, 23 Sep 2026); Hassan on "catastrophic" risks (2023, before our window).
  - **Roster problems found in OUR data (checked with five web searches):** (1) Mississippi: news reports say Scott Colom beat Sen. Hyde-Smith; we list Hyde-Smith as continuing and have no record for Colom. (2) Alaska: Mary Peltola leads Sen. Sullivan; not called; ranked-choice count 18 Nov, certification 25 Nov; we list Sullivan as continuing. (3) Klobuchar was elected governor of Minnesota and Blackburn governor of Tennessee; both will leave the Senate in January and their seats will be filled by appointment; we list both as continuing. So our "next Senate" is wrong for two to four seats.
- **Next steps (for Oz to decide):** mark Hyde-Smith as a lame duck and add a record for Colom; decide how to show Alaska until it is called; mark Klobuchar and Blackburn as leaving with their seats shown as vacant pending appointment (the render check currently requires two senators per state in the next Senate); consider adding the Flanagan and Sanders quotes.

## 2026-11-15 (late night): Senate roster fixed; Colom added; Flanagan and Sanders quotes added

- **Rulings (Oz):** fix the roster; show Sullivan's race as undecided; add the Flanagan and Sanders quotes and move Flanagan to A.
- **What was done:**
  - `data/status.csv`: Hyde-Smith, Klobuchar and Blackburn marked lame duck (Hyde-Smith lost to Colom per news reports, not certified on 15 Nov; Klobuchar and Blackburn elected governor, seats to be filled by appointment); Sullivan marked with the new status "race undecided" (ranked-choice count 18 Nov, certification 25 Nov); Colom added as senator-elect. `site/build.py` accepts the new status; the template shows "Race undecided" and, on the next-Senate map, "One seat to be filled by appointment" for Minnesota and Tennessee. `site/render_check.py` now expects 100 current senators, 98 in the next Senate with one each for Minnesota and Tennessee, and 118 Senate-side people.
  - Scott Colom (id ELECT-MS-COLOM): news search by one Opus 5.5 subagent (10 web searches) -> `data/news/ELECT-MS-COLOM.json`, three statements, all D, all from his campaign site; X account @scott_colom confirmed by lookup (profile says "Senator-Elect"; the second handle on his site, colomsw, does not exist on X); added to `data/accounts.csv` as batch 5; `python3 collector/search.py --accounts data/accounts.csv --batch 5 --db data/posts.sqlite --raw-dir data/raw --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 300` -> 12 posts (Senate database now 2,864); labelled by a subagent (10 D, 2 off topic, no positions); merged. Relevance choices for his 10 D posts written by me to `data/classify/relevance/output/chunk_6.json` (4 shown: his own views on data centers; 6 campaign attacks not shown). Quote check run on his file and Flanagan's and appended to `data/news/quote_check.csv` (5 found; one Colom quote not found by the script, shown as read by a model). Summary sentence written by me in `data/summaries.csv`.
  - Flanagan: MPR News debate quote of 27 Jul 2026 added to `data/news/ELECT-MN-FLANAGAN.json` at level A (a web-fetch subagent confirmed it is a direct quote); summary rewritten; grade now A.
  - Sanders: "Scientists have been clear: AI is an existential threat to humanity." (Casar-Sanders release, 23 Sep 2026, attributed "Senator Sanders said") added to his hand-written record in `xrisk-record.html`.
- **Results:** render check passed (653 people). Current Senate: A 27, B 12, C 19, D 36, F 5, none 1. Next Senate (98): A 30, B 12, C 13, D 39, F 4. Looked at a screenshot of Colom's page.
- **Open questions / next steps:** recheck Alaska after 18 Nov (if Peltola wins she needs a record and Sullivan becomes a lame duck); Mississippi certification; appointees for the Minnesota and Tennessee seats; an August 2026 candidates' pledge on AI safety reviews that Colom may have signed (signer list not found). X spend estimate about $52.3 of $90. Nothing since `a03da24` is committed.

## 2026-11-15: independent repository and web-source review

- **Goal:** review errors and oversights without changing site content or grades.
- **What was done:** reviewed builders, template, generated artifact, classification and quote-check logic; checked selected claims through web search and primary sources. Detailed findings and sources are in `REVIEW.md`.
- **Results:** existing generated site fails `python3 site/render_check.py site/index.html` (next Senate 100 versus expected 98). A full build directed to `/tmp/congress-review-index.html` fails on a missing Colom relevance decision for post 2101000279982223519. Generated script inspection found 427 current House records, six sitting representatives moved entirely to the senators-elect category, stale Flanagan B, and 22 House China-coordination Mixed labels whose explanations say the letter does not request pacing. The House recency rule discards all older evidence whenever any 2026 statement exists. Web checks confirmed the September 23 letter's pause language and existential framing, Flanagan's July existential-risk quote, Sanders' bill release, and Colom's election win. This was a targeted audit, not a comprehensive quote or election audit.
- **Next steps:** resolve missing classification and rebuild; correct current/next-office representation; decide and document consistent recency and policy-position rules. No site data, grades, or application code changed in this review.

## 2026-11-15 (after the outside review): fixes from REVIEW.md

**Goal:** Oz had another model review the project (`REVIEW.md`). Act on it: make the House recency rule match the Senate, stop the China talks letter counting as a position, and do five agreed fixes (six missing representatives, quote label, methodology wording, skipped searches).

**What was done** (all on top of commit `a03da24`, nothing committed):
- **Review findings 1 and 3 were already fixed** when I read it: the review saw the site part-way through the roster work. The render check passes.
- **House recency rule** (`site/house_records.py`): every statement since 1 January 2025 now counts. Before, any 2026 statement made older ones stop counting.
- **China talks letter** (`data/house/letter_levels.csv`): no longer gives a position on coordination with China (Oz reversed his ruling of the same day). The letter still counts as a B statement.
- **Six sitting representatives who are senators-elect** (Barr, Hageman, Hern, Letlow, Moore, Pappas): `site/build.py` has a new option `--house-roster data/house/roster.csv` that gives their Senate-side record a `house` field (their current district). The template counts them in the current House (list, charts, counts) and finds them by zip code in their district. `site/render_check.py` checks all of this.
- **Quote label:** "read at source" and "quote checked against the source by script" both became "wording found on the source page". The Verification paragraph now says the script check does not confirm speaker, date or context.
- **Methodology wording:** the B rubric line no longer lists bioweapons; the dismissal ruling says a D can be a C lowered one letter; D statements are described as filling leftover places; the recency ruling describes the two chambers separately.
- **Skipped searches rerun:** 20 Senate-side news files had web searches that never ran. One Opus subagent per politician (instructions in the scratchpad, results saved to `data/news_rerun/<id>.json`), merged with the new script `classify/merge_rerun.py`. 132 searches ran, none refused. The 13 new quotes were run through `classify/check_news_quotes.py` and the rows appended to `data/news/quote_check.csv`.

Commands:
```
python3 classify/merge_rerun.py --results data/news_rerun --news data/news --date "15 November 2026"
python3 site/house_records.py --roster data/house/roster.csv --news data/news_house --letters data/house/letters.json --letter-levels data/house/letter_levels.csv --quote-check data/news_house_quote_check.csv --quote-review data/quote_review/results.csv --labels data/house/classify/review_queue.csv --elect data/house/members_elect.csv --leaving data/house/not_returning.csv --election data/house/election_2026.csv --summaries data/house/summaries.csv --out site/house_records.json
python3 site/build.py --labels data/classify/review_queue.csv --accounts data/accounts.csv --template xrisk-record.html --out site/index.html --since "1 January 2025" --news data/news --quote-check data/news/quote_check.csv --quote-review data/quote_review/results.csv --status data/status.csv --summaries data/summaries.csv --relevance data/classify/relevance/output --map site/us_states.json --grade-overrides data/grade_overrides.csv --house site/house_records.json --house-roster data/house/roster.csv --zips site/zip_districts.json --zips-next site/zip_districts_next.json
python3 site/render_check.py site/index.html
```

**Results:**
- House grades: A 41, B 93, C 51, D 276, F 7, none 67. Four changed: Lieu B to A; Moolenaar, Davidson and Perry D to C. Their written summaries were for the old grade, so their pages now show the rule sentence.
- 22 House records went from Mixed to no stated position on coordination with China.
- Current House now shows 433 sitting representatives (427 plus the six). Render check: 653 people, passes.
- Search rerun: no Senate grade changed. 13 new statements (El-Sayed 3 at A and 1 at B; Blunt Rochester 1 at C; 8 at D for Barr, Jackson, Alme, Heinrich, Letlow). 12 of the 13 quotes were found on their pages by the script; one El-Sayed quote was not.

**Open questions / known problems:**
- **The two chambers still differ on recency.** Oz's hand rulings in the Senate put Budd, Risch, Blackburn and Lankford at D because their stronger statement was from 2025. The House rule now counts 2025 statements in full, so Moolenaar, Davidson and Perry are C for the same pattern. Oz should pick one.
- Letlow: a Louisiana Illuminator article (5 October 2026) says in the reporters' words that she "doubted AI poses a true threat to humankind". No direct quote, so not used; her own words would make it F.
- Jackson: the American Prospect (16 October 2026) paraphrases him saying the AI race "needs to slow down or stop". No direct quote, so positions unchanged.
- Flanagan: KAXE (30 October 2026) says she "has hinted at a potential pause". No direct quote.
- Blunt Rochester's new C quote is a boundary case (could be D); it does not affect her A.
- Sullivan's file still lists one search as not run (the China letter signer list); the list is verified elsewhere and he is not on it.
- Not done from the review: Yes plus Mixed still gives Yes in the Senate and Mixed in the House; Senate summaries are not tied to a grade; search-coverage limits are not shown on pages; `classify/rubric_prompt.md` still lists bioweapons under B; contact email is still a placeholder.

**Next steps:** Oz to decide the recency question and whether to commit (and whether the 70 MB of House portraits go in).

**Later the same day: old House recency rule restored (Oz).** The change above to count every statement since 1 January 2025 was undone, because Oz's hand rulings in the Senate (Budd, Risch, Blackburn, Lankford at D) follow the old rule: if there is any 2026 statement, only 2026 statements count. House grades are back to A 40, B 94, C 48, D 279, F 7, none 67 (Lieu B; Moolenaar, Davidson, Perry D), all 468 written summaries are in use again, and the methodology line reads as before. The "two chambers still differ" problem listed above no longer applies. Everything else in this entry stands. Render check passes (653 people). Checked: the Yes plus Mixed difference between the builders affects no one today (only Sanders has both in his posts, and his record is written by hand).

**Two more fixes from the review, then committed (Oz asked for both).**
- **Yes plus Mixed:** `site/build.py` now gives Mixed when a senator's X posts on one policy include a Mixed label, as `site/house_records.py` already did. No page changed (only Sanders has both labels, and his record is written by hand).
- **Senate summaries tied to a grade:** `data/summaries.csv` has a new `grade` column (the grade each sentence was written for) and the build stops, naming the people, if a record's grade differs. The column was filled from today's grades, which assumes each sentence matched its grade today; a rough check (sentences opening "has not acknowledged" against grade D) found no mismatch, but no one reread all 113. Tested by changing one grade in a copy: the build stopped as intended.
- Render check passes (653 people). House portraits (`site/img/`, about 70 MB of new files) are still left out of git, pending Oz's decision.

## 2026-11-15 (evening): getting ready to host

**Goal:** prepare to publish on Cloudflare Pages. Oz bought `airiskrecord.org` and `congressonairisk.org`.

**What was done** (not committed):
- `site/make_public.sh`: runs the render check, then copies the page, the preview image and the portraits into `public/` (535 files, 90 MB; `public/` is in `.gitignore`).
- Link preview: `site/preview_card.html` and `site/make_preview.sh` make `site/preview.png` (1200 x 630); `xrisk-record.html` has the description, canonical address and preview tags.
- Node.js installed with Homebrew (v26.13.1) so the site can be published from the command line with Cloudflare's tool (`npx wrangler pages deploy public --project-name <name>`).

**Assumption to confirm:** the preview tags use `https://airiskrecord.org/` as the main address, with `congressonairisk.org` redirecting to it.

Contact address set to `contact@airiskrecord.org` (Oz); it needs email forwarding set up on the domain before it receives mail.

**Open:** the preview has not been tested on a live address (it can only be tested once the site is up); portraits are larger than needed.

**Next steps:** Oz creates the Cloudflare account and Pages project and runs the first publish; then attach the domains and email forwarding.

**First publish and a character bug (same evening).** Oz published to a Cloudflare Worker (test address `long-scene-4494.<account>.workers.dev`); `wrangler.jsonc` in the project root holds the settings, so publishing is `bash site/make_public.sh && npx wrangler deploy`. The live page showed a stray "Â" before every "·" and similar marks: the template never declared its character set (the earlier preview tool added that for us). Fixed by starting `xrisk-record.html` with a doctype, `<html lang="en">`, a UTF-8 declaration and a viewport tag. Rebuilt, render check passes, index and a member page looked at in screenshots with the new declarations. Needs one more `npx wrangler deploy` to reach the live address.

**Live on the real domains (15 November 2026, evening).** Checked from the command line, connecting to the addresses the public name servers give: `https://airiskrecord.org/` serves a page byte-for-byte identical to `public/index.html` (render check passes on it, 653 people); the preview image and a portrait load; `congressonairisk.org` serves the same page directly (attached as a second domain, not a redirect). Email records for `airiskrecord.org` are in place (Cloudflare mail servers and sender record); delivery not tested. Found: neither `www.` address exists; plain `http://` is not sent on to `https://`; this Mac's own name lookup did not yet know the new domains when checked. The link preview has not been tested in a real app.

## Search results grouping, chart title, redirects (15–17 November 2026)

- **Goal:** small site polish after launch.
- **What was done:** (15 Nov) search results list senators first under a "Senate" band, then "House of Representatives"; while a search is showing the heading reads "What members of Congress have said…". (17 Nov) the grade bar chart now fills its column so the bars start right under the title, and its title is "How explicitly senators/representatives acknowledge catastrophic AI risk, by grade: current/next Senate/House". All in `xrisk-record.html`. Published with `bash site/make_public.sh && npx wrangler deploy` (17 Nov version 922d73e9-cf5f-45a9-b638-7addf762c97e).
- **Results:** render check passes (653 people); live page compared byte for byte with `public/index.html` after each deploy. `www.airiskrecord.org`, `congressonairisk.org` and `www.congressonairisk.org` all redirect to `https://airiskrecord.org/` (checked 15 Nov). Chart checked in desktop screenshots only, not at phone width.
- **Open questions:** everything since commit `394762e` is uncommitted. A similar site appeared, https://www.dconai.org/ (all of Congress, 0–4 scores from two AI models, only spot-checked by a person); it leaves Flanagan's existential-risk score blank where we have an A quote. Email delivery to contact@airiskrecord.org and the link preview are untested.
- **Next steps (Oz to decide):** compare their existential-risk scores with our grades as a list of leads; add a data download; commit.

## Contact details on each person's page (17 November 2026)

- **Goal:** show how to reach each sitting member on their page.
- **What was done:** downloaded `https://unitedstates.github.io/congress-legislators/legislators-current.json` to `data/contact/legislators-current.json` (17 Nov 2026, 539 people). `site/build.py` has a new required argument `--contacts data/contact/legislators-current.json` (add it to the end of the build command) and writes a `CONTACTS` table into the page; `xrisk-record.html` shows "Contact the Washington office: phone · contact form or official website" under the grade.
- **Results:** 533 of 653 people have a contact line; the 120 without are members-elect who hold no office yet (119 `ELECT` ids plus Sherrod Brown). Render check passes. Members of Congress do not publish email addresses, so the page links the contact form (the list has one for 86 senators and 2 representatives) or else the official website. Phone numbers and links were not spot-checked against the members' own sites. Checked one page (Pappas) in a screenshot.
- **Open questions:** not yet published to the live site; not committed.

## X accounts listed on each person's page (17 November 2026)

- **What was done:** `site/build.py` has a new required argument `--house-accounts data/house/accounts.csv` and writes an `ACCOUNTS` table (from it and `data/accounts.csv`); `xrisk-record.html` shows "X accounts searched: @handle (official) · …" with profile links at the top of the Statements section, or "No X account was found for this person." Build command now ends `… --contacts data/contact/legislators-current.json --house-accounts data/house/accounts.csv`.
- **Results:** 638 of 653 people have at least one account listed, 15 have none. Every handle that appears on an X-post statement is in the lists. Render check passes; one page (Pappas) checked in a screenshot.
- **Open questions:** the line says "searched" for every account in the lists; I did not confirm against the post databases that each listed account was actually collected. Not yet published or committed.

## Alaska Senate called for Peltola (18 November 2026)

- **Goal:** Oz: "Alaska has been called for Peltola, can you update?"
- **Check of the call:** two web searches. The Associated Press called the race on 17 November (NPR, NBC News, Alaska Public Media, Axios): Peltola 50.1% of first choices to Sullivan's 45.8%, so no ranked-choice count was needed. Not certified yet (due 25 November); the Justice Department is appealing a dismissed lawsuit about certification. The Alaska House seat (Begich v. Hill) was not found called as of the search; left as undecided.
- **What was done:**
  - `data/status.csv`: Sullivan (S001198) from "race undecided" to "lame duck"; new row for Peltola (id P000619, her bioguide id as a former representative) as senator-elect. Source NPR, 17 Nov 2026.
  - News search: one Opus 5.5 subagent, 10 web searches, none refused -> `data/news/P000619.json`: no statements, all positions none. It could not open an Alaska Beacon article (3 Nov 2026) on donations from AI-company employees.
  - X: lookup `python3 collector/lookup_users.py --raw-dir data/raw MaryPeltola Rep_Peltola RepPeltola MaryPeltolaAK PeltolaForAK` (3 found; RepPeltola is someone else). @MaryPeltola and @Rep_Peltola added to `data/accounts.csv` as batch 6; `python3 collector/search.py --accounts data/accounts.csv --batch 6 --db data/posts.sqlite --raw-dir data/raw --endpoint all --start-time 2025-01-01T00:00:00Z --max-query-len 1024 --max-posts 300` -> 10 posts (Senate database now 2,874). Cost by the reported rates about $0.08; running estimate about $52.4 of $90.
  - Labels written by me, not a subagent (`data/classify/output/P000619_1.json`): 9 D (data centers and energy costs, campaign attacks on Sullivan), 1 off topic; merge passed. Relevance choices written by me in `data/classify/relevance/output/chunk_7.json`: 3 shown, 6 not. Summary sentence written by me in `data/summaries.csv`. Portrait fetched to `site/img/P000619.jpg`.
  - `site/render_check.py` now expects 119 Senate-side people.
- **Results:** render check passed: 654 people; 19 senators-elect, 21 lame ducks. Peltola grade D. Looked at a screenshot of her page.
- **Open questions:** a person has not checked her three quoted posts against X; Alaska certification 25 Nov; Alaska House seat still to be updated when called; "race undecided" status is now unused but kept.

## Weekly update: X posts and news, 12 to 23 November 2026 (23 November 2026)

- **Goal:** Oz: "Can you update with new articles / tweets from this past week?"
- **X posts:** `python3 collector/search.py --accounts data/accounts.csv --db data/posts.sqlite --raw-dir data/raw --endpoint all --start-time 2026-11-11T19:00:00Z --max-query-len 1024 --max-posts 800` (134 returned, 133 new; database 3,007) and the same for `data/house/accounts.csv` / `data/house/posts.sqlite` from `2026-11-13T02:00:00Z` (209 returned, 186 new; database 5,718). Cost by the reported rates about $1.72; running estimate about $54.1 of $90, not confirmed in the console.
- **Labelling:** 9 Opus 5.5 subagents (4 Senate, 5 House files of the new posts only), each checking its own output. I rebuilt the output chunk files from old plus new labels; both `classify/merge.py` checks pass (3,007 and 5,718 posts). Re-running `export_chunks.py` for the House wrote plain `<id>_<n>.json` files that duplicated the 120 `<id>_h4_<n>.json` files from 15 Nov; after confirming all 793 labels were present unchanged, the 120 input and 120 output files were moved to the session scratchpad (not deleted).
- **Label changes I made, not yet reviewed by Oz:** Hassan post 2123171039387455785 B to C (misuse only; in `classify/overrides.csv`); Hickenlooper 2123494454187503668 slowdown yes to none ("considering a ban" on self-improvement); Casar 2122405017738977447 coordination yes to none (China not named); Ansari 2122548192390819886 C to D (bare call for a pause, no risk named; pause yes kept); McCormick 2122761963268939972 slowdown no to none (opposes the pause bill only); three Hamadeh staff posts C to D ("remains under our control" is ambiguous).
- **Relevance:** 17 new ordinary Senate posts judged by me in `data/classify/relevance/output/chunk_8.json` (14 shown, 3 not).
- **News:** not the per-person search. Three Opus 5.5 subagents swept the period's news by theme, 43 web searches, none refused. Curated results in `data/news_sweep/2026-11-23.json`; merged with new `classify/merge_sweep.py` (command in its header): 10 statements (Van Hollen 2 B, Hickenlooper 1 B, Hassan C, Schumer C, Kennedy C, Beyer 2 C, Whitesides C, Jacobs C) and 9 record items (House AI Safety and Innovation Caucus co-chairs, SAFE AI Act co-leads, Hassan's audit and hearing, Hickenlooper's letter, Van Hollen's video). Cruz's remark to the AP ("finding common ground on addressing catastrophic risk") added by hand to his record in `xrisk-record.html` at C. Quote check: 9 of 10 found on the page by `classify/check_news_quotes.py` (rows appended to both quote check files); Hickenlooper's letter is a PDF the script cannot read (the same sentence is in his own X post); the Cruz quote was found on the AP page by a direct download.
- **Results:** render check passes (654 people). Compared with the published build using `python3 site/compare_builds.py public/index.html site/index.html <scratch folder>`: 38 people gain statements; one grade changes (Hassan D to C, summary rewritten by me); no policy position changes. Senate grades otherwise unchanged; House A 40, B 94, C 48, D 279, F 7, none 67 (unchanged). Footer date set to 23 November 2026.
- **Open questions for Oz:** (1) Hickenlooper and Van Hollen both said to "consider banning" recursive self-improvement: is that Yes, Mixed or no position on the self-improving AI ban? Left as no position. (2) Hassan C (misuse only) or B? (3) Warren's post quoting Anthropic's "existential risks to humanity" was labelled A as an endorsed warning; she is already A. (4) Summary sentences were not rewritten for people whose grade did not change, so some do not mention this week's statements (Hickenlooper, Van Hollen, Sanders, Cruz). (5) The themed sweep is thinner than the per-person search and will have missed statements with little coverage. (6) Not published or committed yet.

### Follow-up the same day: Oz's rulings, Booker's thread, publication
- **Goal:** apply Oz's answers and publish the weekly update.
- **Oz's rulings (23 Nov 2026):** "consider banning" recursive self-improvement counts as **Mixed** on the self-improving AI ban (Hickenlooper, Van Hollen; set in `data/news/H000273.json` and `V000128.json`). Hassan stays **C** (misuse only). Publish now.
- **Booker:** Oz asked whether Booker's post on recursive self-improvement was included. It was not: his 22 Nov thread has six posts and the keyword search only returns posts containing a keyword such as "AI", so three were missed, including "We should rein in the race to recursive self-improvement". Added `--query` to `collector/search.py` and ran `python3 collector/search.py --accounts data/accounts.csv --db data/posts.sqlite --query "(from:SenBooker OR from:CoryBooker) -is:retweet" --start-time 2026-11-22T00:00:00Z --max-posts 100` (13 posts, about $0.07). Seven unrelated personal posts it returned were removed from the database again (raw response kept in `data/raw/`); database now 3,010 posts. I labelled the three thread posts (one C, two D) and set his self-improving AI position to Mixed ("rein in", not "ban") by analogy with Oz's ruling; Oz has not reviewed that.
- **Results:** render check passes (654 people). Against the previously published build: one grade change (Hassan D to C); self-improving AI ban none to Mixed for Booker, Hickenlooper, Van Hollen; 38 people gain statements.
- **Known problem:** the keyword search misses thread replies that do not repeat a keyword. Other members' threads may have the same gap; not checked.
