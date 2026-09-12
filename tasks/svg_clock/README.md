# svg_clock

Every model gets the same one-line request — draw an analog clock showing
3:47, as SVG — and the board shows what each of them drew, side by side.

There is no score for the drawing. Whether a clock is right is something
you can see: at 3:47 the minute hand points just past the 9, and the hour
hand has travelled most of the way from 3 to 4. An hour hand parked on the
3, hands of the wrong length, a face with thirteen numerals — all of it is
on the card, and deciding what counts is left to whoever is looking.

## The question

> Draw an analog clock face showing 3:47.
>
> Reply with a single SVG document and nothing else — no explanation, no
> code fence. Draw everything inside the SVG itself: no external images or
> fonts.

## What the judge checks

Only that the reply is an SVG the board can draw. It scores 1.0 and passes
the drawing on, or 0.0 with a reason:

| reply | result |
|---|---|
| an SVG, with or without chatter or a code fence around it | 1.0, drawn |
| an SVG missing its `xmlns` or an `xmlns:xlink` it uses | 1.0 — the declaration is added, because without it a browser shows a broken image |
| prose with no `<svg>` | 0.0, "no `<svg>` element" |
| markup that is not well-formed XML | 0.0 |
| an SVG over 65,536 characters | 0.0 — the board draws nothing past that size |

Two figures come with each drawing: `shapes` (circles, lines, paths, text
and so on) and `bytes`. They are there to sort by, not to rank.

## Running it

```bash
python3 -m pytest tests/ -q
```
