# moderation_calibration

Given a single public comment, output a probability that a content-moderation
team would escalate it for human review under a standard harassment/toxicity
policy. The task scores **how well-calibrated that probability is** against a
real outcome — not just whether the yes/no call was right.

## Why this task

Most classification benchmarks score accuracy: right or wrong. That misses a
question that matters just as much for anything making probabilistic
decisions inside software — a moderation queue, a routing rule, a triage
score: when the system says "70% likely," is it actually right about 70% of
the time? A model that always answers with extreme confidence (near 0 or
near 1) can score well on accuracy while being badly miscalibrated, and a
model that hedges everything toward 0.5 can look "safe" while being useless
as a routing signal.

This is also, deliberately, a fair fight between different ways of producing
that probability: an LLM reasoning about the text directly and self-reporting
a number, an LLM outsourcing the judgment to a dedicated decision primitive
(e.g. TypeSafe's Jev, or any other structured-decision API), and different
ways of using such a primitive (a single call vs. decomposed sub-questions,
different amounts of context). The task doesn't favor any one approach —
`judge.py` only sees a number on a sentinel line, however it was produced.

## Input / output contract

Each case directory (`inputs/<id>/`) contains:

- `task.md` — the fixed instructions (identical across all cases)
- `comment.txt` — the one comment to judge, with no surrounding article or
  thread

Print your estimate on its own line, anywhere in your output:

```
ANSWER: 0.73
```

You may reason or write anything else before it; only the **last** line
starting with `ANSWER:` is read. The value must be a plain probability in
`[0, 1]` — not a percentage, not a 1–10 scale.

## Wiring up a solution

```yaml
name: my-solution
cmd: uv run python solution.py
timeout: 120        # cases are single short LLM/API calls; well under trap's 600s default

tasks:
  moderation_calibration:
    source: /path/to/this/task
```

## Scoring

`score_case()` computes:

```
score = 1.0 - (predicted_probability - true_toxicity) ** 2
```

`true_toxicity` is the real annotator fraction from the source dataset (see
Sources below) — not an LLM judgment, not authored by us. This is a
[strictly proper scoring rule](https://en.wikipedia.org/wiki/Scoring_rule#Proper_scoring_rules):
the solution's best strategy is to report its actual, honest estimate.
Rounding to 0 or 1 when genuinely uncertain scores worse than reporting the
honest middle value, and hedging toward 0.5 when the evidence points
elsewhere also scores worse — the task README given to solutions says this
explicitly, so it's a stated rule, not a hidden gotcha.

The run-level score is the mean of all 60 per-case scores; per-bin (`clear_no`
/ `ambiguous_low` / `ambiguous_mid` / `ambiguous_high` / `clear_yes`) means
are broken out separately, since a solution that's well-calibrated on
obvious cases but not on ambiguous ones is a meaningfully different result
than one that's uniformly mediocre.

**`n_passed` (score `== 1.0`) is not a meaningful number for this task** — it
will be ~0 for every solution, since squared error against a real-valued
target is essentially never exactly zero. Read the mean score and the
per-bin breakdown; ignore `n_passed`/`passed`, which `grader.py` reports
generically for every task in this repo.

Malformed output degrades to `score: 0.0` rather than crashing the judge:
missing `ANSWER:` line, non-numeric value, `Infinity`/`NaN`, or a value
outside `[0, 1]` (including an unrescaled percentage like `73` instead of
`0.73` — this is treated as a real mistake, not silently corrected).

If cost is shown on a run, note that `trap` prices prompt and completion
tokens with no cache-hit discount, so a solution whose provider serves part
of the request from a prompt cache will show a cost higher than what the
call actually cost.

## Sources & licensing

See [`ATTRIBUTION.md`](ATTRIBUTION.md) for the dataset, license (CC0), and
exactly how the 60 cases were selected and curated from it.

## Known limitations

- **Curated, not randomly sampled.** The 60 cases were hand-reviewed for
  label face-validity (see `ATTRIBUTION.md`) — some comments the source
  dataset scores near 0 or 1 don't read that way out of context, likely from
  a small number of annotators per comment. This task keeps the ones where
  the score plausibly matches the text; it does not represent the source
  dataset's raw label noise.
- **Stratified, not natural prevalence.** Real toxicity data is heavily
  skewed toward non-toxic; this case set deliberately over-samples the
  middle of the range so there's something for a calibration curve to show.
  A per-case squared-error mean is not distorted by this the way a binned
  ECE would be, but a solution's absolute score here should not be read as
  "how well-calibrated is this on a representative comment stream."
- **No article/thread context**, by construction (see `ATTRIBUTION.md`) —
  the task is triage on the comment text alone, which is a real and common
  first-pass setting, but not the only one.
- **Leakage risk is real but likely modest.** Civil Comments is a
  well-known, moderately-cited dataset (unlike a famous, heavily-blogged
  benchmark), and cases were sampled from the full ~97k-row `test` split at
  an arbitrary seed rather than reusing a commonly-copied demo subset. This
  reduces but does not eliminate the chance a specific comment's score was
  memorized during training.
- **Single domain.** This only tests toxicity/harassment triage. It does not
  claim calibration on one domain transfers to another (fraud, routing,
  content moderation for a different policy, etc.).

## Run

```bash
python3 build_cases.py                 # (re)generate inputs/ and expected/ from gold.cases.json
python3 -m pytest tests/ -v            # unit tests
```
