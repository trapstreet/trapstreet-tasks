"""Element extraction: the rendered identity of everything on a page.

Shared by case building (which computes the equivalence sets) and rendering
(which re-derives them to catch a shard that has moved under us).
"""
from __future__ import annotations

from html.parser import HTMLParser

ATTRS = ("aria_label", "title", "alt", "value", "placeholder", "type")

# Mind2Web wraps bare text nodes in a <text> pseudo-element. They carry a
# backend_node_id but are not things you can act on, and no gold is ever one
# (across the set: a, button, input, li, img, select, div, h3). Excluding them
# is what makes "how many elements are on this page" mean one thing in the
# published median, the grader's page-size split and the leak battery.
NON_ACTIONABLE = ("text",)


class Elements(HTMLParser):
    """Every element carrying a backend_node_id, with its own text."""

    def __init__(self) -> None:
        super().__init__()
        self.stack: list = []
        self.found: dict[str, tuple] = {}

    def handle_starttag(self, tag, attrs):
        self.stack.append((tag, dict(attrs), []))

    def handle_endtag(self, tag):
        while self.stack:
            t, a, buf = self.stack.pop()
            bid = a.get("backend_node_id")
            if bid and bid not in self.found:
                self.found[bid] = (t, a, " ".join(buf).strip())
            if self.stack:
                self.stack[-1][2].extend(buf)
            if t == tag:
                break

    def handle_data(self, data):
        data = data.strip()
        if data and self.stack:
            self.stack[-1][2].append(data)


def describe(tag: str, attrs: dict, text: str) -> str:
    """The rendered identity of an element: what a person would see and act on."""
    parts = [f"<{tag}>"]
    parts += [f'{k}="{attrs[k][:60]}"' for k in ATTRS if attrs.get(k)]
    if text:
        parts.append(f'"{text[:100]}"')
    return " ".join(parts)


def parse(page_html: str) -> dict[str, tuple]:
    """backend_node_id -> (tag, attrs, own text) for every actionable element."""
    p = Elements()
    p.feed(page_html)
    while p.stack:
        t, a, buf = p.stack.pop()
        bid = a.get("backend_node_id")
        if bid and bid not in p.found:
            p.found[bid] = (t, a, " ".join(buf).strip())
    return {k: v for k, v in p.found.items() if v[0] not in NON_ACTIONABLE}


def equivalent_to(page_html: str, gold_id: str) -> list[str]:
    """Every element whose rendered identity is indistinguishable from gold's.

    About a quarter of these pages carry a second element with the same tag,
    same accessible name and same text -- a link duplicated between the top nav
    and a sticky header, say. A solution naming the twin made the right
    decision and the page cannot tell them apart, so it must be accepted.
    """
    found = parse(page_html)
    if gold_id not in found:
        return []
    target = describe(*found[gold_id])
    return sorted((bid for bid, e in found.items() if describe(*e) == target), key=int)
