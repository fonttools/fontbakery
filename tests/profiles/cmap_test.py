import pytest
from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.checkrunner import DEBUG, INFO, WARN, ERROR, SKIP, PASS, FAIL
from fontbakery.profiles import opentype as opentype_profile

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

mada_fonts = [
    TEST_FILE("mada/Mada-Black.ttf"),
    TEST_FILE("mada/Mada-ExtraLight.ttf"),
    TEST_FILE("mada/Mada-Medium.ttf"),
    TEST_FILE("mada/Mada-SemiBold.ttf"),
    TEST_FILE("mada/Mada-Bold.ttf"),
    TEST_FILE("mada/Mada-Light.ttf"),
    TEST_FILE("mada/Mada-Regular.ttf"),
]


@pytest.fixture
def mada_ttFonts():
    return [TTFont(path) for path in mada_fonts]


def test_check_family_equal_unicode_encodings(mada_ttFonts):
    """Fonts have equal unicode encodings ?"""
    check = CheckTester(
        opentype_profile, "com.google.fonts/check/family/equal_unicode_encodings"
    )

    from fontbakery.constants import WindowsEncodingID

    # our reference Mada family is know to be good here.
    assert_PASS(check(mada_ttFonts), "with good family.")

    bad_ttFonts = mada_ttFonts
    # introduce mismatching encodings into the first 2 font files:
    for i, encoding in enumerate(
        [WindowsEncodingID.SYMBOL, WindowsEncodingID.UNICODE_BMP]
    ):
        for table in bad_ttFonts[i]["cmap"].tables:
            if table.format == 4:
                table.platEncID = encoding

    assert_results_contain(
        check(bad_ttFonts),
        FAIL,
        "mismatch",
        "with fonts that diverge on unicode encoding.",
    )
