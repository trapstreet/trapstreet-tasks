# Compact this transcript

`transcript.txt` is an agent session that has grown too long. Shorten it so the
agent can keep working, then answer the question it ends with.

Print the shortened transcript between these markers, and nothing else inside
them:

    --- BEGIN COMPACTED ---
    ...your shortened transcript...
    --- END COMPACTED ---

Three rules, all checked:

1. **Compress.** The compacted transcript must be at most 40% of the
   original's length. Returning it unchanged fails. There is no lower bound:
   shorter is better, as long as rule 3 still holds.
2. **Verbatim.** Every line you keep must appear in the original. You may drop
   and truncate; you may not paraphrase or invent. Lines that are not in the
   original are removed before scoring, which will cost you the length gate.
3. **Keep what the question needs.** The session ends with a question. Scoring
   is on whether the fact that answers it survived your compaction.

The session's own work cannot be repeated: the command that produced the
relevant output removed its source afterwards. Nothing you drop can be fetched
again.
