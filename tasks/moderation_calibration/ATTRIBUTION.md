# Attribution — moderation_calibration

- **Dataset:** Civil Comments, as redistributed by Google/Jigsaw for the
  *Jigsaw Unintended Bias in Toxicity Classification* competition
- **Source:** [`google/civil_comments`](https://huggingface.co/datasets/google/civil_comments)
  on Hugging Face, `test` split
- **License:** CC0 1.0 Universal (public domain). Freely usable, no
  permission needed, no notice required. Attribution is given here as good
  practice, not a license condition.
- **Original source of the comment text:** the Civil Comments platform, a
  commenting plugin used on ~50 independent English-language news sites,
  2015–2017.

## What "true_toxicity" actually is

Every comment in the source dataset carries a `toxicity` field: the
**empirical fraction of independent human crowd annotators** who rated that
comment as toxic (the raw annotation counts per comment are not published in
this CC0 release, but the fraction's denominators we observed when sampling
were mostly 5, 6, or 10 raters). This is a real outcome statistic from real
people, not an LLM judgment and not authored by us — which is the entire
point of the task (see README.md, "Why this task").

## How the 60 shipped cases were selected

Sourced from a random sample of ~270 comments (`source_index` traceable back
to the `test` split), filtered for:

- length 60–280 characters (readable in seconds, no walls of text)
- no URLs, no heavy quote-nesting
- **no reference to unseen context** — comments containing phrases like "my
  previous post", "as I said above", "this article" were excluded. The
  annotators who produced `toxicity` saw the surrounding article/thread; we
  do not ship it, so a comment whose score depends on that context would be
  unfair to grade from text alone.
- `severe_toxicity < 0.5`, `threat < 0.4`, `sexual_explicit < 0.3` — the task
  tests ordinary harassment/toxicity triage, not a shock-content ceiling.

From the filtered pool, cases were **manually reviewed and hand-picked** (not
purely randomly sampled) to drop comments whose score didn't plausibly match
what a reader would perceive from the text alone — a real, observed failure
mode of this dataset at the extremes (a `toxicity` of exactly 0.0 or 1.0 can
come from very few raters, and several of the initially-sampled 1.0-labeled
comments read as unremarkable out of context). This is disclosed rather than
hidden: it means the shipped 60 are a curated subset chosen for label
face-validity, not an unbiased random sample of the source dataset — see
README.md, "Known limitations".

Final composition, stratified by `toxicity` to guarantee enough cases in the
middle of the range (where a calibration curve actually has something to
show — natural prevalence in this dataset is heavily skewed toward
non-toxic):

| bin | toxicity range | n |
|---|---|---|
| `clear_no` | = 0.0 | 8 |
| `ambiguous_low` | (0.0, 0.35] | 14 |
| `ambiguous_mid` | (0.35, 0.65] | 14 |
| `ambiguous_high` | (0.65, 1.0) | 14 |
| `clear_yes` | = 1.0 | 10 |

This stratification does not represent the source dataset's natural
prevalence of toxic content — see README.md for why that's the right call
for a per-item calibration metric, and why it wouldn't be for a
prevalence-sensitive metric like binned ECE.
