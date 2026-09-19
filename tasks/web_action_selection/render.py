"""Render one case into what the solution is served.

Two things happen here that the raw Mind2Web snapshot does not do for us.

**The ids are renumbered.** Mind2Web assigns `backend_node_id` in a way that
puts the target element at or near the minimum id on the page -- so
`min(id for clickable elements)` is the gold answer on 45.7% of cases, with no
language understanding at all. That is roughly published SOTA for this dataset.
Renumbering to a shuffled range destroys the ordinal information while leaving
the document byte-identical otherwise, and takes every trivial baseline to 0.0%
(see `leak_report()` and tests/test_build.py).

**Document order is left alone.** It carries real meaning for a solver and
leaks nothing: every position-in-DOM heuristic already scores 0/46.
"""
from __future__ import annotations

import json
import random
import re

import elements

ID_RE = re.compile(r'backend_node_id="(\d+)"')
EL_RE = re.compile(r'<(\w+)[^>]*backend_node_id="(\d+)"')
CLICKABLE = ("a", "button", "input", "select", "textarea", "option", "label")
ID_BASE = 1000

TASK_MD = """# Pick the next element to act on

You are driving a web page toward a goal. You are given the goal, the actions
already completed, and the page's full HTML in `page.html`.

Every element you may act on carries a `backend_node_id` attribute. Name the
one element the next action should target.

`page.html` is large — a median of about 730 actionable elements, up to 2,159.
There is no shortlist: narrowing the page down is part of the task.

Print these three lines. Anything else you write is ignored, and only the LAST
occurrence of each line is read:

    ELEMENT: <backend_node_id>
    OP: <CLICK | TYPE | SELECT>
    VALUE: <the text to type or option to select, or leave empty for CLICK>

Scoring is on `ELEMENT` first: naming the right element is the task. `OP` and
`VALUE` are scored beside it and a case counts as a full step success only when
all three are right. One element is scored -- the last `ELEMENT:` line -- so
listing several candidates does not help.
"""


def renumber(page_html: str, seed: str) -> tuple[str, dict[str, str]]:
    """Bijectively remap every backend_node_id to a shuffled range.

    Returns the rewritten page and the old->new mapping. Deterministic in
    `seed` (the case id), so the public half can render a page and the private
    half can map the answer into it without either knowing the other's data.
    """
    seen: list[str] = []
    for m in ID_RE.finditer(page_html):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    new = list(range(ID_BASE, ID_BASE + len(seen)))
    random.Random(seed).shuffle(new)
    mapping = {old: str(n) for old, n in zip(seen, new)}
    return ID_RE.sub(lambda m: 'backend_node_id="%s"' % mapping[m.group(1)], page_html), mapping


NON_ACTIONABLE = elements.NON_ACTIONABLE


def id_elements(page_html: str) -> list[tuple[str, str]]:
    """(tag, id) for every actionable element, document order, deduped."""
    out, seen = [], set()
    for m in EL_RE.finditer(page_html):
        if m.group(2) not in seen and m.group(1) not in NON_ACTIONABLE:
            seen.add(m.group(2))
            out.append((m.group(1), m.group(2)))
    return out


# Every trivial rule we could think of that needs no language understanding.
# Each must score 0 for the task to be measuring element selection at all.
TRIVIAL_BASELINES = {
    "lowest_id": lambda e: min(e, key=lambda t: int(t[1]))[1] if e else None,
    "highest_id": lambda e: max(e, key=lambda t: int(t[1]))[1] if e else None,
    "lowest_id_clickable": lambda e: (min([x for x in e if x[0] in CLICKABLE], key=lambda t: int(t[1]))[1]
                                      if any(x[0] in CLICKABLE for x in e) else None),
    "highest_id_clickable": lambda e: (max([x for x in e if x[0] in CLICKABLE], key=lambda t: int(t[1]))[1]
                                       if any(x[0] in CLICKABLE for x in e) else None),
    "first_in_dom": lambda e: e[0][1] if e else None,
    "last_in_dom": lambda e: e[-1][1] if e else None,
    "middle_of_dom": lambda e: e[len(e) // 2][1] if e else None,
    "first_clickable": lambda e: next((i for t, i in e if t in CLICKABLE), None),
    "first_anchor": lambda e: next((i for t, i in e if t == "a"), None),
    "first_button": lambda e: next((i for t, i in e if t == "button"), None),
    "first_input": lambda e: next((i for t, i in e if t == "input"), None),
}


def _words(s: str) -> set:
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def lexical_pick(page_html: str, goal: str) -> str | None:
    """The weakest rule that actually READS the page: highest word overlap
    between the goal and an element's rendered identity. It is the reference
    the language-free rules are held below."""
    target = _words(goal)
    best, pick = -1.0, None
    for bid, e in elements.parse(page_html).items():
        w = _words(elements.describe(*e))
        if not w:
            continue
        score = len(w & target) / len(w | target)
        if score > best:
            best, pick = score, bid
    return pick


def leak_report(rendered: list[tuple[str, list[str], str]]) -> dict[str, int]:
    """How many cases each baseline gets right.

    `rendered` is (page_html, accepted_elements, goal). Keys other than
    `lexical_overlap` use no language at all and must not beat it -- see
    `assert_no_trivial_baseline` for why the gate is phrased that way rather
    than as "must be zero".
    """
    out = {}
    for name, pick in TRIVIAL_BASELINES.items():
        hits = 0
        for page_html, accepted, _goal in rendered:
            try:
                hits += pick(id_elements(page_html)) in set(accepted)
            except Exception:
                pass
        out[name] = hits
    out["lexical_overlap"] = sum(lexical_pick(p, g) in set(a) for p, a, g in rendered)
    return out


def render_inputs(case_id: str, task: dict, action: dict) -> tuple[dict[str, str], dict[str, str]]:
    """What the solution is served, plus the id mapping used to produce it.

    Needs nothing about which element is correct -- the public half runs this.
    """
    page, mapping = renumber(action["cleaned_html"], case_id)
    idx = next(i for i, a in enumerate(task["actions"]) if a["action_uid"] == action["action_uid"])
    prior = list(task["action_reprs"][:idx])
    goal = task["confirmed_task"]
    n_steps = len(task["action_reprs"])
    prior_md = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(prior)) or "(none -- this is the first step)"
    inputs = {
        "task.md": TASK_MD,
        "step.md": (f"## Goal\n\n{goal}\n\n## Actions already completed\n\n{prior_md}\n\n"
                    f"## This step\n\nStep {idx + 1} of {n_steps}. The page is in `page.html`.\n"),
        "step.json": json.dumps({"goal": goal, "prior_actions": prior, "step": idx + 1,
                                 "n_steps": n_steps, "page": "page.html"}, indent=2, ensure_ascii=False) + "\n",
        "page.html": page,
    }
    return inputs, mapping


def render(case: dict, task: dict, action: dict) -> tuple[dict[str, str], dict]:
    """(files the solution is served, the answer the judge is served).

    Re-derives the equivalence set and the gold element's rendered identity
    from the shard, so a shard that has moved under us fails the build instead
    of silently changing the task.
    """
    gold_id = case.get("gold_element") or case["accepted_elements"][0]
    accepted_raw = elements.equivalent_to(action["cleaned_html"], gold_id)
    if accepted_raw != sorted(case["accepted_elements"], key=int):
        raise ValueError(f"{case['id']}: equivalence set no longer reproduces from the shard "
                         f"({accepted_raw} vs {case['accepted_elements']})")
    desc = elements.describe(*elements.parse(action["cleaned_html"])[gold_id])
    if desc != case["gold_description"]:
        raise ValueError(f"{case['id']}: gold renders as {desc!r}, not {case['gold_description']!r}")

    inputs, mapping = render_inputs(case["id"], task, action)
    step = json.loads(inputs["step.json"])
    answer = {
        "id": case["id"],
        "accepted_elements": [mapping[a] for a in accepted_raw],
        "op": action["operation"]["op"].upper(),
        "value": action["operation"].get("value", "") or "",
        # The board's by_category breakdown is the only one that survives the
        # platform's key filter, so it has to carry the informative label. On
        # this case set `domain` is a one-to-one relabelling of `website`
        # (travelzoo->Travel, kohls->Shopping, sports.yahoo->Entertainment), and
        # showing three domains reads as more breadth than three sites.
        "category": task["website"],
        "domain": task["domain"],
        "website": task["website"],
        "n_elements": case["n_elements"],
        "step": step["step"],
        "n_steps": step["n_steps"],
        "is_last_step": step["step"] == step["n_steps"],
        "action_uid": case["action_uid"],
        "episode": case["annotation_id"],
        "gold_element": mapping[gold_id],
        "gold_description": case["gold_description"],
    }
    return inputs, answer
