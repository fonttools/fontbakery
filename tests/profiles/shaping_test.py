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
from fontbakery.profiles import universal


def wrap_args(config, ttFont):
    return {
        "config": config,
        "font": ttFont.reader.file.name,
        "fonts": [ttFont.reader.file.name],
        "ttFont": ttFont,
        "ttFonts": [ttFont],
    }


def test_check_shaping_regression():
    """ Check that we can test shaping against expectations. """
    check = CheckTester(universal, "com.google.fonts/check/shaping/regression")

    shaping_test = {
        "configuration": {},
        "tests": [{"input": "AV", "expectation": "A=0+664|V=1+691"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(shaping_test, open(os.path.join(tmp_gf_dir, "test.json"), "w"))

        config = {"com.google.fonts/check/shaping": {"test_directory": tmp_gf_dir}}

        ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
        assert_PASS(check(wrap_args(config, ttFont)), "Nunito: A=664,V=691")

        ttFont = TTFont(TEST_FILE("slabo/Slabo13px.ttf"))
        assert_results_contain(
            check(wrap_args(config, ttFont)), FAIL, "shaping-regression", "Slabo: A!=664,V!=691"
        )


def test_check_shaping_forbidden():
    """ Check that we can test for forbidden glyphs in output. """
    check = CheckTester(universal, "com.google.fonts/check/shaping/forbidden")

    shaping_test = {
        "configuration": {"forbidden_glyphs": [".notdef"]},
        "tests": [{"input": "日"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(shaping_test, open(os.path.join(tmp_gf_dir, "test.json"), "w"))

        config = {"com.google.fonts/check/shaping": {"test_directory": tmp_gf_dir}}

        ttFont = TTFont(TEST_FILE("cjk/SourceHanSans-Regular.otf"))
        assert_PASS(check(wrap_args(config, ttFont)), "Source Han contains CJK")

        ttFont = TTFont(TEST_FILE("slabo/Slabo13px.ttf"))
        assert_results_contain(
            check(wrap_args(config, ttFont)), FAIL, "shaping-forbidden", "Slabo shapes .notdef for CJK"
        )


def test_check_shaping_collides():
    """ Check that we can test for colliding glyphs in output. """
    check = CheckTester(universal, "com.google.fonts/check/shaping/collides")

    shaping_test = {
        "configuration": {"collidoscope": {"area": 0, "marks": True}},
        "tests": [{"input": "ïï"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(shaping_test, open(os.path.join(tmp_gf_dir, "test.json"), "w"))

        config = {"com.google.fonts/check/shaping": {"test_directory": tmp_gf_dir}}

        ttFont = TTFont(TEST_FILE("cousine/Cousine-Regular.ttf"))
        assert_PASS(check(wrap_args(config, ttFont)), "ïï doesn't collide in Cousine")

        ttFont = TTFont(TEST_FILE("nunito/Nunito-Black.ttf"))
        assert_results_contain(
            check(wrap_args(config, ttFont)), FAIL, "shaping-collides", "ïï collides in Nunito"
        )
