# Attribution — model_routing

Every question and answer in this task comes from **MMLU-Pro** by TIGER-Lab.

- **Dataset:** MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark
- **Source:** [TIGER-Lab/MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro), file
  `data/test-00000-of-00001.parquet` at revision
  `b189ec765aa7ed75c8acfea42df31fdae71f97be` (sha256
  `0e24a191921c2f453518a537a8b2117bd137e7714d4ef1565e9ba06c1ecb9ad8`)
- **License:** MIT, as declared on the dataset card.

## Changes made

- **Selection.** 200 test questions, 100 from `law` and 100 from `engineering`,
  drawn with a fixed seed after removing 200 calibration questions (listed in
  `calibration_question_ids.json`, drawn the same way).
- **Format.** `question` is unchanged; `options` are keyed by letter
  (`A`, `B`, ...) in their original order. Subject, source and answer are not
  shipped with the cases.

## Citation

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
