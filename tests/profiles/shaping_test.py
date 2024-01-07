import json
import os
import tempfile
from unittest.mock import patch

from fontTools.ttLib import TTFont

from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.profiles import shaping as shaping_profile


def wrap_args(config, font):
    ttFont = TTFont(font)
    return {
        "config": config,
        "font": font,
        "fonts": [font],
        "ttFont": ttFont,
        "ttFonts": [ttFont],
    }


@patch("vharfbuzz.Vharfbuzz", side_effect=ImportError)
def test_extra_needed_exit(mock_import_error):
    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    with patch("sys.exit") as mock_exit:
        check = CheckTester(
            shaping_profile, "com.google.fonts/check/shaping/regression"
        )
        check(font)
        mock_exit.assert_called()


def test_check_shaping_regression():
    """Check that we can test shaping against expectations."""
    check = CheckTester(shaping_profile, "com.google.fonts/check/shaping/regression")

    shaping_test = {
        "configuration": {},
        "tests": [{"input": "AV", "expectation": "A=0+664|V=1+691"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(
            shaping_test,
            open(os.path.join(tmp_gf_dir, "test.json"), "w", encoding="utf-8"),
        )

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


def test_check_shaping_regression_with_variations():
    """Check that we can test shaping with variation settings against expectations."""
    check = CheckTester(shaping_profile, "com.google.fonts/check/shaping/regression")

    shaping_test = {
        "configuration": {},
        "tests": [
            {
                "input": "AV",
                "expectation": "A=0+453|V=1+505",
            },
            {
                "input": "AV",
                "expectation": "A=0+517|V=1+526",
                "variations": {"wght": 700},
            },
        ],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(
            shaping_test,
            open(os.path.join(tmp_gf_dir, "test.json"), "w", encoding="utf-8"),
        )

        config = {"com.google.fonts/check/shaping": {"test_directory": tmp_gf_dir}}

        font = TEST_FILE("varfont/Oswald-VF.ttf")
        assert_PASS(check(wrap_args(config, font)), "Oswald: A=0+453|V=1+505")


def test_check_shaping_forbidden():
    """Check that we can test for forbidden glyphs in output."""
    check = CheckTester(shaping_profile, "com.google.fonts/check/shaping/forbidden")

    shaping_test = {
        "configuration": {"forbidden_glyphs": [".notdef"]},
        "tests": [{"input": "日"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(
            shaping_test,
            open(os.path.join(tmp_gf_dir, "test.json"), "w", encoding="utf-8"),
        )

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
    check = CheckTester(shaping_profile, "com.google.fonts/check/shaping/collides")

    shaping_test = {
        "configuration": {"collidoscope": {"area": 0, "bases": True, "marks": True}},
        "tests": [{"input": "ïï"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(
            shaping_test,
            open(os.path.join(tmp_gf_dir, "test.json"), "w", encoding="utf-8"),
        )

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


def test_check_dotted_circle():
    """Ensure dotted circle glyph is present and can attach marks."""
    check = CheckTester(shaping_profile, "com.google.fonts/check/dotted_circle")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(check(font), WARN, "missing-dotted-circle")

    font = TEST_FILE("broken_markazitext/MarkaziText-VF.ttf")
    assert_results_contain(check(font), FAIL, "unattached-dotted-circle-marks")


def test_check_soft_dotted():
    """Check if font substitues soft dotted glyphs
    when combined with top marks."""
    check = CheckTester(shaping_profile, "com.google.fonts/check/soft_dotted")

    font = TEST_FILE("abeezee/ABeeZee-Regular.ttf")
    msg = assert_results_contain(check(font), WARN, "soft-dotted")
    assert "The dot of soft dotted characters used in orthographies" not in msg
    assert "The dot of soft dotted characters _should_ disappear" in msg

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    msg = assert_results_contain(check(font), WARN, "soft-dotted")
    assert "The dot of soft dotted characters used in orthographies" in msg
    assert "The dot of soft dotted characters _should_ disappear" in msg

    font = TEST_FILE("akshar/Akshar[wght].ttf")
    assert_PASS(check(font), "All soft dotted characters seem to lose their dot ...")

    font = TEST_FILE("rosarivo/Rosarivo-Regular.ttf")
    assert_SKIP(check(font), "It is not clear if soft dotted characters ...")
