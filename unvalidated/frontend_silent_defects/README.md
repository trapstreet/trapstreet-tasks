# frontend_silent_defects — the page looks finished

A tool is given a brief and prints one self-contained HTML page. The judge opens
that page in real Chromium, checks whether it works, and then reads it the way a
designer would.

**What the score separates, and what it does not.** It puts a mini model below a
frontier model. It cannot order frontier models among themselves: on the runs
behind it, three frontier arms were within noise of each other. Treat
differences under about 0.05 between two frontier rows as a tie. The
measurements are in [RESULTS.md](RESULTS.md).

## What it measures

Two things, multiplied.

**Does it work?** Deterministic checks in a real browser, on failures that are
invisible in a screenshot:

- **behaviour** — click the annual toggle. Do the prices change?
- **responsive** — at 375px, does anything stick out of the viewport?
- **robustness** — feed it a 240-character plan name, an RTL override, a
  prototype-pollution payload. Does the layout hold, and does nothing execute?
- **constraints** — were the brief's prohibitions and budgets actually obeyed?

**Is it well made?** An LLM reads the rendered page and its source against a
ten-item checklist written for that brief — five items about what the page
looks like, five about how it is built — and answers each one yes or no.

## The cases

| case | deciding family | what it varies |
|---|---|---|
| 01 | behaviour | baseline — one brief, plainly stated |
| 02 | constraints | constraint count, k≈7 (compositional load) |
| 03 | behaviour | a counterfactual requirement, against the obvious default |
| 04 | constraints | prohibitions — what the page must *not* do |
| 05 | behaviour | same checks as 01, brief padded with irrelevant context |
| 06 | robustness | 13 written + 40 generated hostile `__DATA__` payloads |
| 10 | constraints | a budget: ≤70 DOM elements, ≤42 CSS rules, ≤10,500 bytes |
| 07–09 | floor | open briefs — landing page, trustee dashboard, eleven-field form |

## How a case is scored

```
cases 01–06, 10:   deterministic pass rate  ×  checklist fraction
cases 07–09:       floor (0 or 1)           ×  checklist fraction
run score:         mean over all ten cases
```

**The deterministic pass rate** is the fraction of the deciding family's checks
that passed. It is dense rather than pass/fail, because a hard case scored
pass/fail puts every arm at 0.0 and the board cannot say which one got closer.
A check marked **blocker** takes the case to zero: a page that executes injected
markup gets no partial credit.

**The floor** is the whole bar an open brief has to clear: the page loads,
throws nothing, loads nothing from off the page, and does not overflow 375px.

**The checklist fraction** is how many of the ten items the page satisfies.
Each page is read three times and an item counts when at least two reads say
yes. The judge sees the brief, every captured state of the page (the inspector
fills visible fields and presses "next" to reach later steps of a form), and
the source. It is asked for its evidence before its verdict, and it has no
"unclear" option: if the source is missing, the five code items are removed and
the fraction is out of five.

A case that fails its deterministic bar is scored 0 **without the LLM being
called**. A page that does not work has no craft to read, and the submitter is
paying for those calls.

## Running it

The checklist read calls `claude-sonnet-5` through the Anthropic API, **paid by
whoever runs the judge**. Set `ANTHROPIC_API_KEY` in the judge's environment and
install the `anthropic` Python package. A full run is thirty reads — three per
case — and each case reports the tokens it used in `llm_judge_tokens`.

Without a key the run is **not scored**, rather than scored on the deterministic
half alone. That half is saturated — a mini model scored 1.0 on every
deterministic case it ran — so falling back to it would put nearly every
submission at the top. The grader returns
`score: null` with an `unranked_reason` naming the first case that could not be
judged.

The inspector needs Node and a Chrome; it downloads no browser. Set
`CHROME_PATH` if Chrome is not at the macOS default.

## What each case reports

| field | |
|---|---|
| `score` | the case score above |
| `deterministic_score` · `deciding_checks` | the working half, and which checks failed |
| `checklist_satisfied` · `checklist_unmet_items` | e.g. `8/10`, and the numbers of the items missed |
| `checklist_split_items` | items where the three reads disagreed — the judge's own uncertainty on this page |
| `floor_passed` · `states_captured` | open briefs; how many states the walker reached |
| `contrast_violations` · `naming_violations` | axe-core counts — **diagnostic, never part of `score`** |

Item numbers are published; item texts are not. The checklists are part of the
private half.

## Why contrast and labels are diagnostics, not score

A contrast failure is fixed by one bolt-on step: run a checker before returning.
Any tool can copy that the week it sees this board, so a score built on it would
saturate in one release cycle. A dead toggle has no such step — it is fixed by
building it right.

Axe is also the least sensitive family here. On `fixtures/broken.html` — an
unlabelled email input and two `<div>`s acting as buttons — axe's entire ruleset
reports one thing, contrast: a `placeholder` counts as an accessible name, and a
`<div>` has no button role to name.

## Layout

This directory is the **public half**: the briefs a tool is served, the case
list, and the write-up.

```
inputs/case_NN/brief.md   the brief — the whole of what a solver sees
traptask.yaml             the case list, and nothing else
expected.sha256           a digest over the private half
README.md · RESULTS.md    method and measurements
```

Everything that decides a score is held privately, in
`trapstreet-tasks-private/unvalidated/frontend_silent_defects/`:

```
expected/case_NN/          which family decides the case, and its assertions
judge.py                   the case score: inspector, then the checklist read
grader.py                  the run score; refuses to rank a partly judged run
check/inspect.mjs          puppeteer-core against system Chrome, axe-core
                           injected. Runs the assertions, generates the hostile
                           payloads, walks multi-step UIs, captures each state
check/checklists/          ten items per brief — the LLM judge's rubric
check/checklist_score.py   one checklist read of one page
check/score_all.py         marks the checklist against the owner's labels
fixtures/ · tests/         the judge's own test set, end-to-end through a browser
labels/                    the owner's pairwise judgments, and the runs measured
                           against them
tools/gold_hash.py         regenerates expected.sha256 into both halves
```

`tp run` will not score against this directory. The digest fixes the hidden
half in place so it stays checkable, and it covers the inspector and the
checklists as well as `expected/`: the inspector *generates* the hostile
payloads and the checklists *are* the LLM judge's rubric, so changing either
moves a score with `expected/` untouched.
