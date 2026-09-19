# Attribution

This task is built on **Mind2Web**, and the pages, goals and action sequences
it uses are the work of its authors, not ours. What is ours is the case
selection, the element extraction, the equivalence sets, the id renumbering and
the scoring.

> Xiang Deng, Yu Gu, Boyuan Zheng, Shijie Chen, Samuel Stevens, Boshi Wang,
> Huan Sun, Yu Su. *Mind2Web: Towards a Generalist Agent for the Web.* 2023.

```bibtex
@misc{deng2023mind2web,
  title={Mind2Web: Towards a Generalist Agent for the Web},
  author={Xiang Deng and Yu Gu and Boyuan Zheng and Shijie Chen and Samuel Stevens and Boshi Wang and Huan Sun and Yu Su},
  year={2023},
  eprint={2306.06070},
  archivePrefix={arXiv},
  primaryClass={cs.CL}
}
```

- Dataset: <https://huggingface.co/datasets/osunlp/Mind2Web>
- Project: <https://osu-nlp-group.github.io/Mind2Web/>
- Licence: Creative Commons Attribution 4.0 International (CC-BY-4.0)

## Why this repository ships no dataset files

The licence permits redistribution with attribution. The authors nonetheless
ask, in the dataset's own documentation:

> Please DO NOT redistribute the unzipped data files online.

So we don't. This repository carries the transformation — which actions are
used, how elements are extracted, how ids are renumbered — and `prepare.py`
fetches the data from the authors' own distribution on your machine.
`expected.sha256` pins the result so a run is still verifiable.

## Train split only

Only Mind2Web **train** shards are used. The test splits are password-protected
by the authors specifically to keep them out of model training corpora, and
pulling them into an open leaderboard would defeat that.
