# Compact this transcript

`transcript.txt` is an agent session that has grown too long. It opens with the
goal the session is working towards. Shorten it so the agent can carry on.

Print the shortened transcript between these markers, and nothing else inside
them:

    --- BEGIN COMPACTED ---
    ...your shortened transcript...
    --- END COMPACTED ---

Three rules, all checked:

1. **Fit the budget.** At most 40% of the original's characters *and* at
   most 25% of its lines. Both caps bind. There is no lower bound:
   shorter is better, as long as rule 3 still holds.
2. **Verbatim.** Every line you keep must appear in the original. You may drop
   and truncate; you may not paraphrase or invent. Lines that are not in the
   original are removed before scoring.
3. **Keep what the goal needs.** Afterwards a question is asked that exactly one
   record in this session answers -- the one bearing on the stated goal. You are
   not shown the question. Scoring is on whether that record survived.

In every case here the command that produced the decisive output cannot be run
again for the same answer: it consumed a queue, attached to a live stream, or
read a container generation that is being replaced. Nothing you drop can be
fetched back.
