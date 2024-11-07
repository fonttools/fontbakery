from fontTools.ttLib import TTFont
import pytest

from conftest import check_id
from fontbakery.status import FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    TEST_FILE,
)


@pytest.fixture
def montserrat_ttFonts():
    paths = [
        TEST_FILE("montserrat/Montserrat-Black.ttf"),
        TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Bold.ttf"),
        TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Italic.ttf"),
        TEST_FILE("montserrat/Montserrat-Light.ttf"),
        TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Medium.ttf"),
        TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Regular.ttf"),
        TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
        TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Thin.ttf"),
        TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"),
    ]
    return [TTFont(path) for path in paths]


@pytest.fixture
def mada_ttFonts():
    paths = [
        TEST_FILE("mada/Mada-Regular.ttf"),
        TEST_FILE("mada/Mada-Black.ttf"),
        TEST_FILE("mada/Mada-Bold.ttf"),
        TEST_FILE("mada/Mada-ExtraLight.ttf"),
        TEST_FILE("mada/Mada-Light.ttf"),
        TEST_FILE("mada/Mada-Medium.ttf"),
        TEST_FILE("mada/Mada-SemiBold.ttf"),
    ]
    return [TTFont(path) for path in paths]


@check_id("family/win_ascent_and_descent")
def test_check_family_win_ascent_and_descent(check, mada_ttFonts):
    """Checking OS/2 usWinAscent & usWinDescent."""

    # Mada Regular is know to be bad
    # single font input
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    message = assert_results_contain(check(ttFont), FAIL, "ascent")
    assert message == (
        "OS/2.usWinAscent value should be"
        " equal or greater than 880, but got 776 instead"
    )

    # multi font input
    check_results = check(mada_ttFonts)
    message = assert_results_contain([check_results[0]], FAIL, "ascent")
    assert message == (
        "OS/2.usWinAscent value should be"
        " equal or greater than 918, but got 776 instead"
    )
    message = assert_results_contain([check_results[1]], FAIL, "descent")
    assert message == (
        "OS/2.usWinDescent value should be"
        " equal or greater than 406, but got 322 instead"
    )

    # Fix usWinAscent
    ttFont["OS/2"].usWinAscent = 880
    assert_PASS(check(ttFont))

    # Make usWinAscent too large
    ttFont["OS/2"].usWinAscent = 880 * 2 + 1
    message = assert_results_contain(check(ttFont), FAIL, "ascent")
    assert message == (
        "OS/2.usWinAscent value 1761 is too large. "
        "It should be less than double the yMax. Current yMax value is 880"
    )

    # Make usWinDescent too large
    ttFont["OS/2"].usWinDescent = 292 * 2 + 1
    message = assert_results_contain(check(ttFont), FAIL, "descent")
    assert message == (
        "OS/2.usWinDescent value 585 is too large."
        " It should be less than double the yMin. Current absolute yMin value is 292"
    )

    # Delete OS/2 table
    del ttFont["OS/2"]
    message = assert_results_contain(check(ttFont), FAIL, "lacks-OS/2")
    assert message == "Font file lacks OS/2 table"


@check_id("os2_metrics_match_hhea")
def test_check_os2_metrics_match_hhea(check):
    """Checking OS/2 Metrics match hhea Metrics."""

    # Our reference Mada Regular is know to be faulty here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_results_contain(
        check(ttFont),
        FAIL,
        "lineGap",
        "OS/2 sTypoLineGap (100) and hhea lineGap (96) must be equal.",
    )

    # Our reference Mada Black is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Black.ttf"))

    assert_PASS(check(ttFont), "with a good font...")

    # Now we break it:
    correct = ttFont["hhea"].ascent
    ttFont["OS/2"].sTypoAscender = correct + 1
    assert_results_contain(
        check(ttFont), FAIL, "ascender", "with a bad OS/2.sTypoAscender font..."
    )

    # Restore good value:
    ttFont["OS/2"].sTypoAscender = correct

    # And break it again, now on sTypoDescender value:
    correct = ttFont["hhea"].descent
    ttFont["OS/2"].sTypoDescender = correct + 1
    assert_results_contain(
        check(ttFont), FAIL, "descender", "with a bad OS/2.sTypoDescender font..."
    )

    # Delete OS/2 table
    del ttFont["OS/2"]
    message = assert_results_contain(check(ttFont), FAIL, "lacks-OS/2")
    assert message == "Mada-Black.ttf lacks a 'OS/2' table."


@check_id("family/vertical_metrics")
def test_check_family_vertical_metrics(check, montserrat_ttFonts):
    """Each font in a family must have the same set of vertical metrics values."""

    assert_PASS(check(montserrat_ttFonts), "with multiple good fonts...")

    montserrat_ttFonts[0]["OS/2"].sTypoAscender = 3333
    montserrat_ttFonts[1]["OS/2"].usWinAscent = 4444
    results = check(montserrat_ttFonts)
    msg = assert_results_contain([results[0]], FAIL, "sTypoAscender-mismatch")
    assert "Montserrat Black: 3333" in msg
    msg = assert_results_contain([results[1]], FAIL, "usWinAscent-mismatch")
    assert "Montserrat Black Italic: 4444" in msg

    del montserrat_ttFonts[2]["OS/2"]
    del montserrat_ttFonts[3]["hhea"]
    results = check(montserrat_ttFonts)
    msg = assert_results_contain([results[0]], FAIL, "lacks-OS/2")
    assert msg == "Montserrat-Bold.ttf lacks an 'OS/2' table."
    msg = assert_results_contain([results[1]], FAIL, "lacks-hhea")
    assert msg == "Montserrat-BoldItalic.ttf lacks a 'hhea' table."


@check_id("caps_vertically_centered")
def test_check_caps_vertically_centered(check):
    """Check if uppercase glyphs are vertically centered."""

    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("cjk/SourceHanSans-Regular.otf"))
    assert_SKIP(check(ttFont))

    # FIXME: review this test-case
    # ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.leftslanted.ttf"))
    # assert_results_contain(check(ttFont), WARN, "vertical-metrics-not-centered")


@check_id("linegaps")
def test_check_linegaps(check):
    """Checking Vertical Metric Linegaps."""

    # Our reference Mada Regular is know to be bad here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # But just to be sure, we first explicitely set
    # the values we're checking for:
    ttFont["hhea"].lineGap = 1
    ttFont["OS/2"].sTypoLineGap = 0
    assert_results_contain(check(ttFont), WARN, "hhea", "with non-zero hhea.lineGap...")

    # Then we run the check with a non-zero OS/2.sTypoLineGap:
    ttFont["hhea"].lineGap = 0
    ttFont["OS/2"].sTypoLineGap = 1
    assert_results_contain(
        check(ttFont), WARN, "OS/2", "with non-zero OS/2.sTypoLineGap..."
    )

    # And finaly we fix it by making both values equal to zero:
    ttFont["hhea"].lineGap = 0
    ttFont["OS/2"].sTypoLineGap = 0
    assert_PASS(check(ttFont))

    # Confirm the check yields FAIL if the font doesn't have a required table
    del ttFont["OS/2"]
    assert_results_contain(check(ttFont), FAIL, "lacks-table")
