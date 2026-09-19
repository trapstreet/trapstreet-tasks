#!/usr/bin/env python3
"""Download the Mind2Web shard and render this task's inputs/.

The dataset is CC-BY-4.0 and its authors ask that the unzipped data files not
be redistributed online, so this repository ships the transformation rather
than the data. One command materialises the cases:

    python3 prepare.py

It downloads one 28 MB shard from the authors' HuggingFace distribution into
~/.cache/trapstreet/mind2web (override with MIND2WEB_CACHE), then writes
inputs/<case_id>/{task.md, step.md, step.json, page.html} and checks every
byte against expected.sha256.

No browser, no Docker, no API key, and nothing to run again unless you clear
the cache.
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402
import source  # noqa: E402


def download() -> Path:
    if source.LOCAL.exists():
        digest = hashlib.sha256(source.LOCAL.read_bytes()).hexdigest()
        if digest == source.SHARD_SHA256:
            print(f"shard already cached at {source.LOCAL}")
            return source.LOCAL
        print(f"cached shard has the wrong digest ({digest[:12]}...), re-downloading")
    source.CACHE.mkdir(parents=True, exist_ok=True)
    print(f"downloading {source.URL}\n       -> {source.LOCAL}  (28 MB)")
    tmp = source.LOCAL.with_suffix(".part")
    with urllib.request.urlopen(source.URL) as r, tmp.open("wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
    if digest != source.SHARD_SHA256:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"downloaded shard digest {digest} != expected {source.SHARD_SHA256}")
    tmp.rename(source.LOCAL)
    return source.LOCAL


def main() -> None:
    download()
    index = json.loads((HERE / "cases.json").read_text())
    by_uid = {}
    for t in json.loads(source.shard_path().read_text()):
        for a in t["actions"]:
            by_uid[a["action_uid"]] = (t, a)

    written = {}
    for case in index["cases"]:
        task, action = by_uid[case["action_uid"]]
        inputs, _mapping = render.render_inputs(case["id"], task, action)
        d = HERE / "inputs" / case["id"]
        d.mkdir(parents=True, exist_ok=True)
        for name, text in inputs.items():
            (d / name).write_text(text)
            written[f"inputs/{case['id']}/{name}"] = hashlib.sha256(text.encode()).hexdigest()

    expected = {}
    for line in (HERE / "expected.sha256").read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        h, path = line.split(None, 1)
        expected[path.strip()] = h
    bad = [k for k, h in expected.items() if k in written and written[k] != h]
    missing = [k for k in expected if k not in written]
    if bad or missing:
        raise SystemExit(f"FAIL: {len(bad)} file(s) differ from expected.sha256, {len(missing)} missing.\n"
                         f"      first few: {(bad + missing)[:3]}")
    print(f"{len(index['cases'])} cases rendered into inputs/ -- "
          f"all {len(expected)} files match expected.sha256")


if __name__ == "__main__":
    main()
