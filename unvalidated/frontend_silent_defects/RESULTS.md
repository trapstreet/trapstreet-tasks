Measurements in the order they were taken. Each verdict applies to the version
of the instrument it measured. The version that ships is the last one: the
deterministic checks multiplied by an LLM checklist read. The evidence for it,
and its limits, are in [What ships](#what-ships--the-checklist-as-a-tier-separator).

---

# Does it discriminate? No.

**2026-09-06. Three arms, six scored cases, eighteen scores, all 1.00.**

| case | lever | opus-relay | gpt-terra | kimi-k3 |
|---|---|---|---|---|
| case_01 | baseline | 1.00 | 1.00 | 1.00 |
| case_02 | constraint count (k≈7) | 1.00 | 1.00 | 1.00 |
| case_03 | counterfactual | 1.00 | 1.00 | 1.00 |
| case_04 | prohibitions | 1.00 | 1.00 | 1.00 |
| case_05 | no-op distractor | 1.00 | 1.00 | 1.00 |
| case_06 | 13 hostile payloads | 1.00 | 1.00 | 1.00 |
| | | **6/6** | **6/6** | **6/6** |

`claude-opus-5`, `openai/gpt-5.6-terra-pro`, `moonshotai/kimi-k3`. Identical bare
relays — same `solution.py`, no system prompt, no tools, `max_tokens=16000` —
differing only in the model. Arms at
[Ruqii/trapstreet-solutions@d2693d8](https://github.com/Ruqii/trapstreet-solutions/tree/d2693d8/frontend_silent_defects).

The rule was written before the run: two arms differing on two or more cases
means it discriminates; everything passing everything means it does not ship.

**It does not ship.**

## The checks were not a no-op

Worth stating, because "everything passed" and "nothing ran" produce the same
number. Every case ran its full set and every check in it passed:

```
case_01  behaviour 2/2   robustness 1/1                  responsive 1/1
case_02  behaviour 7/7   robustness 1/1                  responsive 1/1
case_03  behaviour 2/2   robustness 1/1  constraints 2/2 responsive 1/1
case_04  behaviour 2/2   robustness 1/1  constraints 3/3 responsive 1/1
case_05  behaviour 2/2   robustness 1/1                  responsive 1/1
case_06  behaviour 2/2   robustness 13/13                responsive 1/1
```

Thirteen adversarial `__DATA__` payloads — empty strings, 240-character names,
HTML in a price field, missing keys — survived by all three. Zero console
errors, zero horizontal overflow at 375px, across the board.

## The one thing that did separate, and why it stays unscored

The a11y diagnostics moved, and not in the same direction for each arm:

| | case_01 | 02 | 03 | 04 | 05 | 06 |
|---|---|---|---|---|---|---|
| **contrast** opus-relay | 0 | 3 | 0 | 0 | 0 | 0 |
| gpt-terra | 0 | 2 | 4 | 2 | 0 | 4 |
| kimi-k3 | 0 | 0 | 0 | 1 | 0 | 0 |
| **naming** opus-relay | 5 | 0 | 4 | **19** | 0 | 0 |
| gpt-terra | 0 | 0 | 0 | 0 | 0 | 0 |
| kimi-k3 | 0 | 0 | 0 | 2 | 0 | 0 |

The arms are genuinely different here: gpt-terra never leaves an unlabelled
control and has the most contrast failures; opus-relay is the reverse, with 19
naming violations on the prohibitions case; kimi-k3 is cleanest on both.

This is not a rescue, and it is not being promoted to `score`. The reason a11y
was excluded is in the README and it has not changed: a contrast or label
failure is fixed by running a checker before returning — one bolt-on step, which
any tool can copy the week it sees the board. A column that separates today and
saturates on the next release is worse than no column, because the ranking it
produces reverses without anything real having changed. Moving it into the score
now, *because* it is the only thing that moved, is the exact post-hoc adjustment
the pre-registered rule exists to prevent.

## Why this was the expected outcome

The first probe passed 20/20, and METR's measurement is that task length
dominates agent success (R²=0.83), with frontier models near-100% under about
four human minutes. This brief is a ten-minute job. Adding constraints does not
change its length, and case_02 (k≈7) is the proof: seven simultaneous
requirements, all three arms clean.

The finding is not "frontend cannot be benchmarked". It is narrower and it is
the one worth writing down: **at a ten-minute brief, deterministic frontend
checks do not separate frontier models.** Everything the instrument can see —
behaviour, robustness, responsive, constraint compliance — they all already do.

## What this run also settles

The three open briefs are not rescued by this either. The judge that would have
read them scored at chance (`labels/gate_stage1.json`), and the deterministic
floor they *are* scored against was cleared by every arm here.

So the task has no scored dimension that separates and no unscored one that can
be trusted. It stays in `unvalidated/` permanently.

## Cost

trap-cli recorded `cost_usd_total: null` for all three — the SDK paths this
relay uses are not wired into its cost tracking. Estimated from output size
(~13KB of HTML per page, 18 pages): well under $1.50.

---

# The rebuilt version — one arm so far

**2026-09-06, `kimi-k3` against Moonshot directly.** Seven scored cases, dense
scoring, the generated hostile family and the budget case both live.

| case | lever | score | checks |
|---|---|---|---|
| case_01 | baseline | 1.000 | 2/2 |
| case_02 | constraint count (k≈7) | **0.571** | 4/7 |
| case_03 | counterfactual | 1.000 | 2/2 |
| case_04 | prohibitions | 1.000 | 3/3 |
| case_05 | no-op distractor | 1.000 | 2/2 |
| case_06 | 13 written + **40 generated** payloads | 1.000 | **53/53** |
| case_10 | budget (70 / 42 / 10,500) | 1.000 | 3/3 |

**The two new mechanisms did not bite.**

*Generated hostile data:* 53/53. All forty generated payloads survived —
prototype pollution, lone surrogates, 300 combining marks, whole-`__DATA__`
type swaps, five injection strings. The generator is not toothless: it found a
live XSS in this repo's own `fixtures/good.html` on its first run. The model's
page is simply better than our fixture was.

*Budget:* 3/3. Stated in the brief, the ceiling is easy to hold. It separates
budgeted from unbudgeted output — `fixtures/overbuilt.html`, real output from
the morning run, misses all three limits — but that is not a capability
difference, it is the difference between being told and not being told.

**The one that moved is the one we already had, and it wobbles.** case_02 is the
seven-constraint case. Three runs of the same model:

| run | endpoint | case_02 |
|---|---|---|
| 10:49 | OpenRouter | 7/7 |
| 16:42 | OpenRouter | 6/7 |
| 17:58 | Moonshot direct | 4/7 |

The 4/7 failure is real, not a judge artifact — the page is complete (ends in a
proper `</html>`, 12,601 bytes) and simply never emits `data-testid="tier"` or
`data-testid="price"`. It dropped the tier-rendering requirement outright.

Two readings are still open and one run cannot separate them: run-to-run
variance, or a difference between the routed and the direct endpoint. What is
already clear is that **a case whose score moves 7/7 → 4/7 across runs of one
model cannot be read from a single run**, which puts a question over the
morning's 18/18 as well. Repeats come before more arms.

---

# The pointwise checklist scorer — first runs

**2026-09-09.** `check/checklist_score.py`, `claude-sonnet-5`, ten binary items
from `check/checklists/case_01.json`, source and both captures supplied.

| page | runs | score | items that disagreed with themselves |
|---|---|---|---|
| kimi-k3's case_01 page | 3 | **0.9 · 0.9 · 1.0** | item 3 |
| `fixtures/broken.html` | 2 | **0.5 · 0.5** | none |

**It separates**, with no overlap, and it separates for the right reasons. On the
broken fixture it named all three of that fixture's known defects unprompted:

```
 7 no  No annual price is ever computed or displayed; price always shows t.monthly
 8 no  `<h2>${t.name}</h2>` built via template literals assigned to innerHTML
 9 no  data-testid="billing-monthly" is entirely absent from the markup
```

The evidence lines are specific enough to check — `padding: 32px 28px`,
`.price is 44px/800 weight while .price-per is 15px/600`, `el() helper sets
node.textContent` — which is the code half of the checklist doing work rather
than the model guessing from the picture.

## The defect this run found

First real run, first judge defect, again. On the broken fixture item 10 —
"re-rendering after a toggle does not discard what the user has typed" — scored
**yes**, with this reasoning:

> "The Annual toggle has no click handler at all, so no re-render is ever
> triggered that could wipe the email input."

True, and worthless. **An item phrased as "X does not break Y" is free for a page
that never does X.** Three items in the shared core had this shape and all three
are now written as behaviour-then-property: *an annual price is shown, and it is
computed from the monthly one; showing no annual price does not satisfy this.*

After the fix the broken fixture scores 0.5 twice with **zero** disagreement
between runs, and item 10 reads correctly:

```
10 no  The Annual toggle div has no click handler or script reference
       (`billing-toggle` is never read in JS), so prices never change
```

## What is still open

Stability is one item in ten on the good page — item 3, "exactly one thing
carries the emphasis, and it is a plan", the most judgment-dependent item on the
list. Score spread 0.100, sd 0.047 over three runs. Whether that is small enough
for a published column is not settled by two pages.

And nothing here says the scorer agrees with a *person*. Separating a page built
by a frontier model from a fixture built to be broken is a floor, not a
validation. That needs `check/pairwise_gate.py` against real labels, at a set
size the gate itself will tell you it needs.

---

# The judge against a person — 2026-09-10

Fifty-one same-brief comparisons over 35 pages from four models, labelled blind
by the task owner, seventeen of them repeated with the sides swapped. Then
`checklist_score.py` scored all 35 pages pointwise and was marked against her.

## Her labels held up

| | |
|---|---|
| self-agreement | **13/17 = 76%** (p = 0.024 against guessing) |
| left-hand picks | 39/68 = 57% (p = 0.28 — no position bias) |
| briefs containing a cycle | **0 of 9** |
| briefs with a strict transitive order | 6 of 9; the other three have one tie each, from a flip |

A random tournament over four pages is transitive 37.5% of the time, so eight
transitive four-page briefs by chance is **p ≈ 4×10⁻⁴**. She said she could not
choose. She could: 76% test-retest implies an underlying consistency of about
**86%**, which is the band WebDevJudge measures between its human experts
(84.82%), and which is also the ceiling any judge can reach against these labels.

Unblinded, her ranking by wins: **opus-relay 28 · gpt-terra 17 · kimi-k3 12 ·
gpt-mini 11.** She put the strongest model first without being told which was
which.

## The judge did not

**17/47 = 36%.** The bar written before the run was ≥30/47. It fails, and not
narrowly: p(≥17 | guessing) = 0.98.

But the number that explains it is the tie count.

| | |
|---|---|
| pairs it called a tie | **18/47 = 38%** |
| pairs where it expressed a preference | 29/47 |
| of those, agreeing with her | 17/29 = **59%** (p = 0.23 — chance) |
| score range over 35 pages | **0.6 – 1.0** |
| pages scoring 0.9 or 1.0 | **27 of 35** |

**The checklist saturates.** Ten items written from each brief, and frontier
models satisfy eight to ten of them. On `case_07` all four pages scored 1.0, so
every one of its five comparisons was a tie and the brief scored 0/5. Where the
judge does have an opinion it is at chance — worse than the 66% a published
pairwise judge reaches, though this is pointwise and 29 comparisons cannot
separate 59% from 66% anyway.

## The one place it did agree

Averaged per arm, against her ranking:

| arm | judge mean | hers |
|---|---|---|
| opus-relay | **0.944** | 1st |
| kimi-k3 | 0.925 | 3rd |
| gpt-terra | 0.900 | 2nd |
| gpt-mini | **0.822** | 4th |

Both put the same model first and the same model last, and disagree only on the
middle two. So the measure is useless for ranking two pages and not useless for
ranking four models over nine briefs — which is what a leaderboard actually
does. With four arms that is one observation, not a finding: getting both ends
right by chance is about 8%.

## What this closes

Every absolute, item-based measure built for this task has saturated at the
frontier: the deterministic checks at 18/18, and now an LLM checklist with 27 of
35 pages at 0.9 or above. The one measure that separated these pages is the one
that never assigns a number to a page on its own — **a person comparing two of
them**, at 76% test-retest and zero cycles.

That is the relational/absolute split from
[docs/raising-task-difficulty.md](../../docs/raising-task-difficulty.md)
arriving from a third direction, and it is now the finding rather than the
inference: *a page has no quality you can read off it alone; it only has a
quality relative to another attempt at the same brief.*

---

# What ships — the checklist as a tier separator

**2026-09-10. This analysis was done after the gate above failed, and was not
pre-registered.** It is stated here as what it is.

The page-level question failed. A leaderboard asks an arm-level one: over the
same briefs, do one model's pages score above another's? Same 35 checklist
scores as above, compared brief by brief between arms, ties dropped from the
sign test:

| comparison | wins–losses (ties) | two-sided sign p |
|---|---|---|
| opus-relay vs gpt-mini | **7–0** (2) | 0.02 |
| kimi-k3 vs gpt-mini | **5–0** (3) | 0.06 |
| gpt-terra vs gpt-mini | **6–1** (2) | 0.12 |
| opus-relay vs gpt-terra | 4–1 (4) | 0.38 |
| opus-relay vs kimi-k3 | 1–0 (7) | 1.00 |
| gpt-terra vs kimi-k3 | 2–3 (3) | 1.00 |

Every frontier arm sits above the mini model; the frontier arms cannot be told
apart. The deterministic half contributes nothing to that: gpt-mini scored 1.0
on all six deterministic cases of the rebuilt version it ran (2026-09-09).

The owner's labels support this only partly. They put gpt-mini last — 11 wins —
but one win behind kimi-k3's 12, where the checklist has kimi-k3 5–0 ahead.

So the claim the score makes is the narrow one: **mini below frontier.** The
README says so at the top.

## What differs from the instrument that was measured

- **Three reads per page, majority per item**, where the validation used one
  read. This reduces variance; it was not itself validated.
- **Captures**: the same 1280×1600 tiles, cut to 900px on the long side. The
  validation set was encoded by `sips` at JPEG 65; the judge encodes in Chrome
  at 88, which matches it in bytes on the same capture (60K / 72K at Chrome 85 /
  90 against sips-65's 68K).
- **Composition**: deterministic pass rate × checklist fraction, with a blocker
  or a failed floor scoring 0 before the checklist is read.

## The gate for the launch run — written before it

Four arms — opus-relay, gpt-terra, kimi-k3, gpt-mini — through the shipped
judge, all ten cases, fresh generations. It ships as a ranked task if both hold:

1. gpt-mini's run score is the **lowest of the four**.
2. Pooled over the three frontier arms, case-level comparisons against gpt-mini
   (ties dropped) favour the frontier arm at **one-sided sign-test p < 0.05** —
   for example at least 15 of 20 non-tied comparisons.

If either fails, it does not ship as a ranked task. Whether the frontier arms
order among themselves is reported, not required: nothing above says they will.

---

# Earlier — the instrument before 2026-09-06

## First real run, 2026-08-31 — and the judge bug it found

One arm (`opus-ceiling`, a bare `claude-opus-5` relay) over the six scored cases.

**It passed everything.** 20/20 on the five levers, then 13/13 on the hostile-data
case. The task does not currently separate anything at the frontier.

The hostile-data case *appeared* to catch it — 0.0, "1 element(s) clip their
content" on the 240-character plan name. That was the judge being wrong. The page
had line-clamped the heading to three lines, added an ellipsis, and put the full
string in a `title` attribute: correct handling, better than this repo's own
`fixtures/good.html`, which simply wraps. The check now fires only when content
vanishes with **no** affordance — no ellipsis, no title, no aria-label.

Two things follow. The repo's claim that every task's first real run turns up a
judge defect held again. And the axis is wrong: METR measures task length as the
dominant predictor of agent success (R²=0.83), with frontier models near-100%
under about four human-minutes. This brief is a ten-minute job. No number of
extra constraints closes that gap.

## The first judge panel — a pairwise gate at 5/9

`check/panel.py` is a three-lens LLM judge — a design director who sees the
render, an engineer who sees only the source, a client checking the brief — over
four axes on a 1–3 forced choice, calibrated against seven screenshots the task
owner sorted blind on that same scale. The method is written up in
[docs/writing-a-judge-rubric.md](../../docs/writing-a-judge-rubric.md).

It was run twice over nine pages from three different labs, authors hidden, and
appeared to fail badly: two pages sitting in its own prompt labelled "2" came
back 3.00 and 2.75, its ranking contradicted the owner's held-out judgments, the
mean swing between runs was 0.36 on a 1–3 scale, and `1` was never used once
across 72 scores.

**Then the ground truth turned out to be partly wrong.** Elicited pairwise
instead — nine same-brief pairs, each shown twice with the sides swapped — the
owner agreed with herself 9/9 with no position bias, and every brief came out
transitive. Two of the three briefs reproduced her earlier overall sort. The
landing brief inverted completely: `good_landing.jpg`, the level-3 landing
anchor, is the page she now ranks *last* of three. So "it contradicted its own
anchors" was, on that page, the anchor being wrong.

So the panel was rebuilt as a **pairwise** judge — two attempts at one brief,
the same words she was given, forced choice — and put through a gate written
before it ran: nine same-brief pairs with the first/second order balanced,
stop at ≤6/9, and ≥8/9 to pass.

**It scored 5/9. Chance is 4.5.** It picked the first-shown page 4 times out of
9 and her page was first 4 times out of 9, so position bias explains nothing.
Per brief: dashboard 3/3, landing 1/3, form 1/3. Stage 2 was not bought.

That is the honest verdict the anchor mismatch was not. The judge is out of the
score and out of the diagnostics, and `check/panel.py`, `check/anchors/` and
`check/pairwise_gate.py` are kept only as record.

One confound and one hypothesis, both worth carrying. The form stimuli are
pre-walker captures showing about two of eleven fields, so that brief was never
fairly asked — the landing brief was, and it went 1/3. And every reason the
judge gave is about information completeness or reassurance: "concrete proof",
"scannable", "all key metrics", "reassuring microcopy". It reads the copy and
the feature inventory. On a dashboard, where completeness genuinely is the job,
it goes 3/3; where restraint decides it, 2/6. With n=9 that is a mechanism worth
naming, not a finding.

Three findings survive, and the first is the one worth carrying:

1. **Check the labels before blaming the judge.** Her pointwise good/bad labels
   inverted on a third of the material; her pairwise ones held 9/9. Ask a human
   for comparisons, not grades.
2. **A within-brief order is ordinal, not absolute.** Knowing 07B beats the
   other two landings does not make it a "3", so `anchors.json` cannot be
   rebuilt from this data — which is the real argument for moving both the
   elicitation and the judge to pairwise, more than anchor count ever was.
3. **The form cases were never judgeable from an image at all**: those pages are
   exactly one viewport tall because steps 2–4 do not exist until a click, so
   every capture showed two of eleven fields. That one was a defect in the
   *input*, not the judge, and it is fixed — see below.

## Capturing a UI that has states

Fixed 2026-09-05, after the panel run made the cost visible.

The inspector now **walks** the page instead of photographing it once. It fills
the visible fields with plausible values, presses the control that reads like
"next", and captures again — up to four states, stopping the moment a click
changes nothing or would leave the page. Each state is captured as 1280×1600
tiles, so neither the fold nor legibility is lost. `states_captured` and, per
state, the label it pressed are reported.

Open briefs cannot declare a click path — we do not know the selectors — so this
is a heuristic and it is honest about being one: it reports what it pressed, and
a page it cannot advance simply reports one state. `fixtures/wizard.html` is a
three-step form whose steps 2 and 3 are not in the DOM until step 1 validates,
and `tests/test_judge.py` fails if the walker stops short of it.

This does not rescue the panel. It removes one reason the panel had no chance.

## What changed after the 18/18

**Scoring is dense.** `grade()` returns the fraction of the deciding family's
checks that passed, not 1.0-or-nothing. Binary cost nothing while every arm
scored 1.00; it becomes the dominant failure mode the moment a case is hard,
because every arm lands on 0.0 and the board cannot say which got closer.
Long-Horizon-Terminal-Bench measured 62.8% of runs making partial progress that
pass/fail discards. **Blockers** survive: a check the spec marks `blocker` takes
the case to zero — a page that executes injected content gets no partial credit.

**The hostile data is generated, not written.** `case_06` keeps its thirteen
written payloads and adds forty seeded generated ones over 29 hostile atoms —
lone surrogates, RTL overrides, 300 combining marks, prototype pollution, whole
`__DATA__` type swaps, five injection strings. A written list has a ceiling the
author can see; three frontier arms took the old thirteen 13/13. The recipe
crossing the process boundary is JSON-safe and the values are built in-page,
because `undefined`, `NaN` and cyclic objects do not survive serialisation.

It found a live XSS in this repo's own `fixtures/good.html` on the first run —
an `<img src=x onerror>` in a plan name executed. The fixture now builds nodes
instead of interpolating into `innerHTML`.

**`case_10` grades restraint against a calibrated ceiling.** 70 DOM elements,
42 CSS rules, 10,500 source bytes, all stated in the brief. The numbers come
from measuring the eighteen pages the three arms actually produced with no
budget stated: nodes ran 67–119, rules 39–61, bytes 9,475–16,473, and **exactly
one of the eighteen met all three at once**. Reachable, and not by accident.

This is as far as FrontierCode's scope discipline translates. It measures scope
against a reference patch; a page generated from a brief has no *before*, so
what survives is a stated ceiling rather than a comparison. Whether that is
enough to separate anything is the open question.

