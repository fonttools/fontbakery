import os

import defcon
import pytest

from conftest import check_id
from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    assert_SKIP,
    TEST_FILE,
)


@pytest.fixture
def empty_ufo_font(tmpdir):
    ufo = defcon.Font()
    ufo.newGlyph("gname")
    ufo_path = str(tmpdir.join("empty_font.ufo"))
    ufo.save(ufo_path)
    return (ufo, ufo_path)


@check_id("ufolint")
def test_check_ufolint(check, empty_ufo_font):
    _, ufo_path = empty_ufo_font

    assert_PASS(check(ufo_path))

    os.remove(os.path.join(ufo_path, "metainfo.plist"))
    msg = assert_results_contain(check(ufo_path), FAIL, "ufolint-fail")
    assert "ufolint failed the UFO source." in msg


@check_id("ufo_required_fields")
def test_check_required_fields(check, empty_ufo_font):
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


@check_id("ufo_recommended_fields")
def test_check_recommended_fields(check, empty_ufo_font):
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


@check_id("ufo_unnecessary_fields")
def test_check_unnecessary_fields(check, empty_ufo_font):
    ufo, _ = empty_ufo_font

    assert_PASS(check(ufo))

    ufo.info.openTypeNameUniqueID = "aaa"
    ufo.info.openTypeNameVersion = "1.000"
    ufo.info.postscriptUniqueID = -1
    ufo.info.year = 2018

    msg = assert_results_contain(check(ufo), WARN, "unnecessary-fields")
    assert "Unnecessary field(s) present:" in msg


@check_id("designspace_has_sources")
def test_check_designspace_has_sources(check):
    """See if we can actually load the source files."""

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_PASS(check(designspace))

    # TODO: FAIL, 'no-sources'


@check_id("designspace_has_default_master")
def test_check_designspace_has_default_master(check):
    """Ensure a default master is defined."""

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_PASS(check(designspace))

    # TODO: FAIL, 'not-found'


@check_id("designspace_has_consistent_glyphset")
def test_check_designspace_has_consistent_glyphset(check):
    """Check consistency of glyphset in a designspace file."""

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_results_contain(check(designspace), FAIL, "inconsistent-glyphset")

    # TODO: Fix it and ensure it passes the check


@check_id("designspace_has_consistent_codepoints")
def test_check_designspace_has_consistent_codepoints(check):
    """Check codepoints consistency in a designspace file."""

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_results_contain(check(designspace), FAIL, "inconsistent-codepoints")

    # TODO: Fix it and ensure it passes the check


@check_id("ufo_features_default_languagesystem")
def test_check_default_languagesystem_pass_without_features(check, empty_ufo_font):
    """Pass if the UFO source has no features."""

    ufo, _ = empty_ufo_font

    assert_SKIP(check(ufo), "No features.fea file in font.")


@check_id("ufo_features_default_languagesystem")
def test_check_default_languagesystem_pass_with_empty_features(check, empty_ufo_font):
    """Pass if the UFO source has a feature file but it is empty."""

    ufo, _ = empty_ufo_font

    ufo.features.text = ""

    assert_PASS(check(ufo))


@check_id("ufo_features_default_languagesystem")
def test_check_default_languagesystem_pass_with_features(check, empty_ufo_font):
    """Pass if the font has features and no default languagesystem statements."""

    ufo, _ = empty_ufo_font

    ufo.features.text = "feature liga { sub f i by f_i; } liga;"

    assert_PASS(check(ufo))


@check_id("ufo_features_default_languagesystem")
def test_check_default_languagesystem_warn_without_default_languagesystem(
    check,
    empty_ufo_font,
):
    """Warn if `languagesystem DFLT dflt` is not present in the feature file,
    but other languagesystem statements are."""

    ufo, _ = empty_ufo_font

    ufo.features.text = (
        "languagesystem latn dflt; feature liga { sub f i by f_i; } liga;"
    )

    assert_results_contain(check(ufo), WARN, "default-languagesystem")


@check_id("ufo_features_default_languagesystem")
def test_check_default_languagesystem_pass_with_default_languagesystem(
    check, empty_ufo_font
):
    """Pass if `languagesystem DFLT dflt` is explicitly used in the features."""

    ufo, _ = empty_ufo_font

    ufo.features.text = """languagesystem DFLT dflt;
languagesystem latn dflt;
feature liga { sub f i by f_i; } liga;"""

    assert_PASS(check(ufo))


@check_id("ufo_consistent_curve_type")
def test_check_ufo_consistent_curve_type_check(check, empty_ufo_font) -> None:
    ufo, _ = empty_ufo_font

    cubic_contour = defcon.Contour()
    cubic_contour.appendPoint(defcon.Point((0, 0), "curve"))
    cubic_glyph = defcon.Glyph()
    cubic_glyph.appendContour(cubic_contour)

    quadratic_contour = defcon.Contour()
    quadratic_contour.appendPoint(defcon.Point((0, 0), "qcurve"))
    quadratic_glyph = defcon.Glyph()
    quadratic_glyph.appendContour(quadratic_contour)

    mixed_contour = defcon.Contour()
    mixed_contour.appendPoint(defcon.Point((0, 0), "curve"))
    mixed_contour.appendPoint(defcon.Point((1, 1), "qcurve"))
    mixed_glyph = defcon.Glyph()
    mixed_glyph.appendContour(mixed_contour)

    # Just cubics
    ufo.insertGlyph(cubic_glyph, "cubic")
    assert_PASS(check(ufo))
    del ufo["cubic"]

    # Just quadratics
    ufo.insertGlyph(quadratic_glyph, "quadratic")
    assert_PASS(check(ufo))

    # Cubics & quadratics, separate glyphs
    ufo.insertGlyph(cubic_glyph, "cubic")
    assert_results_contain(check(ufo), WARN, "both-cubic-and-quadratic")

    # Cubics & quadratics, all in one glyph
    ufo.insertGlyph(mixed_glyph, "mixed")
    assert_results_contain(check(ufo), WARN, "mixed-glyphs")


@check_id("ufo_no_open_corners")
def test_check_ufo_no_open_corners(check) -> None:
    """Ensure the check identifies open corners correctly"""

    ufo = defcon.Font(TEST_FILE("test.ufo"))

    assert_results_contain(check(ufo), FAIL, "open-corners-found")

    # Remove glyph with open corners
    del ufo["square"]

    assert_PASS(check(ufo))


@check_id("designspace_has_consistent_groups")
def test_check_designspace_has_consistent_groups(check, tmpdir) -> None:
    """Ensure the check identifies mismatched groups correctly"""

    designspace_path = TEST_FILE("mismatched_groups/Stupid Font.designspace")

    assert_results_contain(check(designspace_path), WARN, "mismatched-kerning-groups")
