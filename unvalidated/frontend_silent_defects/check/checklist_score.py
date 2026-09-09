"""Score one page against its brief's checklist — pointwise, binary, no opponent.

    ANTHROPIC_API_KEY=... python3 check/checklist_score.py case_08 08B [--repeat 3]

Why this shape
--------------
A leaderboard row is one submission, and a pairwise judge ("A or B") has no
opponent to compare it against. So the thing that produces the number has to be
pointwise. WebDevJudge measures single-answer grading at 60.86% against 66.06%
for pairwise — worse, but not unusable — and names the reason it is usually far
worse than that: people ask for a 1-10 rating. In the same paper, **binary
rubrics substantially outperform multi-point Likert scales** in single-answer
grading, because "verifiable evaluation protocols yield more reliable judgments
when there is a lack of relative information".

So: no rating. Ten items from `check/checklists/<case>.json`, each answered yes
or no, and the score is how many were satisfied. That is also ArtifactsBench's
shape — checklist scoring summed into one number — and it reaches 90.95%
agreement with front-end engineers. Note what they do with pairwise: they use it
to *validate*, not to score. `check/pairwise_gate.py` is our version of that.

Two rules that keep this honest
-------------------------------
**Evidence before verdict.** Each item is answered as {n, evidence, verdict} and
a JSON schema is filled in order, so the observation is written while the
verdict does not yet exist to be justified.

**We decide what is unanswerable, not the judge.** There is no "unclear" option:
given one, a judge can mark everything unanswerable and score nothing. Instead,
when a page has no source, the five code items are removed before the model sees
them and the score is out of five. The denominator is always reported.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import statistics
from pathlib import Path

import anthropic

TASK = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("TRAP_PANEL_MODEL", "claude-sonnet-5")

STANCE = (
    "You are an experienced product designer checking a page against a list of "
    "requirements written for this brief. You are not rating it and not ranking "
    "it against anything — for each item you are answering one question: is this "
    "true of the page in front of you, yes or no. You do not know who or what "
    "produced it, and speculating about that is out of scope."
)

ASK = """For each item on the list, answer yes or no.

**Yes means the page does this.** Not "mostly", not "an effort was made" — if
you would have to argue for it, the answer is no. Most pages will not get every
item, and that is the expected result rather than a sign you are being harsh.

**Do not reward size.** More sections, more copy, more reassurance, more proof
is not evidence for any item on this list. An item is satisfied by the page
doing the thing the item names, and by nothing else.

For each item, in order, give:

  `n`         the item's number
  `evidence`  what you actually see that settles it — a specific element,
              value, or line, not a restatement of the item. Write this first.
  `verdict`   yes or no

One entry per item, in order, no more and no fewer."""

SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer"},
                    # Written before `verdict` on purpose: a schema is filled in
                    # order, so the observation cannot be shaped to fit a verdict
                    # that does not exist yet.
                    "evidence": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["yes", "no"]},
                },
                "required": ["n", "evidence", "verdict"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["items"],
    "additionalProperties": False,
}


def load_checklist(case: str, has_source: bool) -> tuple[list[str], str]:
    """Items to ask, and which half of the list they are."""
    cl = json.loads((TASK / "check" / "checklists" / f"{case}.json").read_text())
    if has_source:
        return cl["vision"] + cl["code"], "vision+code"
    return cl["vision"], "vision only (no source available)"


def page_blocks(pages: Path, page_id: str) -> tuple[list[dict], bool]:
    blocks: list[dict] = []
    shots = sorted(p for ext in ("jpg", "jpeg", "png")
                   for p in list(pages.glob(f"{page_id}.{ext}")) + list(pages.glob(f"{page_id}_*.{ext}")))
    for i, sh in enumerate(shots):
        media = "image/jpeg" if sh.suffix in (".jpg", ".jpeg") else "image/png"
        blocks.append({"type": "image", "source": {
            "type": "base64", "media_type": media,
            "data": base64.standard_b64encode(sh.read_bytes()).decode()}})
        blocks.append({"type": "text", "text":
                       f"(the page as rendered{'' if len(shots) == 1 else f', view {i+1} of {len(shots)}'})"})
    src = pages / f"{page_id}.html"
    if src.exists():
        blocks.append({"type": "text", "text": f"The source:\n\n{src.read_text()[:120_000]}"})
    return blocks, src.exists()


def score_page(client: anthropic.Anthropic, case: str, page_id: str, pages: Path) -> dict:
    brief = (TASK / "inputs" / case / "brief.md").read_text()
    shots, has_source = page_blocks(pages, page_id)
    items, which = load_checklist(case, has_source)
    numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(items))

    resp = client.messages.create(
        model=MODEL, max_tokens=8000, system=STANCE,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA},
                       "effort": os.environ.get("TRAP_PANEL_EFFORT", "medium")},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": f"The brief this was built from:\n\n{brief}"},
            *shots,
            {"type": "text", "text": f"The list, for this brief:\n\n{numbered}"},
            {"type": "text", "text": ASK},
        ]}],
    )
    got = json.loads(next((b.text for b in resp.content if b.type == "text"), ""))["items"]
    by_n = {e["n"]: e for e in got}
    # A missing or extra entry is a malformed answer, not a failed item: say so
    # rather than quietly scoring the page down for the judge's mistake.
    missing = [i + 1 for i in range(len(items)) if i + 1 not in by_n]
    verdicts = [by_n[i + 1]["verdict"] == "yes" for i in range(len(items)) if i + 1 in by_n]
    return {
        "case": case, "page": page_id, "checklist": which,
        "n_items": len(items), "n_answered": len(verdicts),
        "malformed_items": missing,
        "satisfied": sum(verdicts),
        "score": round(sum(verdicts) / len(items), 3) if not missing else None,
        "items": [by_n.get(i + 1, {"n": i + 1, "verdict": "MISSING"}) for i in range(len(items))],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("page")
    ap.add_argument("--pages", default="labels/pages")
    ap.add_argument("--repeat", type=int, default=1,
                    help="score the same page N times and report how many items flip")
    a = ap.parse_args()
    pages = TASK / a.pages if not Path(a.pages).is_absolute() else Path(a.pages)

    client = anthropic.Anthropic(max_retries=5)
    runs = [score_page(client, a.case, a.page, pages) for _ in range(a.repeat)]

    r0 = runs[0]
    print(f"  {a.case} / {a.page}   checklist: {r0['checklist']}")
    for e in r0["items"]:
        mark = {"yes": "OK  ", "no": "no  ", "MISSING": "??  "}[e["verdict"]]
        print(f"   {e['n']:2d} {mark}{e.get('evidence', '')[:110]}")
    print(f"\n  score {r0['satisfied']}/{r0['n_items']} = {r0['score']}")
    if r0["malformed_items"]:
        print(f"  ** the judge skipped items {r0['malformed_items']} — answer is malformed **")

    if a.repeat > 1:
        # The number that decides whether this can go on a board: a column whose
        # value moves between identical runs is not a measurement.
        flips = [sum(1 for r in runs if r["items"][i]["verdict"] == "yes")
                 for i in range(r0["n_items"])]
        unstable = [i + 1 for i, k in enumerate(flips) if 0 < k < a.repeat]
        scores = [r["score"] for r in runs if r["score"] is not None]
        print(f"\n  over {a.repeat} runs: scores {scores}")
        print(f"  items that did not agree with themselves: {unstable or 'none'}")
        if len(scores) > 1:
            print(f"  spread {max(scores) - min(scores):.3f}, sd {statistics.pstdev(scores):.3f}")

    out = TASK / "labels" / f"checklist_{a.case}_{a.page}.json"
    out.write_text(json.dumps({"model": MODEL, "runs": runs}, indent=2) + "\n")
    print(f"  -> {out.relative_to(TASK)}")


if __name__ == "__main__":
    main()
