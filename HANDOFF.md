# AI Risk Record: handoff

Handoff from a planning session on 11 November 2026. Read this first, then `xrisk-record.html` (the prototype page, which also holds the data for five senators).

## Goal

A public website recording what US politicians have said about catastrophic and existential risk from AI. Each politician gets:

1. A letter grade for how explicitly they acknowledge the risk.
2. Yes / No / Mixed / No stated position on three policies: a pause, a slowdown, an international agreement that includes China.
3. Their most relevant statements, dated, quoted and linked to a source.

Scope for now: the US Senate (100 members). The House, governors and state legislators come later.

## Why this and not something else

Existing trackers cover AI policy broadly but none has an existential-risk dimension:

- AI on the Ballot (ontheballot.ai): 2026 congressional candidates, ten broad policy topics.
- AI Congress (aicongress.us): all senators and 140 House members; development, data centers, governance, workers, market power.
- Newsweek AI Policy Scorecard: all of Congress on a skeptic-to-booster scale.
- "What Washington Says About AGI" (LessWrong): scored existential-risk awareness, but a one-off post.

The gap is a maintained, per-politician record focused on catastrophic risk.

## Current state

- `xrisk-record.html`: single-file prototype. Index, five senator pages, methodology page. All data is in the `S` array in the script; rubric in `RUBRIC`; field definitions in `FIELDS`.
- Five draft records: Sanders (A), Blumenthal (B), Hawley (B), Cruz (C), Slotkin (C). These are first-pass drafts with no second human check.
- Nothing has been collected from X yet. Three quotes are X posts cited through news reports.

## Next task: collect posts through the X API

The decision is to use the X API to collect members' posts about AI, so every quote links to the post itself.

### What is known about the API (check all of it in the developer console)

- Pay-per-use since February 2026; the Basic and Pro subscriptions are being retired. No monthly minimum.
- Reported rates (third-party page, not confirmed officially): $0.005 per post returned, $0.010 per user lookup.
- Billed per post returned, not per request. The same post is billed once per day.
- Cap of 3 million post reads per month on pay-per-use.
- X's docs: https://docs.x.com/x-api/fundamentals/post-cap

### Not confirmed

- Whether full-archive search is available on pay-per-use, and its rate.
- Maximum query length, which sets how many `from:` accounts fit in one search.
- X's developer terms on storing and displaying post text. Read these before the site shows post content.

### Cost estimate (assumptions are guesses, not measurements)

Assumptions: about 1,000 accounts for all of Congress, 5 posts per account per day, 2% of posts about AI, 50 AI posts per member since January 2023.

- Pull everything: 1,000 x 5 x 30 = 150,000 posts per month x $0.005 = $750 per month. Rejected.
- Keyword search limited to member accounts: 150,000 x 2% = 3,000 posts per month x $0.005 = $15 per month. Backfill: 535 x 50 = 26,750 posts x $0.005 = about $135 once.

For the Senate only, divide by roughly five.

### Steps

1. Oz creates the X developer account, app and bearer token, and sets a spend cap (suggested $25) before buying credits. The agent does not create accounts or handle the token.
2. The token lives in the environment variable `X_BEARER_TOKEN`. Never print it, log it, or commit it. Put `.env` in `.gitignore`.
3. Build the account list. The `unitedstates/congress-legislators` repository on GitHub publishes social media handles; check that it is current. Include official and personal or campaign accounts, and record which is which.
4. Write the collector: keyword searches restricted to batches of member accounts. Save post ID, link, account, date, full text and the query that matched, in SQLite. Keep raw API responses too.
5. Pilot before anything large: the five senators in the prototype, last seven days. Compare the console charge with the estimate, and settle the unknowns above.
6. Backfill to January 2023 if archive search is available, then schedule a daily or weekly run.
7. Classify posts against the rubric with a language model. A person reviews anything that would set or change a grade.
8. Generate the site from the database instead of the hand-written `S` array.

### Keyword list (starting point)

AI, "artificial intelligence", superintelligence, AGI, "frontier AI", "AI safety", chatbot, OpenAI, Anthropic, "data center". Broaden after looking at what the pilot misses. Extra matches cost little.

## Rubric (draft v0.1)

| Grade | Criterion |
|---|---|
| A | Explicitly says AI could cause human extinction or permanent loss of human control. |
| B | Says advanced AI poses catastrophic risks (mass casualties, bioweapons, loss of control) without the extinction framing. |
| C | Acknowledges serious risks from advanced AI in general terms, or relays others' warnings without stating them as their own view. |
| D | Discusses only present-day harms (jobs, deepfakes, children, data centers). |
| F | Dismisses or mocks catastrophic risk. |
| None | No relevant statement found. Silence is not dismissal. |

The grade measures acknowledgment, not policy. A politician can acknowledge the risk and oppose every measure.

## Position fields

- **Pause:** a halt to building more capable frontier systems. A pause conditional on other countries joining, or on safety rules, is Mixed.
- **Slowdown:** slowing frontier capability progress for safety reasons. Data center moratoria motivated by electricity cost or local impact do not count.
- **International agreement including adversaries:** a safety agreement or treaty that includes China. Coordinating with allies to out-compete China does not count.

"No" requires a statement against the policy. Silence is always "No stated position".

## Open questions for Oz

These came out of the first five records and are not decided:

1. **Relayed warnings.** Hawley and Cruz cite experts' extinction warnings without endorsing them. The draft treats this as C.
2. **Bills and actions.** Does sponsoring a bill about loss-of-control scenarios count as a statement? Hawley is B only if it does.
3. **Co-signed letters.** Blumenthal's strongest language is in a 17-senator letter (23 September 2026). Full weight would make him an A and apply to every signatory.
4. **B/C boundary.** Cruz names catastrophic biological and nuclear risks while rejecting a slowdown. The wording arguably gives him a B.
5. **Staleness.** How old can a statement be before a record is marked out of date? Most useful evidence is from September 2026.
6. **Quote length.** Prototype quotes are under 15 words with one per source. That was a constraint of the drafting session, not a project decision. Oz should set the quote policy.

## Source policy

Tiers, best first: official record (senate.gov releases, letters, bill text, hearing video); transcript; major outlet; other outlet. "Other outlet" sources are leads only and must be replaced or dropped before publication. X posts should link to the post itself. Interviews and hearings should link to the recording with a timestamp where possible.

Known weak spots in the prototype:

- Sanders, 29 April 2026 panel quote: only found in Broadband Breakfast. Needs the event video.
- Sanders, 12 September 2026 X post: cited through Newsweek, seen in a search excerpt only.
- Blumenthal, CNBC interview: cited through IBTimes.
- Blumenthal, 9 September letter: cited from an archive copy, not blumenthal.senate.gov.
- Cruz, 9 September X post: cited through BizPac Review, search excerpt only.
- Cruz, The View: second quote cited through a CBS Austin affiliate.
- Hawley hearing transcript (Tech Policy Press): only the first part was read.
- Slotkin: nothing found on the September 2026 debate; her record needs a deeper search.

## Ground rules

- Every quote attributed to a named politician must be checked against its source by a person before publication. A fabricated or misattributed quote is the main way this project could discredit itself.
- Apply the same rubric and the same effort to every politician regardless of party.
- If a tax-exempt organization ends up hosting the site, grading candidates may raise election-activity rules. Ask a lawyer.
- Do not start the full backfill until the pilot's actual cost has been checked.

## Suggested layout

```
data/accounts.csv        member, chamber, party, state, handle, account type
collector/search.py      X API search, writes to SQLite
collector/pilot.py       five senators, seven days
classify/                rubric prompts and review queue
site/                    generator plus the prototype template
HANDOFF.md
```
