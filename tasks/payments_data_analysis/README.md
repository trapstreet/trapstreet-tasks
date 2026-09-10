# payments_data_analysis

A data-analysis agent is handed one year of card payments for five merchants,
the fee schedule that prices them, and the manual that explains how the
schedule is read — and asked 129 questions about them. Some are a single
aggregation over the transactions. Others need the manual and the fee rules
together: what a merchant paid on a given day, which card scheme it should
steer traffic to, what a change of merchant category code would have cost.

The questions come from [DABstep](https://huggingface.co/datasets/adyen/DABstep),
Adyen and Hugging Face's benchmark for multi-step data reasoning. DABstep's 450
questions are generated from 134 templates; this task takes one question per
template, so each case asks something the others do not.

The answers, the judge and the grader are held privately, so **`tp run` will not
score against this directory**.

## What a solution is given

- `inputs/case_NNN/question.txt` — the question, DABstep's formatting guideline
  for its answer, the files to answer from, and one closing line: `End your
  reply with a line of the form ANSWER: <value>`.
- `inputs/case_NNN/` also holds the seven files every question is asked about:
  `payments.csv` (138,236 transactions), `fees.json` (1,000 fee rules),
  `manual.md`, `merchant_data.json`, `merchant_category_codes.csv`,
  `acquirer_countries.csv`, `payments-readme.md`. Each is a symlink into
  `inputs/context/`, so the repository carries one copy.

`traptask.yaml` is the case list, and `expected.sha256` is a manifest of every
artefact a solution is served.

## How an answer is scored

The last `ANSWER:` line is read and graded by DABstep's own scorer, so an
answer that passes here would pass on DABstep's leaderboard too. Numbers are
accepted within 0.01%, and lists in any order.

One check runs before it: the answer must be the shape of the reference — no
more merchants, schemes, countries or codes than it names, and the same count
of numbers. An answer that lists every candidate does not score.

Each case is tagged with DABstep's own level, `easy` or `hard`, and the run
reports accuracy for each.

## Acknowledgements

This task exists because of DABstep. Thank you to Alex Egg, Martin Iglesias
Goyanes, Friso Kingma, Andreu Mora, Leandro von Werra and Thomas Wolf, and to
Adyen and Hugging Face, for building it, releasing the data and the scorer under
CC BY 4.0, and publishing the leaderboard record in full. The licence notice and
the list of what we changed are in `ATTRIBUTION.md`.

```bibtex
@misc{egg2025dabstep,
  title         = {DABstep: Data Agent Benchmark for Multi-step Reasoning},
  author        = {Egg, Alex and Iglesias Goyanes, Martin and Kingma, Friso and
                   Mora, Andreu and von Werra, Leandro and Wolf, Thomas},
  year          = {2025},
  eprint        = {2506.23719},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG}
}
```
