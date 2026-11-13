# Instructions for labelling posts against the AI risk rubric (v0.2)

You are labelling X posts by one US senator. Each label is a first pass that a person
will review. Label each post on its own text only. Do not use outside knowledge of the
senator, their party, or their other statements. You cannot see attached images, videos
or linked pages; if the label would depend on them, add the flag `needs_media`.

This project tracks one thing: acknowledgment of **catastrophic** risk from AI. Other
consequences of AI (job loss, economic disruption, harm to children, data centers,
electricity bills, privacy, concentration of power) are real and important, but they are
outside its scope. A post about those alone is level D, which is not a negative judgment.

## Level (one per post)

| Level | Criterion |
|---|---|
| A | Explicitly says AI could cause human extinction or permanent loss of human control. |
| B | Says advanced AI poses catastrophic risks (mass casualties, bioweapons, loss of control) without the extinction framing. |
| C | Acknowledges serious risks from advanced AI in general terms, or relays others' warnings without stating them as their own view. |
| D | Catastrophic AI risk not acknowledged: the post is about AI but does not acknowledge catastrophic risk. |
| F | Dismisses or mocks catastrophic risk from AI. |
| off_topic | Not really about AI; the keyword is a passing mention or a false match. |

Rulings to apply:

1. **Threat to humanity is A.** Saying AI threatens "the future of humanity", "the human
   race", "our survival" or similar is A, even without the word extinction.
2. **Endorsed warnings count as the senator's own.** If the post relays someone else's
   warning and the senator endorses it in their own words ("we should worry", "this is
   not science fiction", "we must act"), give the level the warning itself would earn (A
   or B) and add the flag `relayed_warning`. If the warning is relayed without
   endorsement, the level is C, also with the flag.
3. **Military use of AI is D.** Autonomous weapons, AI in lethal decisions or nuclear
   launch, and calls for human oversight of them are about military use, not catastrophic
   risk from AI itself, unless the post names a catastrophic consequence.
4. **"Rogue AI" is not a category; judge by the harm named.** AI agents escaping,
   hacking or acting on their own are graded by the consequence the post states. If the
   only harm is cybercrime, hacking, fraud or financial loss, the level is D. If the post
   names a catastrophic consequence, use A or B. If it names a serious but general threat
   from the AI itself (for example to national security or public safety), use C. If no
   consequence is stated, use D and add the flag `boundary`.
5. **Not AI safety risk, so D:** AI as a tool of surveillance or control if China or
   another rival wins the race; competition with China generally; "AI must benefit
   everyone, not just billionaires" or who controls AI, with no catastrophic harm named;
   jobs, children, deepfakes, data centers, electricity bills, privacy, scams; promoting
   AI; industry news; campaign money.
6. **F needs dismissal of catastrophic risk itself.** Promoting AI or opposing
   regulation is D, not F.

The level measures acknowledgment of risk, not policy. Supporting or opposing a policy
does not change the level. When a post sits between two levels, choose the one the text
best supports, without leaning up or down, and add the flag `boundary`.

## Positions (each: yes, no, mixed, none)

- `pause`: a halt to building more capable frontier AI systems. A pause conditional on
  other countries joining, or on safety rules, is mixed.
- `slowdown`: slowing frontier AI capability progress for safety reasons. A call to
  pause AI for safety reasons also counts as yes here. Data center moratoria count only
  when the post ties them to risks from AI itself; moratoria motivated by electricity
  cost, local impact, jobs or democratic oversight are "none".
- `intl`: international coordination with China on pacing or pausing: coordinating with
  China on the pace of frontier AI development, including a mutual slowdown or pause,
  through an agreement, treaty or direct talks. Coordinating with allies to out-compete
  China does not count.

"no" requires a statement against the policy. If the post does not address the policy,
use "none". Most posts will be "none" on all three. Reporting a poll is not a position.

## Flags (zero or more)

- `relayed_warning`: the post cites or quotes someone else's warning about catastrophic
  risk (see ruling 2).
- `bill_or_action`: the evidence is a bill, letter, hearing or inquiry rather than a
  statement of belief.
- `cosigned_letter`: the evidence is a letter signed with other members.
- `boundary`: the post sits between two levels.
- `needs_media`: the label depends on an attachment or link you cannot see.
- `unsure`: you are not confident in the label for any other reason.

## Quote

For levels A, B, C and F, give the passage that best supports the level. It must be
copied exactly, character for character, as one continuous piece of the post's `text`
field, at most 300 characters. Do not fix typos, change punctuation or join separate
passages. For D and `off_topic`, use an empty string.

## Output

Write a JSON file: a list with exactly one object per input post, in input order.

    {"id": "<post id, as a string>",
     "level": "A|B|C|D|F|off_topic",
     "pause": "yes|no|mixed|none",
     "slowdown": "yes|no|mixed|none",
     "intl": "yes|no|mixed|none",
     "flags": [],
     "quote": "",
     "reason": "<one plain sentence explaining the level>"}

Label every post. Do not skip, merge or add posts.
