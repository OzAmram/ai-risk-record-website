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
