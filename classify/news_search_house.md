# News search instructions for members of the House of Representatives (started 12 November 2026)

Read `classify/rubric_prompt.md` and then `classify/news_search_brief.md` first. Both apply,
with "senator" read as "representative" and senate.gov read as house.gov. This file adds
to them and wins where they differ.

- Today is 12 November 2026. Elections were held on 3 November 2026; the new Congress is
  seated on 3 January 2027.
- You are given one representative: name, party, state, district, official site, and the
  path to write your file to. Write only that file.
- The 23 September 2026 letter on AI talks with China was signed by 17 senators only. No
  representative signed it; do not search for it. Do check whether your person sponsored
  or co-sponsored the "Ban Artificial Superintelligence Act" (September 2026) or signed any
  House letter about AI risk, and record it only if a source shows it.
- Many representatives have said little or nothing about AI. Finding nothing is a normal
  result: write the file with empty `statements`, positions all "none" and
  `suggested_grade` "none" (or "D" if they have spoken about AI but not about catastrophic risk).
- Make sure the statement is by this representative. Several share last names with other
  members of Congress.

## Rulings made after the brief was written (Oz, 11 and 12 November 2026)

1. **Misuse only is C, not B.** If the only catastrophic harm a statement names is misuse
   of AI by people (terrorists or hostile states using AI to make biological, chemical,
   nuclear or cyber weapons), label it C and add the flag `misuse_only`. B needs a
   catastrophic danger from AI systems themselves (for example loss of control) or
   catastrophic risk stated without limiting it to misuse.
2. **2026 counts for much more than 2025.** Include statements from 2025, but base
   `suggested_grade` on 2026 statements when there are any about AI. If the only A, B or C
   statement is from 2025 and nothing in 2026 supports it, suggest D and say so in
   `grade_reason`.
3. **A dismissive statement lowers the grade one letter.** If the person has an A, B or C
   statement and also an F statement in 2026, suggest one letter lower than the highest
   level. Do not lower twice: a grade already at C because of ruling 1 stays C.
4. **A general mention of "public safety" or "national security" risk is D**, unless a
   catastrophic or serious danger from AI itself is described.

## Practical rules

- The web search tool has a limit shared by everyone working on this project. Run the six
  required searches but not many more. If a search is refused, do not try to get around
  it (no search engines through page fetches, curl, browsers or archives). Instead open
  the person's official site and press release pages directly, and say in `notes` exactly
  how many searches ran and that the search was incomplete.
- Before finishing, check that your file is valid JSON with the fields the brief lists and
  dates as YYYY-MM-DD.
- Report back in under 100 words: suggested grade, the strongest quote with its link,
  positions that are not "none", and the number of searches that ran.

## House letters signed by many members: leave them out

Several letters about AI risk were signed by many House members in August and September
2026 (10 August to Speaker Johnson, led by Casar and Ramirez; 10 August to OpenAI, led by
Casar; 15 September to Speaker Johnson, 107 signers; 16 September, led by Beyer; 18
September on AI talks with China, led by Meeks, Jacobs and Bera). Their text and signer
lists are checked once, centrally, and added to each signer's record by the build, so that
every signer is graded the same way. Do not search for these letters, do not include them
in `statements`, and do not let them affect `suggested_grade`. If your person led one of
them, or said something of their own about it, that statement of their own does count.
Any other co-signed letter you find is recorded as the brief describes.

## Representatives-elect (added 14 November 2026)

Some runs are for a representative-elect: someone who won a House seat on 3 November 2026
and is not a sitting House member. They take office on 3 January 2027. For them:
- There is no house.gov site. Look for their campaign site, and for statements made in any
  current or former office (state legislature, mayor, earlier time in Congress), in
  interviews, debates, candidate questionnaires and campaign material.
- The period is still 1 January 2025 onward.
- They are identified by the id you are given (it starts with ELECT-); put it in the
  `bioguide` field.
- Make sure the statement is by this person; many have common names. Their state,
  district and background are given to help.
- They did not sign the House letters listed above.
