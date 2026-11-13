# Instructions for drafting the summary sentence shown after each grade

Each politician's page shows "Grade X." followed by one or two plain sentences about what they
have said. You are drafting those sentences for the people in one digest file. A person will
review them. Accuracy matters more than polish: say only what the digest supports.

Read `data/summaries.csv` first; its sentences are the style to match.

## Rules

- First sentence, by draft grade:
  - A: "Senator X has acknowledged that AI could threaten human survival." (or close wording that
    fits their words, e.g. "existential risk from AI"). If `highest_level_in_own_words` is lower
    than A, the A comes only from the September 2026 letter of 17 senators, so write
    "Senator X has acknowledged existential risk from AI by signing a letter, but not in their own
    words." (or "..., and has spoken about ... themselves" if their own words reach B or C).
  - B: "Senator X has acknowledged catastrophic risk from AI, without describing it as a threat of
    extinction."
  - C: "Senator X has acknowledged serious risks from AI in general terms, without naming a
    catastrophic outcome." (or "has relayed others' warnings ... without endorsing them" when
    that is what happened).
  - D: "Senator X has not acknowledged catastrophic risk from AI."
  - F: "Senator X has dismissed warnings of catastrophic risk from AI."
  - none: "No statement about AI by Senator X was found."
- Then one sentence (two at most) on what they actually said: the strongest statement, with a
  short quoted fragment if one fits, or for D what their AI statements are about (for example
  data centers, competition with China, children's safety).
- If someone graded A, B or C also has an F statement, say so plainly in the second sentence
  (for example: 'He has also called talk of human extinction "over the top".').
- Quoted fragments must be copied exactly from a `quote` field in the digest for that person,
  be at most about 15 words, and must not change the meaning. Use straight double quotes. Do not
  quote the `context` or reason fields; they are a labeller's words, not the politician's.
- Use "Senator" plus the last name (for example "Senator Cortez Masto", "Senator Van Hollen").
  Use "he" or "she" only where the digest or their own quoted words make it certain; otherwise
  repeat the name or use "they". Do not guess from a first name.
- Plain language. No rubric letters, no jargon, no mention of X post counts, search methods or
  language models. No party labels. Do not say "reportedly".
- 25 to 60 words per person.

## Output

Write a CSV with a header line `bioguide,summary`, one row per person in the digest, in the same
order, to the path you are given (use Python's csv module so quoting is right). Then check with a
short script that every bioguide in the digest has exactly one row and that every passage inside
straight double quotes in a summary appears exactly in one of that person's digest `quote`
fields. Write nothing else in the project. Report in under 80 words, listing anyone whose
sentence you were unsure about.
