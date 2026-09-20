# compaction_needle

An agent session has grown too long. Shorten it, keeping lines verbatim — and
the one record that bears on the session's stated goal has to survive.

```
--- BEGIN COMPACTED ---
...your shortened transcript...
--- END COMPACTED ---
```

Transcripts run 155,000 to 304,000 characters, 41 tool calls each. The session
opens with its goal. Somewhere in those results is the one anomaly record that
bears on it, among about 900 that do not, all written the same way. Afterwards a
question is asked that only that record answers — **you are not shown it**. The
commands removed their sources, so nothing you drop can be fetched again.

## Read the floors before you read your score

Language-free rules — no model, no understanding of the transcript — already
score this:

| strategy | score |
|---|---|
| keep whatever looks alarming | **0.208** |
| keep lines sharing a word with the goal | 0.125 |
| keep the first / last / a random slice, to budget | 0.000 |
| keep the shortest / longest / rarest-shaped lines | 0.000 |
| keep everything | 0.000 |
| *oracle: keep the goal's domain, alarming lines only* | *1.000* |

And one real system, measured:

| | score | record kept |
|---|---|---|
| [`fast-jev-compaction`](https://github.com/tamaratran/fast-jev-compaction) @ `e3f262a`, default config | **0.000** | 0 / 24 |

No `keepThreshold` recovers it. At 0.25 nothing survives and nothing compresses
past 0.14; at 0.15 the record survives in 24 of 24 but the compaction ratio is
1.000 — it is keeping everything. The reason is not calibration: the record's
`keepResult` has a median of 0.200 against a session median of 0.190 and a
session maximum of 0.250, all ~38 candidates inside a band 0.08 wide. It was the
top-scoring call in 0 of 24 cases. That is consistent with what the plugin
documents about itself — every tool result is replaced by `ok, <n> chars
(omitted)` before its model sees it, so the decision is made without the
content.

**0.208 is the floor, not zero.** A solution at 0.25 has not beaten anything.

The last row is the ceiling: a rule that knows which artefacts belong to which
domain, and nothing else — no question, no needle, no answer. It scores 1.000,
so the range between floor and ceiling is real and the task is solvable.

Three of these rules used to score 1.000, 1.000 and 0.958. What closed them is
in **What the case set is made of** below; the short version is that each was
finding something the author had made different, not something a compactor
should know.

## What you get, and what you print

One directory per case:

| file | what it is |
|---|---|
| `task.md` | this contract |
| `transcript.txt` | the session: the goal, then 41 tool calls and their results |

There is no `question.txt`. A solver handed the question is doing retrieval, not
compaction — keeping the lines that shared a rare word with it scored 1.000.

Print the compacted transcript between the two markers. Only the **last** marked
block is read, so you may narrate first and then commit.

## Scoring

`score` is the share of cases clearing all three rules. The judge is substring
and length arithmetic — no LLM, no network — so grading is free and identical
between runs.

1. **Verbatim.** A line you return that does not appear in the original is
   dropped before anything is measured. You may drop and truncate; you may not
   paraphrase. A summary keeps nothing, and then fails rule 2 on its own.
2. **Budget.** At most 40% of the characters **and** at most 6% of the lines.
   Both bind. There is no lower bound: shorter is better, as long as rule 3
   still holds. The line cap is there because a character cap alone is
   arbitrageable — shortest-first fits about 80% of the lines into 40% of the
   characters.
3. **The record.** Did the one anomaly that bears on the goal survive?

`reason` on every case says which rule ended it.

Reported beside the score:

| metric | meaning |
|---|---|
| `cases_needle_kept_rate` | the record survived, whatever else happened |
| `cases_within_budget_rate` | cleared both caps |
| `cases_ratio_mean` / `cases_line_ratio_mean` | how far you actually compressed |
| `n_fabricated` | cases where at least one returned line was not in the original |
| `by_category` | by needle kind: `serial`, `symbol`, `checksum` |
| `cases_accuracy_ci_low` / `_high` | 90% interval over case resamples |
| `latency_*`, `cost_*` | a transcript this size is where context cost shows up |

## What this board measures, and what it does not

It measures the tail, deliberately.

Over 26,778 real tool results in local agent sessions, we labelled whether each
result was still needed later. Deciding from the result's **content** beats
deciding from its metadata alone by **1.6 points** — 79.9% against 78.3%. For
ordinary work, a call's name and arguments predict almost everything: `Read
src/auth.ts` matters, `ls /tmp` does not, and the command says so.

This board removes that. Forty-one commands look alike, and nothing in the one
that matters marks it. A compaction layer that never reads what it is dropping
has no signal left to use — and among the content, 900 records are written
exactly like the one that counts.

So a low score here is not evidence that a compaction tool is bad at compaction.
It is evidence about one case: the fact that cannot be re-fetched, where nothing
but the content says so. That case is rare and it is the expensive one.

**These sessions carry no assistant prose, and that makes them a lower bound.**
In real sessions an assistant writes about what it found between tool calls — 
0.45 such messages per tool call, median 155 characters — and 39% of the time
that prose repeats at least three tokens from the result that preceded it.
A compaction layer that drops tool outputs but keeps prose therefore recovers
some of the content second-hand. These transcripts close that channel, so a
score here is the floor of what a layer would do on a real session, not the
typical case.

## Setup

None. The cases are in this repository; clone it and run. No browser, no Docker,
no API key, no download.

## Run it

```yaml
name: my-solution
cmd: python3 solution.py
timeout: 900
tasks:
  compaction-needle:
    source: git+https://github.com/trapstreet/trapstreet-tasks@<commit>#subdirectory=tasks/compaction_needle
```

```bash
tp run
```

Your solution is invoked once per case with `TRAP_MANIFEST` in the environment:

```python
m = json.loads(os.environ["TRAP_MANIFEST"])
inputs = Path(m["inputs_dir"])                  # task.md, transcript.txt
transcript = (inputs / "transcript.txt").read_text()
```

## What the case set is made of

| | |
|---|---|
| cases | 24, each with its own record |
| domains | 6 — billing, search, messaging, auth, storage, cache; 4 cases each |
| anomaly kinds | `digest`, `link_failed`, `quarantined`, `checksum_drift`; 6 cases each |
| decoys | 900 per case, the same sentence for artefacts in every domain |
| transcript size | 155K – 304K characters, median 212K |
| tool calls | 41 per session |
| record position | past character 300 of its result, older than the last six messages |

Every case is an independent draw — distinct needle, distinct log, distinct
seed — so the reported interval resamples 24 independent items rather than
fewer.

The transcripts are synthetic, and calibrated rather than invented. Tool mix
(Bash 69%), result sizes (p50 465 / p75 1,317 / p90 3,629) and per-result line
geometry are all drawn from the distribution measured over real agent sessions;
only statistics were taken, never text.

Line geometry is in that list for a reason. An earlier build matched the sizes
and filled every result with one repeated template, which left the record the
only oddly-shaped line in 150,000 characters — and two language-free rules
scored a perfect 1.000 by finding it. Filler that does not look like real output
does not hide anything.

Three properties are held by the build and fail it otherwise:

- **the goal never names the record.** The goal says *the billing run did not
  balance*; the record says `coupon_ledger_v3`. They share no word, so relating
  them takes knowing what a coupon ledger is for. Anything the goal spells could
  be grepped instead.
- **the record is not alone.** 900 decoys carry the same sentence for artefacts
  in other domains — more than three times the line budget, so keeping every
  alarming line is not an option.
- **the filler's line geometry sits inside the distribution measured over real
  tool results**, so no rule over line length or shape rarity has anything to
  latch onto.

