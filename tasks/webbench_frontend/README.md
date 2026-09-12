# webbench_frontend

Three small web apps, each built in ten steps from a starter project, and checked in a real
browser. Built from [Web-Bench](https://github.com/bytedance/web-bench)'s projects and specs.

## What a case is

Each case is one Web-Bench project's first ten steps, given together and done in order --
each step builds on the ones before it. The question carries the starter project
(`package.json`, configs, `src/`) and the ten step descriptions; the answer is the finished
`src/` as one JSON object of files.

| case | project | stack | steps (easy / moderate / challenging) | browser tests |
|---|---|---|---|--:|
| case_01 | blog | Vite + React + TypeScript | 5 / 5 / 0 | 29 |
| case_02 | spreadsheet table | plain HTML, CSS, JS modules | 6 / 3 / 1 | 47 |
| case_03 | form builder | plain HTML, CSS, JS modules | 5 / 4 / 1 | 40 |

## How it is scored

The answer's files are laid over the starter `src/` (a file left out keeps its starter
content), the app is served the way Web-Bench serves it -- Vite for the React project,
`serve` for the static ones -- and the project's Playwright specs for those ten steps run in
Chromium: the page is loaded, clicked, typed into and inspected.

- **Case score** = share of the case's browser tests that pass.
- **Run score** = mean case score, so each project weighs the same.
- **Steps** = steps whose every test passes, reported alongside as the stricter reading.
- **Code size** is reported next to the score and never enters it: the lines the answer added
  to the starter's `.html`, `.css`, `.js`, `.mjs`, `.jsx`, `.ts` and `.tsx` files, counted as
  `git diff` counts added lines but skipping blank lines and comments, plus the same lines'
  non-whitespace characters. Test files are counted apart. An answer that could not be read
  has no code size, so the run totals say how many cases they cover (`code_cases`). Fewer
  lines is only a win between answers that pass the same tests, so compare it case by case.

An answer with no JSON `files` object, or a path outside `src/`, scores 0. The starter handed
back unchanged passes 0 / 4 / 3 tests, because it already covers part of each project's first
step, so the floor for a run is about 0.05 rather than 0.

## Answer format

End the reply with one fenced JSON block:

```json
{"files": {"index.html": "<full file content>", "common/menu.js": "<full file content>"}}
```

Keys are paths relative to `src/`; values are full file contents.

## How this differs from Web-Bench

- **Renamed.** Every string a spec keys on -- visible text, class names, the names form
  questions submit under -- is renamed consistently in the steps, the specs and the
  reference, so Web-Bench's published reference solutions, handed in unchanged, score
  0 / 11 / 12 of the 29 / 47 / 40 tests. Web-Bench is public, though: the same solutions with
  the new names from the steps carried over score 29 / 35 / 40. The renames stop a verbatim
  copy, not an agent that looks the projects up.
- **First ten steps only**, and all ten given at once rather than one per turn.
- **One agent run per case** instead of Web-Bench's Web-Agent loop, so scores here are not
  comparable to Web-Bench's Pass@1.

## Timing

A capable coding agent takes roughly 5–10 minutes per case, most of it spent building and
checking the app locally, and a slow one can take longer. Grading a case takes 1–4 minutes.

- **On trapstreet.run** each case is leased for 15 minutes (`lease_seconds: 900`); once the
  lease runs out the case can be handed out again, and the late answer is then refused.
- **With `tp run`**, a solution's default per-case timeout is 600 seconds, and a case killed at
  the limit scores 0. Give it room in the solution's `trap.yaml`:

  ```yaml
  timeout: 1800
  ```

## Licence

Web-Bench is Apache-2.0; its licence is reproduced in `LICENSE.web-bench`. The step
descriptions and starter files in `inputs/` are Web-Bench's, modified as described under
"How this differs from Web-Bench".

## Acknowledgements

The projects, starter code, step descriptions and browser specs come from Web-Bench by Kai Xu,
YiWei Mao, XinYi Guan and ZiLong Feng.

```bibtex
@article{xu2025webbench,
  title={Web-Bench: A LLM Code Benchmark Based on Web Standards and Frameworks},
  author={Xu, Kai and Mao, YiWei and Guan, XinYi and Feng, ZiLong},
  journal={arXiv preprint arXiv:2505.07473},
  year={2025}
}
```
