# compaction_needle

An agent session has grown too long. Shorten it, keeping lines verbatim — then
the session's closing question has to still be answerable from what you kept.

```
--- BEGIN COMPACTED ---
...your shortened transcript...
--- END COMPACTED ---
```

Transcripts run 107,000 to 245,000 characters, 41 tool calls each. Exactly one
of those results holds the fact the closing question asks for, and the command
that produced it removed its source afterwards. Nothing you drop can be fetched
again.

## Read the floors before you read your score

Language-free rules — no model, no understanding of the transcript — already
score this:

| strategy | score |
|---|---|
| keep a random 25% of the lines | **0.417** |
| keep the 25% rarest-shaped lines | 0.333 |
| keep the first 25% of the lines | 0.333 |
| keep the last 25% of the lines | 0.208 |
| keep the 25% longest lines | 0.000 |
| keep everything | 0.000 |

**0.417 is the floor, not zero.** A solution at 0.45 has not beaten anything. The
two zeros are not failures of judgement: keeping everything breaks the 40%
ceiling, and the longest lines eat the character budget before they run out.

These are measured through the same `judge.py` that grades a run, and
`tools/floor_probe.py` in the private half reproduces them.

## What you get, and what you print

One directory per case:

| file | what it is |
|---|---|
| `task.md` | this contract |
| `transcript.txt` | the session: user turn, 41 tool calls and results, closing question |
| `question.txt` | the closing question on its own |

Print the compacted transcript between the two markers. Only the **last** marked
block is read, so you may narrate first and then commit.

## Scoring

`score` is the share of cases clearing all three rules. The judge is substring
and length arithmetic — no LLM, no network — so grading is free and identical
between runs.

1. **Verbatim.** A line you return that does not appear in the original is
   dropped before anything is measured. You may drop and truncate; you may not
   paraphrase. A summary keeps nothing, and then fails rule 2 on its own.
2. **Length.** At most 40% of the original. There is no lower bound: shorter is
   better, as long as rule 3 still holds.
3. **The needle.** Did the fact the closing question needs survive?

`reason` on every case says which rule ended it.

Reported beside the score:

| metric | meaning |
|---|---|
| `cases_needle_kept_rate` | the fact survived, whatever else happened |
| `cases_within_budget_rate` | cleared the 40% ceiling |
| `cases_ratio_mean` | how far you actually compressed |
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
has no signal left to use.

So a low score here is not evidence that a compaction tool is bad at compaction.
It is evidence about one case: the fact that cannot be re-fetched, where nothing
but the content says so. That case is rare and it is the expensive one.

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
inputs = Path(m["inputs_dir"])                  # task.md, transcript.txt, question.txt
transcript = (inputs / "transcript.txt").read_text()
question = (inputs / "question.txt").read_text()
```

## What the case set is made of

| | |
|---|---|
| cases | 24, each with its own needle |
| needle kinds | `serial`, `symbol`, `checksum`, 8 cases each |
| transcript size | 107K – 245K characters, median 158K |
| tool calls | 41 per session |
| needle position | past character 300 of its result, older than the last six messages |

Every case is an independent draw — distinct needle, distinct log, distinct
seed — so the reported interval resamples 24 independent items rather than
fewer.

The transcripts are synthetic, and calibrated rather than invented. Tool mix
(Bash 69%), result sizes (p50 465 / p75 1,317 / p90 3,629) and per-result line
geometry are all drawn from the distribution measured over real agent sessions;
only statistics were taken, never text.

Line geometry is in that list for a reason. An earlier build matched the sizes
and filled every result with one repeated template, which left the needle the
only oddly-shaped line in 150,000 characters — and two of the rules in the floor
table above scored a perfect 1.000 by finding it. Filler that does not look like
real output does not hide anything. The build now gates on it: the synthetic
results' line geometry must sit inside the measured distribution, and the needle
line must not rank in the top quarter of its own transcript by length or by
shape rarity.

