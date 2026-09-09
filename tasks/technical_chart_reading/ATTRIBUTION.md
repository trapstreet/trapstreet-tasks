# Attribution

The nineteen chart images in `inputs/charts/` and nineteen of the twenty-seven
questions come from **Chartography**, a benchmark of professional chart
understanding published by Surge AI.

- Source: <https://huggingface.co/datasets/surgeai/chartography>
- Paper: *Chartography: A Benchmark for Professional Chart Understanding*,
  [arXiv:2608.10677](https://arxiv.org/abs/2608.10677)
- Licence: **CC BY 4.0** — <https://creativecommons.org/licenses/by/4.0/>

Only the rows Chartography marks `source_type = "Expert-created"` are used.
Those images were made by the task authors and are released under CC BY 4.0.
The other eighty-one charts in that dataset were collected from third parties
and are **not** redistributed here.

## What we changed

- Three questions carry an added sentence stating the answer format, so that a
  deterministic judge can grade them. The question and its expected answer are
  otherwise unaltered.
- Every question carries the `ANSWER: <value>` contract this repository's judge
  reads.
- Eight further questions (cases 20-27) are **ours**, not Chartography's. They
  ask different things about six of the same charts, and their answers were
  measured from the images rather than taken from the dataset.

Chartography asks that the dataset be used for evaluation and not for training.
That is what this task is for.
