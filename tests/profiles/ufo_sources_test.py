import os

import defcon
import pytest

from fontbakery.checkrunner import FAIL, SKIP, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.profiles.ufo_sources import profile as ufo_sources_profile


@pytest.fixture
def empty_ufo_font(tmpdir):
    ufo = defcon.Font()
    ufo.newGlyph("gname")
    ufo_path = str(tmpdir.join("empty_font.ufo"))
    ufo.save(ufo_path)
    return (ufo, ufo_path)


def test_check_ufolint(empty_ufo_font):
    check = CheckTester(ufo_sources_profile, "com.daltonmaag/check/ufolint")

    _, ufo_path = empty_ufo_font

    assert assert_PASS(check(ufo_path)) == "ufolint passed the UFO source."

    os.remove(os.path.join(ufo_path, "metainfo.plist"))
    msg = assert_results_contain(check(ufo_path), FAIL, "ufolint-fail")
    assert "ufolint failed the UFO source." in msg

    # Run the check on a non-UFO font. The result is PASS because ufolint does not
    # issue any error when it's run on a non-UFO font.
    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    assert assert_PASS(check(font)) == "ufolint passed the UFO source."


def test_check_required_fields(empty_ufo_font):
    check = CheckTester(ufo_sources_profile, "com.daltonmaag/check/ufo_required_fields")

    ufo, _ = empty_ufo_font

    msg = assert_results_contain(check(ufo), FAIL, "missing-required-fields")
    assert "Required field(s) missing:" in msg

    ufo.info.unitsPerEm = 1000
    ufo.info.ascender = 800
    ufo.info.descender = -200
    ufo.info.xHeight = 500
    ufo.info.capHeight = 700
    ufo.info.familyName = "Test"

    assert assert_PASS(check(ufo)) == "Required fields present."

    # Run the check on a non-UFO font.
    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert msg == "Unfulfilled Conditions: ufo_font"


def test_check_recommended_fields(empty_ufo_font):
    check = CheckTester(
        ufo_sources_profile, "com.daltonmaag/check/ufo_recommended_fields"
    )

    ufo, _ = empty_ufo_font

    msg = assert_results_contain(check(ufo), WARN, "missing-recommended-fields")
    assert "Recommended field(s) missing:" in msg

    ufo.info.postscriptUnderlineThickness = 1000
    ufo.info.postscriptUnderlinePosition = 800
    ufo.info.versionMajor = -200
    ufo.info.versionMinor = 500
    ufo.info.styleName = "700"
    ufo.info.copyright = "Test"
    ufo.info.openTypeOS2Panose = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    assert assert_PASS(check(ufo)) == "Recommended fields present."

    # Run the check on a non-UFO font.
    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert msg == "Unfulfilled Conditions: ufo_font"


def test_check_unnecessary_fields(empty_ufo_font):
    check = CheckTester(
        ufo_sources_profile, "com.daltonmaag/check/ufo_unnecessary_fields"
    )

    ufo, _ = empty_ufo_font

    assert assert_PASS(check(ufo)) == "Unnecessary fields omitted."

    ufo.info.openTypeNameUniqueID = "aaa"
    ufo.info.openTypeNameVersion = "1.000"
    ufo.info.postscriptUniqueID = -1
    ufo.info.year = 2018

    msg = assert_results_contain(check(ufo), WARN, "unnecessary-fields")
    assert "Unnecessary field(s) present:" in msg

    # Run the check on a non-UFO font.
    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert msg == "Unfulfilled Conditions: ufo_font"
