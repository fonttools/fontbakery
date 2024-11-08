import json
import os
import tempfile

from conftest import check_id
from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    TEST_FILE,
)


@check_id("shaping/regression")
def test_check_shaping_regression(check):
    """Check that we can test shaping against expectations."""

    shaping_test = {
        "configuration": {},
        "tests": [{"input": "AV", "expectation": "A=0+664|V=1+691"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(
            shaping_test,
            open(os.path.join(tmp_gf_dir, "test.json"), "w", encoding="utf-8"),
        )

        config = {"shaping": {"test_directory": tmp_gf_dir}}

        font = TEST_FILE("nunito/Nunito-Regular.ttf")
        assert_PASS(check(font, config=config), "Nunito: A=664,V=691")

        font = TEST_FILE("slabo/Slabo13px.ttf")
        assert_results_contain(
            check(font, config=config),
            FAIL,
            "shaping-regression",
            "Slabo: A!=664,V!=691",
        )


@check_id("shaping/regression")
def test_check_shaping_regression_with_variations(check):
    """Check that we can test shaping with variation settings against expectations."""

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

        config = {"shaping": {"test_directory": tmp_gf_dir}}

        font = TEST_FILE("varfont/Oswald-VF.ttf")
        assert_PASS(check(font, config=config), "Oswald: A=0+453|V=1+505")


@check_id("shaping/forbidden")
def test_check_shaping_forbidden(check):
    """Check that we can test for forbidden glyphs in output."""

    shaping_test = {
        "configuration": {"forbidden_glyphs": [".notdef"]},
        "tests": [{"input": "日"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(
            shaping_test,
            open(os.path.join(tmp_gf_dir, "test.json"), "w", encoding="utf-8"),
        )

        config = {"shaping": {"test_directory": tmp_gf_dir}}

        font = TEST_FILE("cjk/SourceHanSans-Regular.otf")
        assert_PASS(check(font, config=config), "Source Han contains CJK")

        font = TEST_FILE("slabo/Slabo13px.ttf")
        assert_results_contain(
            check(font, config=config),
            FAIL,
            "shaping-forbidden",
            "Slabo shapes .notdef for CJK",
        )


@check_id("shaping/collides")
def test_check_shaping_collides(check):
    """Check that we can test for colliding glyphs in output."""

    shaping_test = {
        "configuration": {"collidoscope": {"area": 0, "bases": True, "marks": True}},
        "tests": [{"input": "ïï"}],
    }

    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        json.dump(
            shaping_test,
            open(os.path.join(tmp_gf_dir, "test.json"), "w", encoding="utf-8"),
        )

        config = {"shaping": {"test_directory": tmp_gf_dir}}

        font = TEST_FILE("cousine/Cousine-Regular.ttf")
        assert_PASS(check(font, config=config), "ïï doesn't collide in Cousine")

        font = TEST_FILE("nunito/Nunito-Black.ttf")
        assert_results_contain(
            check(font, config=config),
            FAIL,
            "shaping-collides",
            "ïï collides in Nunito",
        )


@check_id("dotted_circle")
def test_check_dotted_circle(check):
    """Ensure dotted circle glyph is present and can attach marks."""

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(check(font), WARN, "missing-dotted-circle")

    font = TEST_FILE("broken_markazitext/MarkaziText-VF.ttf")
    assert_results_contain(check(font), FAIL, "unattached-dotted-circle-marks")


@check_id("soft_dotted")
def test_check_soft_dotted(check):
    """Check if font substitues soft dotted glyphs when combined with top marks."""

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
