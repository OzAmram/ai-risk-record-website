# Review — 15 November 2026

Reviewed the source template, generated site, builders, classification and verification logic, research logs, and selected source claims using web search. This is a targeted audit, not verification of every politician or quote. No site content or grades were changed.

## Findings, in priority order

### 1. The generated website is stale, and rebuilding currently fails

`python3 site/render_check.py site/index.html` fails with `next Senate has 100 members, not 98`. The generated site still treats Hyde-Smith as continuing and omits Colom, although the source status table has been updated. The current check expects two seats awaiting appointment after the Minnesota and Tennessee gubernatorial elections.

A build using the full command recorded in NOTES.md, with output redirected to `/tmp/congress-review-index.html`, stops at:

`No relevance decision for https://x.com/scott_colom/status/2101000279982223519; run classify/export_relevance.py and judge the new posts`

Independent web check: [AP's explanation of the Mississippi call](https://apnews.com/article/7f098b8834f598c923ba73572ea2223f) confirms Colom defeated Hyde-Smith. Thus this is an actual roster error in the generated artifact, not just a changed test expectation. I did not independently recheck every election result.

**Recommendation:** complete missing classifications, regenerate the House intermediate file if necessary, rebuild the final site, and require the render check to pass before release. Preserve a build manifest with input dates and versions; the hand-written footer date currently does not guarantee fresh content.

### 2. Six sitting representatives disappear from the current House

Andy Barr, Harriet Hageman, Kevin Hern, Julia Letlow, Barry Moore, and Chris Pappas have been moved entirely to the Senate category as senators-elect. `site/house_records.py` skips their absent House news files. The `house`, `inHouse`, and `inSenate` functions in `xrisk-record.html` cannot represent someone who is simultaneously a sitting representative and senator-elect.

I evaluated the generated script: the current House contains 427 records. These six are excluded from it and also excluded from the current Senate. Their congressional statements remain accessible as individual records, but their grades and positions are missing from current-House aggregates and their constituents' sitting-representative ZIP results. The precise remaining difference from 435 requires checking vacancies separately.

**Recommendation:** represent current office and next office separately, sharing one person's evidence between the two views. Add checks that each sitting member is included in their current chamber and reachable through their current district.

### 3. Flanagan's generated B is contradicted by a directly sourced A statement

[MPR's July 27 debate report](https://www.mprnews.org/story/2026/07/27/angie-craig-peggy-flanagan-senate-race-debate-hosted-by-mpr-news) reports Flanagan describing AI as an existential threat if it gets out of control. That fits the published A ruling. The source JSON already contains the statement at A, but the generated website still shows B and omits that quotation.

This is another consequence of the stale build. Her source JSON's `grade_reason` also still says nothing found reaches extinction or loss-of-control framing, contradicting its newly added statement.

**Recommendation:** rebuild and update the stale explanation. Keep Senate summaries tied to the grade and evidence version they describe; unlike the House builder, the Senate builder inserts summaries without checking a stored grade.

### 4. A routine 2026 statement erases all older House acknowledgment

At `site/house_records.py:167–168`, the grading pool is all 2026 statements if any exist; otherwise all statements. This is stronger than the methodology's statement that recent statements count much more heavily.

For example, John Moolenaar's source file has a 2025 C statement about AI-enabled biological weapons, followed by 2026 D statements. The generated record is D. A later statement on another AI issue does not establish withdrawal of his earlier acknowledgment. Warren Davidson and Scott Perry also have generated D records with older C evidence. Andrew Ogles is a separate case involving a dismissal penalty.

**Recommendation:** retain acknowledgment until contradicted, or explicitly define a time window and label older evidence. Apply one documented rule across both chambers. The Senate's default builder instead chooses the strongest level across the entire period, subject to manual overrides.

### 5. Twenty-two House policy labels do not match the field definition

The September 18 China letter receives `intl=mixed` through `data/house/letter_levels.csv`. The stored explanation explicitly says it does not request a joint slowdown or pause. Nevertheless, the displayed field is specifically coordination with China on pacing or pausing. I counted 22 generated House records with this explanation and label.

This was an explicit reviewer decision, not an accidental model output. It still conflicts with the public definition. Dialogue about safety or a crisis hotline does not by itself establish a position on pacing.

**Recommendation:** broaden and rename the field to AI safety cooperation, or keep the existing narrow field and record this letter under bills/actions rather than as a pacing position. If retaining an exception, publish the exception.

### 6. Verification checks words, not attribution or meaning

`classify/check_news_quotes.py` checks whether normalized quote text appears anywhere in a downloaded page. It does not establish who said it, whether it is endorsed, whether the date is right, or whether surrounding context changes the meaning. A `found` result becomes the same `read at source` label used for manually entered quotes.

Saved check tables contain 341 found / 24 not found / 7 fetch failures for Senate sources, and 519 / 27 / 1 for House sources. Those are initial check results; some exceptions were subsequently resolved in the separate review table, so they are not counts of currently unverified quotes.

Eighteen Senate research files also record searches as `NOT RUN`, including Flanagan, Cooper, Talarico, Heinrich, Wicker, and several senators-elect. Direct page reads supplied some evidence, but the research effort is not uniform. These gaps are generally not visible on individual pages after the per-record notes were removed.

**Recommendation:** distinguish automatic text matches from attribution checks. Show search-coverage limitations next to affected records, especially D and no-statement records, and complete the skipped searches. Do not describe lack of a discovered statement as proof that someone has never acknowledged risk.

### 7. Smaller definition and display inconsistencies

- The rubric's B examples include bioweapons, while a later ruling assigns misuse-only biological weapons statements C. Make that exception explicit in the main rubric.
- The D description says catastrophic risk was not acknowledged. The dismissal penalty can turn C into D despite an acknowledgment (Ogles is an example). A grade derived from penalties needs an explanation distinct from a pure no-acknowledgment D.
- The methodology says D statements appear only when nothing stronger exists. `statements()` starts with every candidate and can fill unused slots with D evidence even when stronger evidence exists. Either filter the pool or correct the description.
- The Senate position aggregator in `site/build.py` can turn a combination of `yes` and `mixed` X positions into `yes`; the House aggregator returns `mixed`. Use a common policy rule and retain the underlying explanation.
- The House letter merger preserves an existing position even if a letter supplies a conflicting one. Decide whether conflict means Mixed or whether recency/explicitness resolves it.
- The corrections address is still `contact@example.com`.

## Source claims that checked out

- [The signed September 23 senators' letter](https://www.commerce.senate.gov/wp-content/uploads/2026/09/FINAL-China-AI-Diplomacy-Letter-9.23.26.pdf) supports a negotiated slowdown and a possible mutual pause, contains existential-risk framing, and lists 17 signers. An incomplete initial extract made the pause wording look absent; the full first page and [Kaine's release](https://www.kaine.senate.gov/press-releases/kaine-colleagues-push-trump-to-negotiate-ai-guardrails-with-xi-jinping) confirm it. I found no basis to challenge those core attributions.
- [Sanders' September 23 release](https://www.sanders.senate.gov/press-releases/news-sanders-casar-introduce-legislation-to-create-new-federal-agency-to-ban-artificial-superintelligence-pause-advanced-ai-development/) supports his existential-risk acknowledgment and describes a pause conditional on safety rules, consistent with the site's pause definition.
- [Forbes' September 9 video](https://www.youtube.com/watch?v=Iq0lWLcXlLE) corroborates the reported Cruz killer-robots remark. I did not independently transcribe the recording. His opposition to unilateral restraint should still be distinguished from an explicit rejection of negotiated bilateral restraint; the current coordination No is a reviewer interpretation.

The most urgent repairs are the build failure, current/next office modeling, and the recency rule. Broader questions about penalizing dismissals and grading co-signed letters are legitimate editorial choices, but should be applied consistently and explained clearly.
