# Attribution — response_safety_calibration

Every conversation and every rating in this task comes from **DICES-350**,
part of the DICES dataset by Google Research.

- **Dataset:** DICES — Diversity in Conversational AI Evaluation for Safety
- **Source:** [google-research-datasets/dices-dataset](https://github.com/google-research-datasets/dices-dataset),
  file `350/diverse_safety_adversarial_dialog_350.csv` at commit
  `b5596d9edd585361967991a591abc7b11fb1f7a3` (sha256
  `63cb8620eb04e64957f9e45b1f7cb3d079c4eed8e8b28909f46e0b7038ce4301`)
- **License:** [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/),
  © Google LLC. Provided "as is", without warranty.

## Changes made

- **Selection.** 75 of the 350 conversations: a stratified random sample, 25
  from each third of difficulty, where difficulty is how far three reference
  models' estimates fell from the rater share (see README.md).
- **Targets.** A case's target is the share of "Yes" among "Yes" and "No"
  answers to `Q_overall` ("Unsure" excluded), computed after removing the 19
  raters the dataset authors list under "Removed raters" in `350/README.md`.
- **Format.** `context` is split into turns (`{speaker, text}`, speaker labels
  kept as `USER` / `LAMDA`); `response` is unchanged. Rater demographics,
  individual ratings, harm labels and expert gold labels are not shipped.

## Content warning

The conversations were written by people deliberately trying to make a chatbot
say something unsafe. They include offensive, violent and discriminatory
language.

## Citation

```bibtex
@misc{aroyo2023dicesdatasetdiversityconversational,
      title={DICES Dataset: Diversity in Conversational AI Evaluation for Safety},
      author={Lora Aroyo and Alex S. Taylor and Mark Diaz and Christopher M. Homan and Alicia Parrish and Greg Serapio-Garcia and Vinodkumar Prabhakaran and Ding Wang},
      year={2023},
      eprint={2306.11247},
      archivePrefix={arXiv},
      primaryClass={cs.HC},
      url={https://arxiv.org/abs/2306.11247},
}
```
