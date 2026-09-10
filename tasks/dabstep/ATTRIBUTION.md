# Attribution

The seven files in `inputs/context/` and all 100 questions come from
**DABstep: Data Agent Benchmark for Multi-step Reasoning**, published by Adyen
and Hugging Face.

> DABstep: Data Agent Benchmark for Multi-step Reasoning © 2025 by Alexander
> David Egg, Martin Iglesias Goyanes, Andreu Mora, Friso H. Kingma, Thomas Wolf,
> Leandro Von Werra is licensed under Creative Commons Attribution 4.0
> International.

- Dataset: <https://huggingface.co/datasets/adyen/DABstep>, revision
  `f6c0b00817d909dfdd39a6e7a9b4100eb73ca8de`
- Leaderboard and scorer: <https://huggingface.co/spaces/adyen/DABstep>
- Paper: *DABstep: Data Agent Benchmark for Multi-step Reasoning*,
  [arXiv:2506.23719](https://arxiv.org/abs/2506.23719)
- Licence: **CC BY 4.0** — <https://creativecommons.org/licenses/by/4.0/>

## What we changed

- **Selection.** 100 of DABstep's 450 questions: one per question template.
  Five templates are left out because no answer in DABstep's public record
  reproduces that record — the answers their server accepted and the ones it
  rejected cannot both be explained by any one reference answer.
- **Answers.** DABstep publishes no answer column. The reference answers used
  here were read back from its public leaderboard record and checked against
  that record with DABstep's own scorer.
- **Questions.** Each question and its formatting guideline are verbatim. Two
  lines are appended: one naming the seven files to answer from, and `End your
  reply with a line of the form ANSWER: <value>`.
- **Files.** The seven context files are unmodified.
- **Scoring.** DABstep's scorer is used unmodified. A check is added in front of
  it that rejects answers naming more candidate values, or carrying a different
  count of numbers, than the reference answer.
