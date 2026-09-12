"""Per-case judge for svg_clock.

The answer is a drawing, and nobody here decides whether it is a good one.
This judge does two things and nothing else:

  1. Checks the reply is an SVG the board can actually draw. Score 1.0 if
     so, 0.0 with a reason if not.
  2. Hands the drawing on under `drawing`, which the board renders as a
     picture (any metric that is an SVG document does).

"Can actually draw" is stricter than "contains <svg>", because the board
loads the drawing through <img>, and <img> is unforgiving:

  - Without the SVG namespace the browser treats the document as unknown
    XML and shows a broken image. Models often leave `xmlns` off when
    writing inline SVG, so it is added here rather than held against them.
    The same goes for an `xlink:` prefix used without being declared.
  - Past 64 KB the board stops treating the value as a drawing at all.
    That would be a card with no picture and no explanation, so it is
    reported here instead, as an answer that is too big.

The SVG travels under `drawing` and never under `agent_answer`: the board
drops that key on purpose, and the drawing would vanish with it. Nothing
else carries the raw reply, because any string metric becomes a table
column.

I/O contract: reads TRAPTASK_MANIFEST. Identical under `tp run` and the
platform worker -- the worker writes the same manifest and always reports
exit code 0 for an accepted answer.
"""
from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# The board's own limit (apps/web/src/lib/svg-metric.ts, MAX_SVG_BYTES),
# measured the way it measures: JavaScript string length, i.e. UTF-16
# code units.
MAX_DRAWING_UNITS = 64 * 1024

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

_SVG = re.compile(r"<svg\b.*?</svg\s*>", re.DOTALL | re.IGNORECASE)
_OPEN_TAG = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)
_SHAPES = re.compile(
    r"<(circle|ellipse|line|polyline|polygon|rect|path|text)\b", re.IGNORECASE
)


def _utf16_units(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def _declare_namespaces(svg: str) -> str:
    """Add the declarations <img> needs and models tend to omit."""
    m = _OPEN_TAG.search(svg)
    if not m:
        return svg
    tag = m.group(0)
    add = []
    if not re.search(r"\sxmlns\s*=", tag):
        add.append(f'xmlns="{SVG_NS}"')
    if "xlink:" in svg and not re.search(r"\sxmlns:xlink\s*=", tag):
        add.append(f'xmlns:xlink="{XLINK_NS}"')
    if not add:
        return svg
    new_tag = tag[:4] + " " + " ".join(add) + tag[4:]
    return svg[: m.start()] + new_tag + svg[m.end():]


def score_case(stdout: str) -> dict[str, Any]:
    if not stdout.strip():
        return {"score": 0.0, "reason": "the answer is empty"}

    m = _SVG.search(stdout)
    if not m:
        return {"score": 0.0, "reason": "no <svg> element in the answer"}

    svg = _declare_namespaces(m.group(0).strip())

    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        return {"score": 0.0, "reason": f"the SVG is not well-formed XML ({e})"}
    if root.tag != f"{{{SVG_NS}}}svg":
        return {"score": 0.0, "reason": f"the root element is {root.tag!r}, not an SVG"}

    units = _utf16_units(svg)
    if units > MAX_DRAWING_UNITS:
        return {
            "score": 0.0,
            "reason": f"the SVG is {units:,} characters; the board draws up to "
                      f"{MAX_DRAWING_UNITS:,}",
        }

    return {
        "score": 1.0,
        "drawing": svg,
        "shapes": len(_SHAPES.findall(svg)),
        "bytes": len(svg.encode("utf-8")),
    }


def main() -> None:
    m = json.loads(os.environ["TRAPTASK_MANIFEST"])
    stdout = Path(m["run"]["stdout"]).read_text(errors="replace")
    meta = json.loads(Path(m["run"]["meta"]).read_text())
    expected = json.loads((Path(m["expected_dir"]) / "answer.json").read_text())
    base = {"id": expected.get("id"), "category": expected.get("category")}

    if meta.get("exit_code", 0) != 0:
        print(json.dumps({**base, "score": 0.0,
                          "reason": f"solution exited {meta.get('exit_code')}"}))
        return

    print(json.dumps({**base, **score_case(stdout)}))


if __name__ == "__main__":
    main()
