# professional_charts — the public half

Twenty-seven questions about nineteen charts of the kind professionals actually
read: Bode plots, Smith charts, ternary phase diagrams, NMR spectra, control
charts, P&IDs, burndowns, contour sections.

The answers, the judge and the grader are held privately, so **`tp run` will not
score against this directory** — nothing here can tell you whether an answer is
right.

- `traptask.yaml` — the case list, for the platform.
- `traplite-question.yaml` — the same questions as one self-contained string
  each, for a client that fetches this file by URL and cannot be handed a file.
  Each names its chart by a commit-pinned raw URL.
- `inputs/case_NN/question.txt` — the same questions in the layout a local
  runner expects, with `chart.txt` naming the image.
- `expected.sha256` — a manifest of every artefact a solution is served. The
  answers are not in it and are not derivable from it.

## Where the questions come from

Nineteen are Chartography's own, and **their answers are public** — see
`ATTRIBUTION.md`. Eight are ours and their answers have never been published.
A submission that scores well on the first group and poorly on the second is
telling you something; the board does not currently separate them.

## Do not move or rename anything here

`inputs/charts/` is load-bearing. Twenty-seven live questions name those images
by raw URL pinned to a commit, because the benchmark format that serves them
carries no inputs of its own.
