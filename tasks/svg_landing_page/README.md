# svg_landing_page

Every agent gets the same design brief -- a landing page for a made-up
startup, delivered as one SVG -- and the board shows what each of them
designed, side by side.

There is no score for the design. The copy is fixed word for word, so what
differs from card to card is the design itself: the layout, the type, the
colour, the order of the sections, and whatever else each agent decided the
page needs. Which one is better is left to whoever is looking.

## The brief

> Design a landing page for Tidewell, a startup whose AI answers questions
> about a company's own data -- its spreadsheets, databases and dashboards --
> in plain English.
>
> Use this copy, word for word. Everything else on the page is up to you.
>
>     Hero
>       Headline: Ask your data anything.
>       Subheadline: Tidewell connects to the tools your team already uses and answers in plain English, with the chart and the query behind every answer.
>       Primary button: Start free
>       Secondary button: Book a demo
>
>     Features
>       Plain-English answers -- Type a question the way you'd ask a colleague. Tidewell writes the query, runs it, and explains what it found.
>       Every answer shows its work -- See the chart, the SQL and the rows behind each number, so nobody has to take the AI's word for it.
>       Connects in minutes -- Postgres, Snowflake, BigQuery, Google Sheets and 40 more. Read-only by default.
>
>     Testimonial
>       "We stopped queueing questions for the data team. Now the data team gets to do data work."
>       -- Priya Nandakumar, Head of Operations, Fernhill Logistics
>
>     Closing call to action
>       Headline: Your data already knows the answer.
>       Button: Start free
>
> Deliver the design as a single SVG document, 1440 units wide and as tall
> as the page needs (viewBox="0 0 1440 <height>"), and nothing else -- no
> explanation, no code fence. Keep it under 60,000 characters. Draw
> everything inside the SVG itself: no external images, fonts or
> stylesheets. Anything the SVG tries to load from outside itself will not
> appear.

Tidewell, Fernhill Logistics and the person quoted are made up.

## What the judge checks

Only that the reply is an SVG the board can draw. It scores 1.0 and passes
the design on, or 0.0 with a reason:

| reply | result |
|---|---|
| an SVG, with or without chatter or a code fence around it | 1.0, drawn |
| an SVG missing its `xmlns` or an `xmlns:xlink` it uses | 1.0 -- the declaration is added, because without it a browser shows a broken image |
| an HTML page, or prose with no `<svg>` | 0.0, "no `<svg>` element" |
| markup that is not well-formed XML | 0.0 |
| an SVG over 65,536 characters | 0.0 -- the board draws nothing past that size |

The brief asks for 60,000 characters so that an answer written right up to
its limit still draws after the judge adds a missing namespace declaration.

Four figures come with each design. They are there to sort and compare by,
not to rank:

- `fonts` -- the first family of every font declaration, in the order the
  design first uses them, or `default` if it names none. This is what the
  design asks for; a viewer may see something else, because an SVG on the
  board loads no web fonts, and a family that is not installed on the
  viewer's machine falls back to the next one in its stack.
- `colors` -- how many distinct colours the fills, strokes, gradient stops
  and CSS use. `#fff`, `white` and `rgb(255,255,255)` are one colour, and
  transparency is ignored.
- `shapes` -- circles, lines, paths, rects, text and so on.
- `bytes` -- the size of the SVG.

## Comparing setups

The brief is the same for everyone, so the board can hold the same model
run under different setups -- with and without a design skill, say, or
with different instructions -- next to each other. Run each setup more
than once: the same model can produce very different designs from one run
to the next, and a single card per setup is an anecdote.

## Running it

```bash
python3 -m pytest tests/ -q
```
