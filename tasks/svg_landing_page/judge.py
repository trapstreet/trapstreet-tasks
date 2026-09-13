"""Per-case judge for svg_landing_page.

The answer is a design, and nobody here decides whether it is a good one.
This judge does three things and nothing else:

  1. Checks the reply is an SVG the board can actually draw. Score 1.0 if
     so, 0.0 with a reason if not.
  2. Hands the design on under `drawing`, which the board renders as a
     picture (any metric that is an SVG document does).
  3. Describes it: how many shapes, how many bytes, how many distinct
     colours, and which typefaces it asks for. These are there to sort
     and compare by, not to rank.

"Can actually draw" is stricter than "contains <svg>", because the board
loads the drawing through <img>, and <img> is unforgiving:

  - Without the SVG namespace the browser treats the document as unknown
    XML and shows a broken image. Models often leave `xmlns` off when
    writing inline SVG, so it is added here rather than held against them.
    The same goes for an `xlink:` prefix used without being declared.
  - Past 64 KB the board stops treating the value as a drawing at all.
    That would be a card with no picture and no explanation, so it is
    reported here instead, as an answer that is too big.

`fonts` lists the first family of every font declaration, in the order the
document first uses them -- what the designer asked for. What a viewer sees
may differ: <img> loads no web fonts, so a family that is not installed on
the viewer's machine falls back to the next one in the stack.

The SVG travels under `drawing` and never under `agent_answer`: the board
drops that key on purpose, and the drawing would vanish with it. Nothing
else carries the raw reply, because any string metric becomes a table
column.

I/O contract: reads TRAPTASK_MANIFEST. Identical under `tp run` and the
platform worker -- the worker writes the same manifest and always reports
exit code 0 for an accepted answer.
"""
from __future__ import annotations

import colorsys
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

# Properties whose value is a colour, as attributes or as CSS.
_COLOUR_PROPS = {"fill", "stroke", "stop-color", "color", "flood-color", "lighting-color"}
_NOT_A_COLOUR = {"none", "transparent", "currentcolor", "inherit", "initial", "unset", ""}
# Enough names to fold the common ones into their hex; any other name
# counts as itself.
_NAMED = {
    "black": "#000000", "white": "#ffffff", "gray": "#808080", "grey": "#808080",
    "silver": "#c0c0c0", "red": "#ff0000", "maroon": "#800000", "orange": "#ffa500",
    "yellow": "#ffff00", "olive": "#808000", "lime": "#00ff00", "green": "#008000",
    "aqua": "#00ffff", "cyan": "#00ffff", "teal": "#008080", "blue": "#0000ff",
    "navy": "#000080", "fuchsia": "#ff00ff", "magenta": "#ff00ff", "purple": "#800080",
}
_DECL = re.compile(r"([A-Za-z-]+)\s*:\s*([^;{}]+)")
# The size in a `font:` shorthand always carries a unit; a bare number is
# a weight.
_FONT_SIZE = re.compile(r"^[\d.]+(?:px|pt|pc|em|rem|ex|ch|%|vw|vh|vmin|vmax)(?:/\S+)?$", re.I)


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


def _colour(value: str) -> str | None:
    """A colour value as lowercase #rrggbb, or None if it is not one.

    Alpha is dropped: a translucent white is still white in a palette."""
    v = value.replace("!important", "").strip().lower()
    if v in _NOT_A_COLOUR or v.startswith("url("):
        return None
    m = re.fullmatch(r"#([0-9a-f]+)", v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            return "#" + "".join(c * 2 for c in h[:3])
        if len(h) in (6, 8):
            return "#" + h[:6]
        return None
    m = re.fullmatch(r"(rgba?|hsla?)\(([^)]*)\)", v)
    if m:
        parts = [p for p in re.split(r"[\s,/]+", m.group(2).strip()) if p]
        if len(parts) < 3:
            return None
        try:
            if m.group(1).startswith("rgb"):
                rgb = [float(p[:-1]) * 2.55 if p.endswith("%") else float(p) for p in parts[:3]]
            else:
                h = float(parts[0].removesuffix("deg")) / 360
                s, light = (float(p.removesuffix("%")) / 100 for p in parts[1:3])
                rgb = [x * 255 for x in colorsys.hls_to_rgb(h % 1.0, light, s)]
        except ValueError:
            return None
        return "#%02x%02x%02x" % tuple(max(0, min(255, round(x))) for x in rgb)
    if re.fullmatch(r"[a-z]+", v):
        return _NAMED.get(v, v)
    return None


def _first_family(stack: str) -> str | None:
    first = stack.split(",")[0].strip().strip("'\"").strip()
    return first or None


def _family_in_shorthand(value: str) -> str | None:
    tokens = re.findall(r'"[^"]*"|\'[^\']*\'|[^\s]+', value)
    for i, tok in enumerate(tokens):
        if _FONT_SIZE.match(tok):
            return _first_family(" ".join(tokens[i + 1:]))
    return None


def _describe(root: ET.Element) -> tuple[int, str]:
    """Distinct colours, and the typefaces asked for in first-use order."""
    colours: set[str] = set()
    fonts: list[str] = []

    def take(prop: str, value: str) -> None:
        prop = prop.strip().lower()
        if prop in _COLOUR_PROPS:
            c = _colour(value)
            if c:
                colours.add(c)
        elif prop in ("font-family", "font"):
            family = _first_family(value) if prop == "font-family" else _family_in_shorthand(value)
            if family and family not in fonts:
                fonts.append(family)

    for el in root.iter():
        if el.tag == f"{{{SVG_NS}}}style" and el.text:
            for prop, value in _DECL.findall(el.text):
                take(prop, value)
        for name, value in el.attrib.items():
            name = name.rsplit("}", 1)[-1]
            if name == "style":
                for prop, v in _DECL.findall(value):
                    take(prop, v)
            else:
                take(name, value)

    return len(colours), ", ".join(fonts) if fonts else "default"


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

    colours, fonts = _describe(root)
    return {
        "score": 1.0,
        "drawing": svg,
        "fonts": fonts,
        "colors": colours,
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
