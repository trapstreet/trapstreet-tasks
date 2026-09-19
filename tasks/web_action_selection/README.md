# web_action_selection

Given a goal, the actions already taken, and a real web page, name the one
element the next action should act on.

The page is handed over whole — a median of about 730 actionable elements, up
to 2,159, in 88,000 characters of HTML. There is no candidate shortlist. Narrowing the page down is the
task, not a step someone else has done for you.

```
ELEMENT: 4821
OP: CLICK
VALUE:
```

## Why there is no shortlist

Most work on this dataset scores a model against ~50 pre-selected candidates.
We measured what that does: handing two very different systems the same
50-candidate shortlist made them score identically — 65.2% each with no action
history, 87.0% each with it, agreeing on the same option 74–87% of the time.
The shortlist was the product. Whatever picked it had already done the work.

So this board gives you the page. A solution that can only rank a shortlist has
to build its own, and that shortlist is now part of what is being measured.

## What you get, and what you print

One directory per case:

| file | what it is |
|---|---|
| `task.md` | this contract |
| `step.md` | goal, actions already completed, step *n* of *m* |
| `step.json` | the same, machine-readable |
| `page.html` | the page, every actionable element carrying `backend_node_id` |

Print three lines anywhere in your output. Only the **last** occurrence of each
is read, so you are free to narrate, show your shortlist, and then commit:

```
ELEMENT: <backend_node_id>
OP: <CLICK | TYPE | SELECT>
VALUE: <text to type or option to select; empty for CLICK>
```

Exactly one element is scored. Listing several candidates does not help.

## Setup

None. The cases are in this repository; clone it and run. No browser, no
Docker, no API key, no download.

`prepare.py` rebuilds `inputs/` from the dataset's own HuggingFace distribution
and checks every byte against `expected.sha256`. You do not need it to run the
task -- it is here so anyone can reproduce the cases from the source and verify
we did not alter them.

## Run it

A solution is a `trap.yaml` plus something that prints the three lines:

```yaml
name: my-solution
cmd: python3 solution.py
timeout: 600
tasks:
  web-action-selection:
    source: git+https://github.com/trapstreet/trapstreet-tasks@<commit>#subdirectory=tasks/web_action_selection
```

```bash
tp run
```

Your solution is invoked once per case with `TRAP_MANIFEST` in the environment:

```python
m = json.loads(os.environ["TRAP_MANIFEST"])
inputs = Path(m["inputs_dir"])          # task.md, step.md, step.json, page.html
step = json.loads((inputs / "step.json").read_text())
page = (inputs / "page.html").read_text()
```

`web_action_selection/lexical-floor` in the solutions repo is a complete
working example that costs nothing to run.

## Scoring

`score` is **element accuracy** — the share of cases where you named the
element the human annotator acted on. The judge is deterministic: an id
compared against a set, no LLM, so grading costs nothing and does not vary
between runs.

It is a set rather than a single id because about a quarter of these pages
carry a second element that renders identically to the correct one — same tag,
same accessible name, same text, e.g. a link duplicated between the top nav and
a sticky header. Naming the twin is the right decision and the page cannot tell
them apart, so every such element is accepted. The set is computed at build
time from the rendered identity, never curated by hand.

Reported beside the score:

| metric | meaning |
|---|---|
| `cases_step_success_rate` | element **and** operation **and** value all right |
| `cases_op_accuracy` | operation right, regardless of element |
| `cases_accuracy_last_step` / `_earlier_step` | the final step of a goal vs. every earlier one |
| `cases_accuracy_large_page` / `_small_page` | above vs. at-or-below the median element count |
| `cases_accuracy_ci_low` / `_high` | 90% interval over 2,000 case resamples |
| `latency_*`, `cost_*` | a page this size is where context cost shows up |

The two split-outs are there because they are the axes that moved when we
pre-registered this. Supplying the prior actions was worth +21.8 points overall
and +34 on late steps. Candidate-set size predicted nothing. A run that
reverses either is telling you something.

## What the case set is made of

| | |
|---|---|
| cases | 46 |
| episodes | 9 |
| websites | 3 — travelzoo (31), kohls (8), sports.yahoo (7) |
| actionable elements per page | 435 / **729 median** / 2,159 |
| page size | 52k / **88k median** / 337k characters |
| step index within its episode | 1 / **4 median** / 10 |
| prior actions supplied | 0 / **3 median** / 9 |
| first step of an episode (no history) | 9 |
| final step of an episode | 8 |
| operations | CLICK 42, TYPE 3, SELECT 1 |
| gold shares its tag with | 4 / **75 median** / 326 other elements |
| gold shares its exact text with | 0 / **2 median** / 10 other elements |
| gold has an indistinguishable twin | 11 |
| gold carries no visible text of its own | 11 |

"Actionable element" excludes Mind2Web's `<text>` wrappers around bare text
nodes: they carry a `backend_node_id` but are not things you can act on, and no
gold is ever one. Counting them would put the median at 1,104 instead of 729.

There is no difficulty label, and no tier. Difficulty on this task has to be
filtered from measured failure rather than asserted from a proxy: the obvious
candidates — page size, step position, how many elements share the gold's tag —
are structural facts, and which of them actually predicts failure is what a run
tells you. The grader splits the score by page size and by step position so the
first run answers that question rather than assuming it.

## Floors

Publish a score against these, not against zero:

| | element accuracy |
|---|---|
| random choice among page elements | 0.14% |
| best trivial rule with no language understanding | **2.2%** |
| best lexical overlap between the goal and an element's rendered text | 4.3% |
| best single rule that ignores language entirely | 2.2% |
| published results on the *shortlist* version of this data | ~42–53% |

The last row is not a target: it is measured against 50 candidates, and this
task gives you about 730. It is here to say what the shortlist was worth.

The second row is load-bearing. In the raw dataset the correct element is at or
near the *minimum* `backend_node_id` on the page, so `min(id)` over clickable
elements scores **45.7%** — roughly published state of the art, with no
language understanding whatsoever. This task renumbers every element id to a
shuffled range, which leaves the document otherwise byte-identical and takes
that rule to 0/46.

The build enforces this, but not as "must score zero": across a dozen position
rules one will eventually land on a page whose last button really *is* the
answer, and a zero gate would then invite deleting the rule rather than fixing
the task. The gate is that **no rule ignoring language may beat the lexical
reference** — the weakest rule that actually reads the page. Today the eleven
language-free rules peak at 1/46 against a reference of 2/46; before
renumbering one of them was at 21/46.

## What this task does not establish

- **The gold answers are public.** They are derivable from the Mind2Web shard
  by anyone who downloads it. This board measures element selection, not
  secrecy, and the same is true of every benchmark built on a public dataset.
  Runs are reproducible and solution repositories are readable; that, not
  hidden answers, is what makes a row trustworthy.
- **Contamination cuts one way.** These pages are public and may well be in
  training data. Read a strong score accordingly: a system that beats the
  floors is not thereby shown to generalise, while a system that fails them
  has failed on material it may have already seen. We pre-registered that a
  tie is as uninterpretable as a win.
- **It is a click-target benchmark.** 91% of cases are CLICK, 3 are TYPE and 1
  is SELECT. We did not rebalance: TYPE and SELECT were answered correctly
  every time in pre-registration, so importing more of them would pad the set
  with cases that cannot discriminate.
- **46 cases is a probe, not a ranking — and they are not 46 independent
  draws.** They come from **9 episodes across 3 websites** (travelzoo 31, kohls
  8, sports.yahoo 7). The two longest episodes are 20 of the 46 cases; the
  single largest is 22% of the score. Cases inside one episode share a site, a
  goal and largely the same pages, so a solution that understands one site is
  rewarded many times over.

  The grader reports two intervals for that reason: `cases_accuracy_ci_*`
  resamples cases, `cases_accuracy_episode_ci_*` resamples whole episodes.
  **The episode interval is the honest one** — at a score of 0.65 it is about
  23% wider (±15 points rather than ±12). Read that one.

## Timeouts

Pages are large — a median of about 89,000 characters, up to 336,000. Set a
per-case timeout in your solution's `trap.yaml`; the default is 600s, past
which the case is killed and scores 0.0, which reads as a wrong answer rather
than a misconfiguration.

```yaml
timeout: 600
```

The free baseline answers in 0.16s a case, so the budget is entirely yours.
