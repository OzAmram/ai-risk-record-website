# Instructions: who won each House seat on 3 November 2026 (one group of states per run)

Today is 14 November 2026. Elections for all 435 seats of the US House were held on
3 November 2026; winners take office on 3 January 2027. This project needs to know, for
every district in your states, who won, so that it can list representatives-elect (winners
who are not sitting members) and sitting members who will not return.

For each state you are given, find the winner of every congressional district from a
reliable results source (state election officials, AP, CBS News, NBC News, CNN, The New
York Times, Politico, Ballotpedia, local newspapers). Use web search and open the pages.
Do not write anything from memory: every row needs the link where you saw the result.
Several states redrew their districts for 2026, so use the district numbers of the
2026 election, not the old ones.

`data/house/roster.csv` lists the sitting members (columns bioguide, member, last_name,
party, state, district). Use it to fill `sitting_bioguide` when the winner is a sitting
House member (in any district). Leave it empty for anyone else.

Write one JSON file to the path you are given, and nothing else in the project:

    {"states": ["XX", ...],
     "districts": [
       {"state": "XX", "district": 1,            (0 for an at-large seat)
        "winner": "Full Name", "party": "Democrat|Republican|Independent|other",
        "status": "called|uncalled|runoff",       (uncalled or runoff: winner may be "")
        "sitting_bioguide": "",                   (if the winner is a sitting House member)
        "previous": "one plain sentence if the winner is new: who held the seat and why it changed hands (retired, lost primary, lost, ran for other office, redistricting)",
        "background": "for a new winner: one plain sentence on who they are (current or former office, profession)",
        "source_label": "e.g. CBS News results", "source_url": "https://..."}],
     "notes": "anything uncertain: races too close to call, recounts, sources that disagree"}

Every district of every state you were given must have exactly one row. If you cannot
find a result, set status "uncalled", leave winner empty and say so in notes. Before
finishing, check the file is valid JSON and that the number of rows per state matches
that state's number of House seats. Report in under 60 words: rows written, how many
winners are not sitting members, how many uncalled.
