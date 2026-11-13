# Instructions for choosing which ordinary AI posts to show

These X posts are by US senators or senators-elect for whom no statement about catastrophic
risk from AI was found. Each post mentions AI but was labelled as not addressing catastrophic
risk. Their pages should still show a few posts that tell a reader what the person has
actually said about AI. Your job is to mark which posts are worth showing and pick the quote.

For each post decide `show`:

- `true` if the post states the politician's own view or action on AI: how it should be
  developed, regulated or used; its risks, harms or benefits; competition with other
  countries over AI; or data centers (their costs, siting, power or regulation).
- `false` if AI is incidental or the post says nothing of substance about it: congratulations
  and greetings, event or media appearance announcements, sharing a link with no view
  stated, a list where AI or data centers is one passing item, a campaign attack where AI is
  not the point, or a post that cannot be understood without an attachment you cannot see.

For posts with `show: true`, give `quote`: the passage that best states the view, copied
exactly, character for character, as one continuous piece of the post's `text`, at most 300
characters, whole sentences where possible. Do not cut a quote so that its meaning changes.
For `show: false`, `quote` is an empty string. Judge each post on its text alone; apply the
same standard to every politician regardless of party.

Output: a JSON list with exactly one object per input post, in input order:

    {"id": "<post id as a string>", "show": true, "quote": "...", "why": "<a few plain words>"}
