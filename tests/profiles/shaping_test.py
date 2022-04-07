from fontTools.ttLib import TTFont
import json
import os
import tempfile

from fontbakery.checkrunner import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.profiles import universal as universal_profile


def wrap_args(config, font):
    ttFont = TTFont(font)
    return {
        "config": config,
        "font": font,
        "fonts": [font],
        "ttFont": ttFont,
        "ttFonts": [ttFont],
    }


def test_check_shaping_regression():
    """Check that we can test shaping against expectations."""
    check = CheckTester(universal_profile, "com.google.fonts/check/shaping/regression")

    shaping_test = {
        "configuration": {},
        "tests": [{"input": "AV", "expectation": "A=0+664|V=1+691"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(shaping_test, open(os.path.join(tmp_gf_dir, "test.json"), "w"))

        config = {"com.google.fonts/check/shaping": {"test_directory": tmp_gf_dir}}

        font = TEST_FILE("nunito/Nunito-Regular.ttf")
        assert_PASS(check(wrap_args(config, font)), "Nunito: A=664,V=691")

        font = TEST_FILE("slabo/Slabo13px.ttf")
        assert_results_contain(
            check(wrap_args(config, font)),
            FAIL,
            "shaping-regression",
            "Slabo: A!=664,V!=691",
        )


def test_check_shaping_forbidden():
    """Check that we can test for forbidden glyphs in output."""
    check = CheckTester(universal_profile, "com.google.fonts/check/shaping/forbidden")

    shaping_test = {
        "configuration": {"forbidden_glyphs": [".notdef"]},
        "tests": [{"input": "日"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(shaping_test, open(os.path.join(tmp_gf_dir, "test.json"), "w"))

        config = {"com.google.fonts/check/shaping": {"test_directory": tmp_gf_dir}}

        font = TEST_FILE("cjk/SourceHanSans-Regular.otf")
        assert_PASS(check(wrap_args(config, font)), "Source Han contains CJK")

        font = TEST_FILE("slabo/Slabo13px.ttf")
        assert_results_contain(
            check(wrap_args(config, font)),
            FAIL,
            "shaping-forbidden",
            "Slabo shapes .notdef for CJK",
        )


def test_check_shaping_collides():
    """Check that we can test for colliding glyphs in output."""
    check = CheckTester(universal_profile, "com.google.fonts/check/shaping/collides")

    shaping_test = {
        "configuration": {"collidoscope": {"area": 0, "bases": True, "marks": True}},
        "tests": [{"input": "ïï"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(shaping_test, open(os.path.join(tmp_gf_dir, "test.json"), "w"))

        config = {"com.google.fonts/check/shaping": {"test_directory": tmp_gf_dir}}

        font = TEST_FILE("cousine/Cousine-Regular.ttf")
        assert_PASS(check(wrap_args(config, font)), "ïï doesn't collide in Cousine")

        font = TEST_FILE("nunito/Nunito-Black.ttf")
        assert_results_contain(
            check(wrap_args(config, font)),
            FAIL,
            "shaping-collides",
            "ïï collides in Nunito",
        )
