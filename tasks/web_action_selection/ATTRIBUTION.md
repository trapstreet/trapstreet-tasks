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

## What this repository publishes, and what it does not

`inputs/` holds 46 pages derived from Mind2Web, one per case. They are not the
dataset: they are a subset of the **train** split, cleaned by the authors,
with every element id renumbered to a shuffled range so that the dataset's own
node ordering cannot be used to recover the answer.

The licence permits redistribution with attribution. The authors also ask, in
the dataset's documentation:

> Please DO NOT redistribute the unzipped data files online.

We read that as addressed to mirroring the dataset, and this is not that: 46
derived pages from the split the authors themselves publish openly on
HuggingFace, with the identifiers changed. The reason they give for protecting
the **test** split — keeping it out of model training corpora — is why we use
none of it.

We publish the pages rather than a download script for two reasons. A build
recipe cannot be served by a leaderboard that reads a pinned commit and
executes nothing. And a setup step that downloads the shard would place
`pos_candidates`, which contains the correct element for every case, on the
disk of everyone attempting the task.

`prepare.py` reproduces `inputs/` from the authors' distribution and checks it
against `expected.sha256`, so the derivation is auditable.

## Train split only

Only Mind2Web **train** shards are used. The test splits are password-protected
by the authors specifically to keep them out of model training corpora, and
pulling them into an open leaderboard would defeat that.
