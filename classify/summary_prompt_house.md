# House addendum to the summary instructions

Read `classify/summary_prompt.md` first and follow it, with these changes for members of the
House. Read the first 30 lines of `data/summaries.csv` for the style to match.

- Refer to each person exactly as the digest's `call_them` field says (for example
  "Representative Lieu" or "Representative-elect Jane Doe") where the Senate instructions say
  "Senator X". After the first mention use the same form again or "they"; use "he" or "she" only
  where the person's own quoted words make it certain.
- The grade is in `grade`. First sentence by grade:
  - A: "... has acknowledged that AI could threaten human survival or escape human control."
    (or close wording that fits their words).
  - B: "... has acknowledged catastrophic risk from AI, without describing it as a threat of
    extinction."
  - C: "... has acknowledged serious risks from AI in general terms, without naming a
    catastrophic outcome." If `grade_notes` says the only catastrophic risk named is misuse of AI
    by people, write instead that they have acknowledged catastrophic risk from AI only as misuse
    by people (for example biological weapons or cyberattacks), not as a danger from AI systems
    themselves.
  - D: "... has not acknowledged catastrophic risk from AI."
  - F: "... has dismissed warnings of catastrophic risk from AI."
- Co-signed letters. If `grade_notes` says the grade rests on a co-signed letter, say so in the
  first sentence: "... has acknowledged catastrophic risk from AI by co-signing a letter, but not
  in their own words." Then say what the letter said (a short quoted fragment from the letter's
  `quote` is fine) and, if they have statements of their own, what those are about. When quoting
  a letter, make clear the words are the letter's ("a letter she co-signed says ..."), not the
  member's own.
- If `grade_notes` says the grade was lowered because of a dismissive statement, say plainly in
  the second sentence what the dismissive statement was (the statement with level F).
- If `grade_notes` says a stronger statement from 2025 was outweighed by 2026 statements, do not
  lead with the 2025 statement; describe the 2026 ones, and you may add that they spoke more
  strongly in 2025.
- For D, say what their AI statements are about, using the statements' `about` fields and
  `topics_of_other_posts` (these are a labeller's notes: use them for the topic, never quote
  them).
- Quoted fragments must be copied exactly from a `quote` field of that person's `statements`.
- Do not mention grades, levels, letters of the rubric, X post counts, searches or language
  models. No party labels.
- 25 to 60 words per person.

## Output

Write a CSV with header `bioguide,summary`, one row per person in the digest, in the same order,
to the path you are given (use Python's csv module). Then check with a short script that every
bioguide in the digest has exactly one row, that each summary starts with that person's
`call_them`, and that every passage inside straight double quotes in a summary appears exactly in
one of that person's `quote` fields. Write nothing else in the project.
