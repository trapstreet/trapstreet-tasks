"""Tests for the svg_landing_page judge.

Most of the judge's job is deciding whether the board can draw the answer,
so most of these are about the ways an answer that looks fine renders as a
broken image, or vanishes, once it is loaded through <img>. The rest cover
the two descriptive columns, `colors` and `fonts`.
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

PAGE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 3200">'
    '<rect width="1440" height="900" fill="#0B1F3A"/>'
    '<text x="120" y="360" font-family="Georgia, serif" font-size="88" fill="#fff">Ask your data anything.</text>'
    '<rect x="120" y="520" width="180" height="56" rx="8" fill="#F2B84B"/>'
    "</svg>"
)


def _svg(body: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">{body}</svg>'


def test_a_clean_svg_is_passed_through_as_the_drawing():
    r = judge.score_case(PAGE)
    assert r["score"] == 1.0
    assert r["drawing"] == PAGE
    assert r["shapes"] == 3
    assert r["colors"] == 3
    assert r["fonts"] == "Georgia"


def test_the_drawing_never_travels_as_agent_answer():
    # The board drops `agent_answer` on purpose; a drawing sent under it
    # would simply not appear.
    r = judge.score_case(PAGE)
    assert "agent_answer" not in r
    assert "agent_output" not in r


def test_no_metric_is_named_type():
    # A `type` string makes the board read the card as a classification
    # and print "type in n of m runs" under the picture.
    assert "type" not in judge.score_case(PAGE)


def test_chatter_and_a_code_fence_around_the_svg_are_ignored():
    r = judge.score_case("Here's the landing page:\n```svg\n" + PAGE + "\n```\nLet me know!")
    assert r["score"] == 1.0
    assert r["drawing"].startswith("<svg")
    assert r["drawing"].endswith("</svg>")


def test_an_xml_declaration_before_the_svg_is_dropped():
    r = judge.score_case('<?xml version="1.0" encoding="UTF-8"?>\n' + PAGE)
    assert r["drawing"].startswith("<svg")


def test_a_missing_svg_namespace_is_added_not_held_against_the_model():
    # Without it, <img> shows a broken image.
    bare = PAGE.replace(' xmlns="http://www.w3.org/2000/svg"', "")
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
    r = judge.score_case("A bold serif headline over a deep navy field, with an amber button.")
    assert r["score"] == 0.0
    assert "no <svg>" in r["reason"]
    assert "drawing" not in r


def test_html_instead_of_svg_scores_zero():
    # The board can only draw SVG; an HTML page is a different deliverable.
    r = judge.score_case("<!doctype html><html><body><h1>Ask your data anything.</h1></body></html>")
    assert r["score"] == 0.0


def test_malformed_svg_scores_zero_rather_than_rendering_broken():
    r = judge.score_case('<svg xmlns="http://www.w3.org/2000/svg"><text x="1">Ask</svg>')
    assert r["score"] == 0.0
    assert "well-formed" in r["reason"]


def test_an_oversized_drawing_is_reported_not_silently_dropped_by_the_board():
    big = PAGE.replace("</svg>", "<!--" + "x" * (65 * 1024) + "--></svg>")
    r = judge.score_case(big)
    assert r["score"] == 0.0
    assert "the board draws up to" in r["reason"]


def test_the_size_cap_counts_the_way_javascript_does():
    # An astral character is one code point in Python and two UTF-16 units
    # in JavaScript; the board measures the latter.
    assert judge._utf16_units("📊") == 2
    assert judge._utf16_units("abc") == 3


def test_empty_output_scores_zero():
    assert judge.score_case("   \n")["score"] == 0.0


# --- colors -----------------------------------------------------------------

def test_one_colour_written_four_ways_counts_once():
    r = judge.score_case(_svg(
        '<rect fill="#fff"/><rect fill="#FFFFFF"/>'
        '<rect fill="rgb(255, 255, 255)"/><rect fill="white"/>'
    ))
    assert r["colors"] == 1


def test_alpha_is_ignored_in_the_palette():
    r = judge.score_case(_svg('<rect fill="#0b1f3a"/><rect fill="#0B1F3A80"/><rect fill="rgba(11,31,58,.5)"/>'))
    assert r["colors"] == 1


def test_hsl_is_folded_into_the_same_hex():
    r = judge.score_case(_svg('<rect fill="hsl(0, 100%, 50%)"/><rect fill="#ff0000"/>'))
    assert r["colors"] == 1


def test_gradient_stops_strokes_and_css_all_count():
    r = judge.score_case(_svg(
        "<style>.a { fill: #111111; } .b:hover { stroke: #222222 }</style>"
        '<linearGradient id="g"><stop offset="0" stop-color="#333333"/></linearGradient>'
        '<rect class="a" style="stroke:#444444; stroke-width:2"/>'
        '<line stroke="#555555"/>'
    ))
    assert r["colors"] == 5


def test_none_currentcolor_and_paint_servers_are_not_colours():
    r = judge.score_case(_svg(
        '<rect fill="none" stroke="currentColor"/><rect fill="url(#g)"/>'
        '<rect fill="transparent"/><rect fill="#123456"/>'
    ))
    assert r["colors"] == 1


def test_a_drawing_with_no_colour_declared_reports_zero():
    assert judge.score_case(_svg('<rect width="4" height="4"/>'))["colors"] == 0


# --- fonts ------------------------------------------------------------------

def test_fonts_are_the_first_family_of_each_stack_in_first_use_order():
    r = judge.score_case(_svg(
        '<text font-family="\'Playfair Display\', Georgia, serif">A</text>'
        '<text font-family="Inter, system-ui, sans-serif">B</text>'
        '<text font-family="Playfair Display, serif">C</text>'
    ))
    assert r["fonts"] == "Playfair Display, Inter"


def test_fonts_are_read_from_inline_style_and_style_blocks():
    r = judge.score_case(_svg(
        "<style>.h { font-family: \"Fraunces\", serif; font-weight: 600 }</style>"
        '<text class="h">A</text>'
        '<text style="font-size:14px; font-family: \'IBM Plex Sans\', sans-serif">B</text>'
    ))
    assert r["fonts"] == "Fraunces, IBM Plex Sans"


def test_the_font_shorthand_is_read_past_its_weight_and_size():
    # 700 is a weight, not a size; the family follows the size.
    r = judge.score_case(_svg(
        '<style>.h { font: italic 700 64px/1.1 "Söhne", Helvetica, sans-serif; }</style>'
        '<text class="h">A</text>'
    ))
    assert r["fonts"] == "Söhne"


def test_a_drawing_that_names_no_font_reports_default():
    assert judge.score_case(_svg("<text>A</text>"))["fonts"] == "default"


# --- the platform manifest --------------------------------------------------

@pytest.mark.parametrize("exit_code, want", [(0, 1.0), (1, 0.0)])
def test_main_under_the_manifest_the_platform_worker_writes(tmp_path, exit_code, want):
    # The same shape apps/grader/src/grader/worker.py builds: the answer as
    # stdout, an always-{"exit_code": 0} meta for an accepted answer, and an
    # empty outputs dir -- no usage.json, so nothing about the model.
    (tmp_path / "stdout").write_text(PAGE)
    (tmp_path / "stderr").write_text("")
    (tmp_path / "meta.json").write_text(json.dumps({"exit_code": exit_code}))
    (tmp_path / "outputs").mkdir()
    manifest = {
        "inputs_dir": str(TASK / "inputs" / "case_01"),
        "expected_dir": str(TASK / "expected" / "case_01"),
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
    assert r["id"] == "case_01"
    assert ("drawing" in r) == (want == 1.0)


def test_meta_without_an_exit_code_is_read_as_success(tmp_path):
    (tmp_path / "stdout").write_text(PAGE)
    (tmp_path / "meta.json").write_text("{}")
    manifest = {
        "expected_dir": str(TASK / "expected" / "case_01"),
        "run": {"stdout": str(tmp_path / "stdout"), "meta": str(tmp_path / "meta.json")},
    }
    out = subprocess.run(
        [sys.executable, str(TASK / "judge.py")],
        env={**os.environ, "TRAPTASK_MANIFEST": json.dumps(manifest)},
        capture_output=True, text=True, check=True,
    )
    assert json.loads(out.stdout)["score"] == 1.0


def test_the_question_file_and_the_yaml_description_are_the_same_brief():
    import yaml  # noqa: PLC0415 -- only this test needs it
    spec = yaml.safe_load((TASK / "traptask.yaml").read_text())
    brief = (TASK / "inputs" / "case_01" / "question.txt").read_text().strip()
    assert spec["cases"][0]["description"].strip() == brief
