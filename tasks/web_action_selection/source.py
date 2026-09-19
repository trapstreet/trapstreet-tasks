"""Locating the Mind2Web shard this task is built from.

The dataset is CC-BY-4.0, but its authors ask specifically:

    "Please DO NOT redistribute the unzipped data files online."

So neither half of this task carries their page data. Both halves carry our
transformation of it -- case selection, element extraction, id renumbering --
and read the pages from a shard the user downloads from the authors' own
HuggingFace distribution. `prepare.py` in the public half does that download.

Only train shards are used. The Mind2Web test splits are password-protected
precisely to keep them out of training corpora, and pulling them into a public
benchmark would defeat that.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

REPO = "osunlp/Mind2Web"
SHARD = "data/train/train_10.json"
SHARD_SHA256 = "182542d7947b3fa9e90fc57a3d82d4d8f2997ca5a06664217720d7a78a956e33"
URL = f"https://huggingface.co/datasets/{REPO}/resolve/main/{SHARD}"

CACHE = Path(os.environ.get("MIND2WEB_CACHE", Path.home() / ".cache" / "trapstreet" / "mind2web"))
LOCAL = CACHE / "train_10.json"


def shard_path() -> Path:
    if not LOCAL.exists():
        raise SystemExit(
            f"Mind2Web shard not found at {LOCAL}.\n"
            f"Download it from the authors' distribution first:\n\n"
            f"    python3 prepare.py\n\n"
            f"or fetch {URL} to that path by hand."
        )
    return LOCAL


def load_actions() -> dict[str, dict]:
    """action_uid -> {cleaned_html, ...} for every action in the shard."""
    data = json.loads(shard_path().read_text())
    out = {}
    for task in data:
        for act in task.get("actions", []):
            out[act["action_uid"]] = act
    return out
