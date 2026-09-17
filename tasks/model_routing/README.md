# Model routing: same accuracy, less spend?

200 multiple-choice questions from MMLU-Pro — 100 law, 100 engineering — where
cheap and frontier models are far apart. A solution answers each question
however it likes: one model, or a pipeline that sends some questions to a
cheaper model and some to a stronger one. The board puts **accuracy** next to
**metered cost**, so a router is judged on whether it keeps the strong model's
accuracy while paying for it less often.

## Input and output

Each case gives a solution two files:

- `task.md` — the instructions (the same for every case)
- `question.json` — `{"question": "...", "options": {"A": "...", "B": "...", ...}}`
  (most questions have 10 options)

The solution prints, as its last `ANSWER:` line:

```
ANSWER: <letter>
```

Optional lines, never scored:

- `ESCALATED: yes|no` — the final answer came from a more expensive step than
  the first one tried. The run page reports the share.
- `UNMETERED_COST_USD: <dollars>` — spend on an API tp's cost proxy cannot
  meter; it is added to the cost-per-correct figure and shown as self-reported.

## Scoring

- **Score = share of questions answered correctly.** No answer counts as wrong.
  Always answering the most common letter scores 0.16.
- **Cost** is metered by tp for Anthropic, OpenAI, DeepSeek, Moonshot and
  OpenRouter calls, and shown beside the score.

Run page fields:

| field | meaning |
|---|---|
| `n_correct`, `n_unanswered` | counts |
| `cases_accuracy_ci_low` / `_high` | 90% interval for the score from resampling the questions |
| `cost_usd_total` | metered spend over all questions |
| `cost_unmetered_usd` | self-reported spend tp cannot meter |
| `cost_usd_per_correct` | (metered + self-reported) / correct answers |
| `cases_escalation_rate` | share of questions a solution reported `ESCALATED: yes` for |
| `by_category` | accuracy in law and in engineering |

## Calibration questions

A router needs a threshold, and a threshold tuned on the scored questions
would be fitted to the answer key. `calibration_question_ids.json` lists 200
other MMLU-Pro test questions (100 law, 100 engineering, drawn with a fixed
seed) that are **not** in the case set; tune on those.

On those 200, answered once each with no extended thinking:

| model | law | engineering |
|---|---|---|
| Claude Haiku 4.5 | 53 | 62 |
| DeepSeek Flash | 72 | 83 |
| Claude Opus 5 | 87 | 84 |

## How the 200 cases were chosen

MMLU-Pro's test split has 1,101 law and 969 engineering questions. The 200
calibration questions were removed, then 100 per subject were drawn with a
fixed seed. Law and engineering were chosen because a public leaderboard
(Vals.ai) shows a large gap there between Claude Haiku 4.5 and Claude Opus 5,
which the calibration questions above confirm: a small model and a frontier
model disagreeing often is what gives routing something to do.

## Limitations

- **MMLU-Pro is public** (since 2024), answers included. Models may have seen
  the questions in training, and a solution that looks a question up can find
  its answer. Results assume solutions answer the question rather than
  retrieve it.
- **Escalation is self-reported.** The platform gives graders each case's cost
  total, not which model it came from. A case that went to a stronger model
  shows it in its cost on the run page.
- 200 questions: a run's score moves with which questions were drawn; see the
  interval on the run page.

## Acknowledgements

Questions and answers come from MMLU-Pro (Wang et al., 2024), released by
TIGER-Lab under the MIT License. See [ATTRIBUTION.md](ATTRIBUTION.md).

```bibtex
@misc{wang2024mmlupro,
      title={MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark},
      author={Yubo Wang and Xueguang Ma and Ge Zhang and Yuansheng Ni and Abhranil Chandra and Shiguang Guo and Weiming Ren and Aaran Arulraj and Xuan He and Ziyan Jiang and Tianle Li and Max Ku and Kai Wang and Alex Zhuang and Rongqi Fan and Xiang Yue and Wenhu Chen},
      year={2024},
      eprint={2406.01574},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2406.01574},
}
```
