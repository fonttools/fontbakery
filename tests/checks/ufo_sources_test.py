import os
import sys

import defcon
import pytest

from conftest import ImportRaiser, remove_import_raiser

from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    assert_SKIP,
    CheckTester,
    TEST_FILE,
)


@pytest.fixture
def empty_ufo_font(tmpdir):
    ufo = defcon.Font()
    ufo.newGlyph("gname")
    ufo_path = str(tmpdir.join("empty_font.ufo"))
    ufo.save(ufo_path)
    return (ufo, ufo_path)


def test_extra_needed_exit(monkeypatch):
    module_name = "defcon"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)

    ufo_path = TEST_FILE("test.ufo")
    with pytest.raises(SystemExit):
        check = CheckTester("com.daltonmaag/check/ufo_required_fields")
        check(ufo_path)

    remove_import_raiser(module_name)


def test_check_ufolint(empty_ufo_font):
    check = CheckTester("com.daltonmaag/check/ufolint")

    _, ufo_path = empty_ufo_font

    assert_PASS(check(ufo_path))

    os.remove(os.path.join(ufo_path, "metainfo.plist"))
    msg = assert_results_contain(check(ufo_path), FAIL, "ufolint-fail")
    assert "ufolint failed the UFO source." in msg


def test_check_required_fields(empty_ufo_font):
    check = CheckTester("com.daltonmaag/check/ufo_required_fields")

    ufo, _ = empty_ufo_font

    msg = assert_results_contain(check(ufo), FAIL, "missing-required-fields")
    assert "Required field(s) missing:" in msg

    ufo.info.unitsPerEm = 1000
    ufo.info.ascender = 800
    ufo.info.descender = -200
    ufo.info.xHeight = 500
    ufo.info.capHeight = 700
    ufo.info.familyName = "Test"

    assert_PASS(check(ufo))


def test_check_recommended_fields(empty_ufo_font):
    check = CheckTester("com.daltonmaag/check/ufo_recommended_fields")

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

    assert_PASS(check(ufo))


def test_check_unnecessary_fields(empty_ufo_font):
    check = CheckTester("com.daltonmaag/check/ufo_unnecessary_fields")

    ufo, _ = empty_ufo_font

    assert_PASS(check(ufo))

    ufo.info.openTypeNameUniqueID = "aaa"
    ufo.info.openTypeNameVersion = "1.000"
    ufo.info.postscriptUniqueID = -1
    ufo.info.year = 2018

    msg = assert_results_contain(check(ufo), WARN, "unnecessary-fields")
    assert "Unnecessary field(s) present:" in msg


def test_check_designspace_has_sources():
    """See if we can actually load the source files."""
    check = CheckTester("com.google.fonts/check/designspace_has_sources")

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_PASS(check(designspace))

    # TODO: FAIL, 'no-sources'


def test_check_designspace_has_default_master():
    """Ensure a default master is defined."""
    check = CheckTester("com.google.fonts/check/designspace_has_default_master")

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_PASS(check(designspace))

    # TODO: FAIL, 'not-found'


def test_check_designspace_has_consistent_glyphset():
    """Check consistency of glyphset in a designspace file."""
    check = CheckTester("com.google.fonts/check/designspace_has_consistent_glyphset")

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_results_contain(check(designspace), FAIL, "inconsistent-glyphset")

    # TODO: Fix it and ensure it passes the check


def test_check_designspace_has_consistent_codepoints():
    """Check codepoints consistency in a designspace file."""
    check = CheckTester("com.google.fonts/check/designspace_has_consistent_codepoints")

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_results_contain(check(designspace), FAIL, "inconsistent-codepoints")

    # TODO: Fix it and ensure it passes the check


def test_check_default_languagesystem_pass_without_features(empty_ufo_font):
    """Pass if the UFO source has no features."""
    check = CheckTester("com.thetypefounders/check/features_default_languagesystem")

    ufo, _ = empty_ufo_font

    assert_SKIP(check(ufo), "No features.fea file in font.")


def test_check_default_languagesystem_pass_with_empty_features(empty_ufo_font):
    """Pass if the UFO source has a feature file but it is empty."""
    check = CheckTester("com.thetypefounders/check/features_default_languagesystem")

    ufo, _ = empty_ufo_font

    ufo.features.text = ""

    assert_PASS(check(ufo))


def test_check_default_languagesystem_pass_with_features(empty_ufo_font):
    """Pass if the font has features and no default languagesystem statements."""
    check = CheckTester("com.thetypefounders/check/features_default_languagesystem")

    ufo, _ = empty_ufo_font

    ufo.features.text = "feature liga { sub f i by f_i; } liga;"

    assert_PASS(check(ufo))


def test_check_default_languagesystem_warn_without_default_languagesystem(
    empty_ufo_font,
):
    """Warn if `languagesystem DFLT dflt` is not present in the feature file,
    but other languagesystem statements are."""
    check = CheckTester("com.thetypefounders/check/features_default_languagesystem")

    ufo, _ = empty_ufo_font

    ufo.features.text = (
        "languagesystem latn dflt; feature liga { sub f i by f_i; } liga;"
    )

    assert_results_contain(check(ufo), WARN, "default-languagesystem")


def test_check_default_languagesystem_pass_with_default_languagesystem(empty_ufo_font):
    """Pass if `languagesystem DFLT dflt` is explicitly used in the features."""
    check = CheckTester("com.thetypefounders/check/features_default_languagesystem")

    ufo, _ = empty_ufo_font

    ufo.features.text = """languagesystem DFLT dflt;
languagesystem latn dflt;
feature liga { sub f i by f_i; } liga;"""

    assert_PASS(check(ufo))
