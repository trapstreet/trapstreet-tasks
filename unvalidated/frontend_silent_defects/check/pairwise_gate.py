"""Does a pairwise judge reproduce the owner's comparisons?

    ANTHROPIC_API_KEY=... python3 check/pairwise_gate.py labels/pairs_<set>.json

Design, and where each decision comes from — the reasoning is in
docs/frontend-judges-how-they-are-built.md.

**Pairwise, not pointwise.** WebDevJudge (ICLR 2026) measures pairwise beating
single-answer grading by over 8 points across models on exactly this task; a
2026 position-bias study finds pointwise judges favour the first position 60-70%
of the time on identical inputs, while pairwise sits near 50-50.

**Code as well as screenshots.** The same paper ablated the inputs and removing
the code hurt more than removing the screenshots. A set without source can still
be run, and is scored, but it is testing the judge with its weaker half.

**Every state, not one frame.** ArtifactsBench captures before/during/after a
scripted interaction and its ablation shows multiple screenshots materially
improve agreement with human experts. Whatever `check/inspect.mjs`'s walker
captured is sent, in order.

**A per-brief checklist, not one global rubric.** WebDevJudge found a fixed
rubric tree gives only marginal benefit over no guidance in pairwise settings —
"evaluation capability is an internalized skill". ArtifactsBench reaches 90.95%
agreement with front-end engineers using a checklist *generated per task*. Those
are not in conflict: a rubric that says the same thing about every brief adds
little, and one derived from this brief's own requirements is where the number
comes from. `check/checklists/<case>.json` holds ten items per brief, five
vision-oriented and five code-oriented, written from the brief.

**The bar is set against the field, not against chance.** Humans agree with each
other 84.82% of the time here; the best published LLM pairwise judge reaches
66.06%, and the field plateaus below the mid-70s. An earlier version of this
file used nine pairs and a bar of >=8/9, which is 89% — a judge performing at
the state of the art would have failed it 87% of the time. `bar()` now reports
what a set of this size can and cannot resolve, and refuses to pretend a small
set has settled anything.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from math import comb
from pathlib import Path

import anthropic

TASK = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("TRAP_PANEL_MODEL", "claude-sonnet-5")

HUMAN_CEILING = 0.8482      # WebDevJudge, human expert pairwise agreement
PUBLISHED_BEST = 0.6606     # WebDevJudge, best LLM pairwise (Claude-4-Sonnet)

STANCE = (
    "You are an experienced product designer running a critique. You are looking "
    "at two attempts at the same brief and deciding which is the better piece of "
    "work. You do not know who or what produced either, and speculating about "
    "that is out of scope."
)

ASK = """Same brief, two attempts. One is better work. Say which.

You have been given a checklist written from THIS brief — ten things that
matter for this page and not for pages in general. Work through it.

**Do not count features.** A page that does one thing well is better work than
one that does five adequately. If your reason for preferring an attempt is that
it contains more — more sections, more copy, more reassurance, more proof —
discard that reason. More is not better, and a longer page is not a more
considered one. The checklist tally does not decide the choice either; it is
there to keep you looking at this brief's requirements rather than at your
general impression.

Work in this order and do not skip a step:

  1. `standard` — for THIS brief, what would good look like? One sentence,
     written before you have chosen, and about the brief rather than about
     either attempt.
  2. `items` — for each checklist item in order, which attempt does it better:
     "first", "second", or "same". Ten entries, no more, no fewer.
  3. `gap` — the single largest way one of the two falls short of the standard.
     Name which attempt, and which checklist item it belongs to.
  4. `choice` — first or second. No ties; if it is close, choose anyway.
  5. `why` — one sentence."""

SCHEMA = {
    "type": "object",
    "properties": {
        # Field order is the mechanism, not decoration: a JSON schema is filled in
        # order, so the standard and the item-by-item reading are written while
        # `choice` does not yet exist to be rationalised. Moving `choice` up would
        # undo most of this.
        "standard": {"type": "string", "description": "What good would look like for this brief. One sentence, about the brief, not about either attempt."},
        "items": {
            "type": "array",
            "description": "One entry per checklist item, in order.",
            "items": {"type": "string", "enum": ["first", "second", "same"]},
        },
        "gap": {"type": "string", "description": "The largest shortfall against that standard. Name the attempt and the checklist item."},
        "choice": {"type": "string", "enum": ["first", "second"]},
        "why": {"type": "string", "description": "One sentence."},
    },
    "required": ["standard", "items", "gap", "choice", "why"],
    "additionalProperties": False,
}


def p_ge(k: int, n: int, p: float = 0.5) -> float:
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def bar(n: int) -> tuple[int, float]:
    """The score needed to beat chance at p<0.05, and the chance a judge at the
    published state of the art would reach it. When that second number is low,
    the set is too small to conclude anything from a miss."""
    k = next(k for k in range(n + 1) if p_ge(k, n) < 0.05)
    return k, p_ge(k, n, PUBLISHED_BEST)


def _b64(p: Path) -> str:
    return base64.standard_b64encode(p.read_bytes()).decode()


def page_blocks(pages: Path, page_id: str, label: str) -> list[dict]:
    """Everything we hold about one attempt: every captured state, then source."""
    blocks: list[dict] = [{"type": "text", "text": f"{label}:"}]
    shots = sorted(list(pages.glob(f"{page_id}.jpg")) + list(pages.glob(f"{page_id}_*.jpg"))
                   + list(pages.glob(f"{page_id}.png")) + list(pages.glob(f"{page_id}_*.png")))
    for i, sh in enumerate(shots):
        media = "image/jpeg" if sh.suffix in (".jpg", ".jpeg") else "image/png"
        blocks.append({"type": "image", "source": {"type": "base64", "media_type": media, "data": _b64(sh)}})
        if len(shots) > 1:
            blocks.append({"type": "text", "text": f"({label}, view {i + 1} of {len(shots)})"})
    src = pages / f"{page_id}.html"
    if src.exists():
        blocks.append({"type": "text", "text": f"{label}, source:\n\n{src.read_text()[:120_000]}"})
    return blocks


def ask(client: anthropic.Anthropic, brief: str, checklist: dict,
        pages: Path, first: str, second: str) -> dict:
    numbered = "\n".join(
        f"{i + 1}. {t}" for i, t in enumerate(checklist["vision"] + checklist["code"]))
    content = [
        {"type": "text", "text": f"The brief both were built from:\n\n{brief}"},
        {"type": "text", "text": f"A checklist for this brief — items 1-5 are about what you can see, 6-10 about the implementation:\n\n{numbered}"},
        *page_blocks(pages, first, "The first attempt"),
        *page_blocks(pages, second, "The second attempt"),
        {"type": "text", "text": ASK},
    ]
    resp = client.messages.create(
        model=MODEL, max_tokens=6000, system=STANCE,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA},
                       "effort": os.environ.get("TRAP_PANEL_EFFORT", "medium")},
        messages=[{"role": "user", "content": content}],
    )
    return json.loads(next((b.text for b in resp.content if b.type == "text"), ""))


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__.strip().splitlines()[2].strip())
    manifest = json.loads(Path(sys.argv[1]).read_text())
    pages = TASK / manifest["pages_dir"] if not Path(manifest["pages_dir"]).is_absolute() \
        else Path(manifest["pages_dir"])
    pairs = manifest["pairs"]
    n = len(pairs)
    need, power = bar(n)

    print(f"  set {manifest['name']}: {n} pairs, source {'included' if manifest.get('has_source') else 'MISSING'}")
    print(f"  bar to beat chance: >={need}/{n}. A judge at the published best "
          f"({PUBLISHED_BEST:.0%}) clears that {power:.0%} of the time.")
    if power < 0.5:
        print(f"  ** this set is underpowered: a miss will not mean the judge is bad **")
    print()

    client = anthropic.Anthropic(max_retries=5)
    rows, by_brief = [], {}
    for pair in pairs:
        b = pair["brief"]
        brief_text = (TASK / "inputs" / f"case_{b}" / "brief.md").read_text()
        checklist = json.loads((TASK / "check" / "checklists" / f"case_{b}.json").read_text())
        r = ask(client, brief_text, checklist, pages, pair["first"], pair["second"])
        chose = pair["first"] if r["choice"] == "first" else pair["second"]
        hers = pair.get("hers")
        ok = None if hers is None else chose == hers
        if ok is not None:
            by_brief.setdefault(b, []).append(ok)
        rows.append({**pair, "judge": chose, "ok": ok, **r})
        mark = "" if ok is None else ("  ok" if ok else "  MISS")
        print(f"  {pair['first']} vs {pair['second']}   hers={hers}  judge={chose}{mark}")
        print(f"      {r['gap'][:150]}")

    scored = [r for r in rows if r["ok"] is not None]
    if scored:
        k = sum(r["ok"] for r in scored)
        print(f"\n  {k}/{len(scored)} = {k/len(scored):.0%}   "
              f"(chance 50%, published best {PUBLISHED_BEST:.0%}, humans {HUMAN_CEILING:.0%})")
        for brief, oks in sorted(by_brief.items()):
            print(f"    case_{brief}: {sum(oks)}/{len(oks)}")
        print(f"  p(>= this | judge is guessing) = {p_ge(k, len(scored)):.3f}")
    picked_first = sum(1 for r in rows if r["judge"] == r["first"])
    print(f"  picked the first-shown attempt {picked_first}/{n}")

    out = TASK / "labels" / f"gate_{manifest['name']}.json"
    out.write_text(json.dumps({"model": MODEL, "set": manifest["name"],
                               "n": n, "rows": rows}, indent=2) + "\n")
    print(f"  -> {out.relative_to(TASK)}")


if __name__ == "__main__":
    main()
