# compaction_needle

A transcript compaction benchmark. Each case is one agent session that has grown
too long, plus the goal it is working towards. A solution returns a shorter
transcript. Scoring asks whether the one record that answers the goal survived,
within a character and a line budget, using only lines that were in the original.

The session cannot be re-run: the decisive output came from a consumed queue, a
live stream, or a container generation that is being replaced.

## Cases

24 cases across 6 domains, in two categories by how plainly the decisive
command is one-shot:

| category | the decisive command | cases |
|---|---|---|
| `consumed` | reading destroys the source -- a queue receive, a stream attach | 12 |
| `ephemeral` | it is about to be gone -- a restarting container's previous log | 12 |

Budgets are 40% of characters and 25% of lines, both binding.
A per-case build gate asserts that an answer keeping only the decisive record
fits inside the budget and that the strongest content-free strategy does not.

## What does not score

Ten trivial strategies were measured through this judge. The best reaches
0.083, which is the chance of picking one call at random out of about
thirty: keep everything, drop everything, keep the shortest lines, keep the
longest result, keep the first / last / a random call, keep the command that
appears only once, keep the lines that look alarming, and keep the lines that
echo the goal's own words.
