"""Tests for the svg_clock judge.

The judge's whole job is to decide whether the board can draw the answer,
so most of these are about the ways an answer that looks fine renders as
a broken image, or vanishes, once it is loaded through <img>.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

TASK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TASK))
import judge  # noqa: E402

CLOCK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'
    '<circle cx="100" cy="100" r="92" fill="#fff" stroke="#111"/>'
    '<line x1="100" y1="100" x2="27.6" y2="84.6" stroke="#111"/>'
    '<line x1="100" y1="100" x2="145.9" y2="119.9" stroke="#111"/>'
    "</svg>"
)


def test_a_clean_svg_is_passed_through_as_the_drawing():
    r = judge.score_case(CLOCK)
    assert r["score"] == 1.0
    assert r["drawing"] == CLOCK
    assert r["shapes"] == 3


def test_the_drawing_never_travels_as_agent_answer():
    # The board drops `agent_answer` on purpose; a drawing sent under it
    # would simply not appear.
    r = judge.score_case(CLOCK)
    assert "agent_answer" not in r
    assert "agent_output" not in r


def test_chatter_and_a_code_fence_around_the_svg_are_ignored():
    r = judge.score_case("Sure! Here's your clock:\n```svg\n" + CLOCK + "\n```\nEnjoy.")
    assert r["score"] == 1.0
    assert r["drawing"].startswith("<svg")
    assert r["drawing"].endswith("</svg>")


def test_an_xml_declaration_before_the_svg_is_dropped():
    r = judge.score_case('<?xml version="1.0" encoding="UTF-8"?>\n' + CLOCK)
    assert r["drawing"].startswith("<svg")


def test_a_missing_svg_namespace_is_added_not_held_against_the_model():
    # Without it, <img> shows a broken image.
    bare = CLOCK.replace(' xmlns="http://www.w3.org/2000/svg"', "")
    r = judge.score_case(bare)
    assert r["score"] == 1.0
    assert ET.fromstring(r["drawing"]).tag == "{http://www.w3.org/2000/svg}svg"


def test_an_undeclared_xlink_prefix_is_declared():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<defs><circle id="c" r="4"/></defs><use xlink:href="#c"/></svg>'
    )
    r = judge.score_case(svg)
    assert r["score"] == 1.0
    assert 'xmlns:xlink="http://www.w3.org/1999/xlink"' in r["drawing"]


def test_prose_with_no_svg_scores_zero_with_a_reason():
    r = judge.score_case("I can't draw, but 3:47 is thirteen minutes to four.")
    assert r["score"] == 0.0
    assert "no <svg>" in r["reason"]
    assert "drawing" not in r


def test_malformed_svg_scores_zero_rather_than_rendering_broken():
    r = judge.score_case('<svg xmlns="http://www.w3.org/2000/svg"><line x1="1"></svg>')
    assert r["score"] == 0.0
    assert "well-formed" in r["reason"]


def test_an_oversized_drawing_is_reported_not_silently_dropped_by_the_board():
    big = CLOCK.replace("</svg>", "<!--" + "x" * (65 * 1024) + "--></svg>")
    r = judge.score_case(big)
    assert r["score"] == 0.0
    assert "the board draws up to" in r["reason"]


def test_the_size_cap_counts_the_way_javascript_does():
    # An astral character is one code point in Python and two UTF-16 units
    # in JavaScript; the board measures the latter.
    assert judge._utf16_units("🕒") == 2
    assert judge._utf16_units("abc") == 3


def test_empty_output_scores_zero():
    assert judge.score_case("   \n")["score"] == 0.0


@pytest.mark.parametrize("exit_code, want", [(0, 1.0), (1, 0.0)])
def test_main_under_the_manifest_the_platform_worker_writes(tmp_path, exit_code, want):
    # The same shape apps/grader/src/grader/worker.py builds: the answer as
    # stdout, an always-{"exit_code": 0} meta for an accepted answer, and an
    # empty outputs dir -- no usage.json, so nothing about the model.
    (tmp_path / "stdout").write_text(CLOCK)
    (tmp_path / "stderr").write_text("")
    (tmp_path / "meta.json").write_text(json.dumps({"exit_code": exit_code}))
    (tmp_path / "outputs").mkdir()
    manifest = {
        "inputs_dir": str(TASK / "inputs" / "clock_347"),
        "expected_dir": str(TASK / "expected" / "clock_347"),
        "outputs_dir": str(tmp_path / "outputs"),
        "run": {
            "stdout": str(tmp_path / "stdout"),
            "stderr": str(tmp_path / "stderr"),
            "meta": str(tmp_path / "meta.json"),
        },
    }
    out = subprocess.run(
        [sys.executable, str(TASK / "judge.py")],
        env={**os.environ, "TRAPTASK_MANIFEST": json.dumps(manifest)},
        capture_output=True, text=True, check=True,
    )
    r = json.loads(out.stdout)
    assert r["score"] == want
    assert r["id"] == "clock_347"
    assert ("drawing" in r) == (want == 1.0)


def test_meta_without_an_exit_code_is_read_as_success(tmp_path):
    (tmp_path / "stdout").write_text(CLOCK)
    (tmp_path / "meta.json").write_text("{}")
    manifest = {
        "expected_dir": str(TASK / "expected" / "clock_347"),
        "run": {"stdout": str(tmp_path / "stdout"), "meta": str(tmp_path / "meta.json")},
    }
    out = subprocess.run(
        [sys.executable, str(TASK / "judge.py")],
        env={**os.environ, "TRAPTASK_MANIFEST": json.dumps(manifest)},
        capture_output=True, text=True, check=True,
    )
    assert json.loads(out.stdout)["score"] == 1.0
