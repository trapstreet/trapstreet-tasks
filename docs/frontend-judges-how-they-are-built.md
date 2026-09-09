# How frontend LLM judges are actually built — and where ours stands

Written after `frontend_silent_defects`' pairwise gate scored 5/9, to check the
design against what the field does rather than against my own reasoning.

## The two numbers that should govern everything else

[WebDevJudge](https://arxiv.org/abs/2510.18560) (ICLR 2026) is the paper for
this exact question: it measures (M)LLMs *as critics of web development
quality*, on 654 instances drawn from WebDev Arena preference data, annotated
with rubric trees over three dimensions — intention, static quality, dynamic
behaviour.

| | agreement |
|---|---|
| human experts, pairwise | **84.82%** |
| best LLM pairwise (Claude-4-Sonnet) | **66.06%** |
| best LLM single-answer (Claude-3.7-Sonnet) | **60.86%** |

"No current model achieves a sufficient level of agreement with expert
judgments", and performance **plateaus below the mid-70s**.

Two consequences for us, and the second is the one that matters:

- Our pairwise gate scored 5/9 = **55.6%**, against a published ceiling of
  ~66%. That is below the state of the art but not by much — and at n=9, the
  difference between 5/9 and 6/9 is a single item.
- **Our pre-registered bar of ≥8/9 is 89%, which is above what anyone has
  achieved and above the human ceiling minus noise.** The gate was set against
  chance, not against the field. It has to be re-set before a re-run means
  anything, and nine pairs cannot separate 56% from 66% in either direction.
  That, not cost, is the reason to hold the next run.

## What the literature validates in our design

**Pairwise over pointwise.** WebDevJudge: pairwise beats single-answer grading
by **over 8 percentage points across models**. Independently,
[a 2026 position-bias study](https://arxiv.org/abs/2602.02219) finds pointwise
judges favour the first position **60–70%** of the time on identical responses,
while pairwise sits near 50–50. We switched to pairwise. Right call.

**Balanced and swapped order.** That same paper's mitigation for pairwise is
randomising or averaging over orderings. Our stage 1 balances first/second and
stage 2 swaps every pair. Right call — and our observed 4/9 first-position rate
is what a debiased setup should look like.

**More than one screenshot.** [ArtifactsBench](https://huggingface.co/papers/2507.04952)
captures **three staged screenshots — before, during and after a scripted
interaction** — and its ablation confirms multiple screenshots significantly
improve agreement with humans over a single image. This is the one design
decision the literature validates outright: our state walker, which drives the
page and captures each state, is the same move.

**Measuring the human ceiling first.** WebDevJudge's annotation reached 89.7%
inter-annotator agreement with ties, 94.0% without — "substantially better than
MT-Bench's 63%" — and they report it as the ceiling every judge is measured
against. We measured the task owner at 9/9 with no position bias before
measuring the judge. Right order.

## What the literature says we have wrong

### 1. Code is the critical input, and our gate has none

WebDevJudge tested judges on source only, screenshots only, and both.
**Removing the code hurt more than removing the screenshots.**

Our gate is screenshot-only, because the nine labelled pages were generated out
of band and their HTML is gone. This is a likely dominant cause of the 5/9, and
**no prompt change can fix it** — it needs pages whose source we still have.

### 2. A global rubric is the wrong shape — and this cuts against what I just built

This is the finding that undercuts the rewrite:

> "Under the pairwise evaluation, the Direct setting achieves agreement rates
> comparable to guidance-based methods" — external guidance provides only
> **marginal** benefits, because "evaluation capability is an internalized skill
> in modern LLMs".

So the five UICrit clusters and the standard-before-verdict schema are a *better
global rubric*, and a better global rubric is exactly the thing measured as
marginal in a pairwise setting. Expect a small effect, not a rescue.

The nuance that saves rubric-writing: in **single-answer** grading, binary
rubrics substantially outperform multi-point Likert scales — "verifiable
evaluation protocols yield more reliable judgments when there is a lack of
relative information". Rubrics matter pointwise. Pairwise, the comparison
already carries the information a rubric would supply.

**And the two papers do not actually disagree.** ArtifactsBench reaches
**90.95% pairwise agreement with front-end engineers** and **94.4% ranking
consistency with WebDev Arena** — far above WebDevJudge's 66% — using a rubric.
The difference is the shape:

| | WebDevJudge | ArtifactsBench |
|---|---|---|
| rubric | one fixed tree over 654 instances | **a 10-dimension checklist generated per task** |
| calibration | — | 10% human-curated seed at Cohen's κ≥0.8, reused as few-shot |
| axes | intention / static / dynamic | 5 vision-oriented + **5 code-oriented** |
| capture | — | three staged screenshots, headless Chromium, deterministic seeds |

A rubric that says the same thing about every brief adds little. A checklist
derived from *this* brief's own requirements is where the 90% comes from.
UICrit's finding points the same way: few-shot examples **retrieved by task and
visual similarity** were worth a 55% gain, which is per-instance grounding
again, arriving from a third direction.

Note what that costs. ArtifactsBench's checklists are human-refined against a
κ≥0.8 seed set. That is a labelling programme, not a next step. It is recorded
here as where the number comes from, not as a plan.

### 3. Why LLM judges fail here at all

WebDevJudge names three failure modes, and they are not rubric problems:

- **Functional-equivalence blindness** — judges adhere to literal
  interpretation rather than intent, and cannot see that two different
  implementations satisfy a requirement identically.
- **Feasibility verification gap** — LLM judges have moderate recall but low
  precision (they find the relevant code but cannot verify it executes);
  agentic judges invert it, failing on their own navigation limits rather than
  on the implementation.
- **Inherent bias** — position bias persists *despite explicit instructions*:
  "instruction alone is insufficient to eliminate these deeply embedded
  inductive biases."

The paper's conclusion is that closing the gap needs "fundamental deficiencies
in calibration capability" addressed, not better protocols.

## Where that leaves the design

| decision | verdict |
|---|---|
| pairwise, forced choice | keep — validated twice |
| balanced order, swap in stage 2 | keep — the published mitigation |
| walker capturing each state | keep — ArtifactsBench's ablation is exactly this |
| measure the human ceiling first | keep |
| **screenshot-only input** | **wrong — code is the more important half** |
| **one global rubric for every brief** | **wrong shape — marginal in pairwise** |
| **≥8/9 gate** | **mis-calibrated — above the published ceiling** |

The cheap consequence: the 18 pages from the 2026-09-06 run still have their
`stdout` on disk, so their **source and their captures both exist**. Six briefs
× three arms gives **18 same-brief pairs** — twice the current gate, with code,
at the size where 56% and 66% begin to separate. What is missing is labels, and
that is the same elicitation the owner has already been shown to do reliably.

## Sources

- [WebDevJudge: Evaluating (M)LLMs as Critiques for Web Development Quality](https://arxiv.org/abs/2510.18560) — ICLR 2026
- [ArtifactsBench: Bridging the Visual-Interactive Gap in LLM Code Generation Evaluation](https://huggingface.co/papers/2507.04952)
- [Am I More Pointwise or Pairwise? Revealing Position Bias in Rubric-Based LLM-as-a-Judge](https://arxiv.org/abs/2602.02219)
- [UICrit](https://arxiv.org/abs/2407.08850) — the design-critique side, written up in [writing-a-judge-rubric.md](writing-a-judge-rubric.md)
- [WebDev Arena](https://arena.ai/blog/webdev-arena) — Bradley-Terry over 80,000+ human votes, the preference data WebDevJudge is built from
