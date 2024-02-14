import pytest

from fontTools.ttLib import TTFont

from fontbakery.status import WARN, FAIL, PASS
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
    MockFont,
)


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


def test_check_family_underline_thickness(mada_ttFonts):
    """Fonts have consistent underline thickness ?"""
    check = CheckTester("com.google.fonts/check/family/underline_thickness")

    # We start with our reference Mada font family,
    # which we know has the same value of post.underlineThickness
    # across all of its font files, based on our inspection
    # of the file contents using TTX.
    #
    # So the check should PASS in this case:
    assert_PASS(check(mada_ttFonts), "with a good family.")

    # Then we introduce the issue by setting a
    # different underlineThickness value in just
    # one of the font files:
    value = mada_ttFonts[0]["post"].underlineThickness
    incorrect_value = value + 1
    mada_ttFonts[0]["post"].underlineThickness = incorrect_value

    # And now re-running the check on the modified
    # family should result in a FAIL:
    assert_results_contain(
        check(mada_ttFonts),
        FAIL,
        "inconsistent-underline-thickness",
        "with an inconsistent family.",
    )


def test_check_post_table_version():
    """Font has acceptable post format version table?"""
    check = CheckTester("com.google.fonts/check/post_table_version")

    # create mock fonts for post format testing

    base_tt_font = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    #
    # post format 2 mock font test
    #
    mock_post_2 = base_tt_font

    mock_post_2["post"].formatType = 2
    mock_post_2.reader.file.name = "post 2 mock font"

    assert_PASS(check(mock_post_2), reason="with a post 2 mock font")

    #
    # post format 2.5 mock font test
    #
    mock_post_2_5 = base_tt_font

    mock_post_2_5["post"].formatType = 2.5
    mock_post_2_5.reader.file.name = "post 2.5 mock font"

    assert_results_contain(
        check(mock_post_2_5),
        FAIL,
        "post-table-version",
        "with a font that has post format 2.5 table",
    )

    #
    # post format 3 mock font test
    #
    mock_post_3 = base_tt_font

    mock_post_3["post"].formatType = 3
    mock_post_3.reader.file.name = "post 3  mock font"

    assert_results_contain(
        check(mock_post_3),
        WARN,
        "post-table-version",
        "with a font that has post format 3 table",
    )

    #
    # post format 4 mock font test
    #
    mock_post_4 = base_tt_font

    mock_post_4["post"].formatType = 4
    mock_post_4.reader.file.name = "post 4 mock font"

    assert_results_contain(
        check(mock_post_4),
        FAIL,
        "post-table-version",
        "with a font that has post format 4 table",
    )

    #
    # post format 2/3 OTF CFF mock font test
    #
    mock_cff_post_2 = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))

    mock_cff_post_2["post"].formatType = 2
    assert "CFF " in mock_cff_post_2
    assert "CFF2" not in mock_cff_post_2
    mock_cff_post_2.reader.file.name = "post 2 CFF mock font"

    assert_results_contain(
        check(mock_cff_post_2),
        FAIL,
        "post-table-version",
        "with a CFF font that has post format 2 table",
    )

    mock_cff_post_3 = mock_cff_post_2
    mock_cff_post_3["post"].formatType = 3

    assert_PASS(check(mock_cff_post_3), reason="with a post 3 CFF mock font.")


def test_check_italic_angle():
    """Checking post.italicAngle value."""
    check = CheckTester("com.google.fonts/check/italic_angle")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # italic-angle, style, fail_message
    test_cases = [
        [1, "Italic", WARN, "positive"],
        [0, "Regular", PASS, None],  # This must PASS as it is a non-italic
        [-21, "ThinItalic", WARN, "over-20-degrees"],
        [-30, "ThinItalic", WARN, "over-20-degrees"],
        [-31, "ThinItalic", WARN, "over-30-degrees"],
        [-91, "ThinItalic", FAIL, "over-90-degrees"],
        [0, "Italic", FAIL, "zero-italic"],
        [-1, "ExtraBold", FAIL, "non-zero-upright"],
    ]

    for value, style, expected_result, expected_msg in test_cases:
        ttFont["post"].italicAngle = value

        if expected_result != PASS:
            assert_results_contain(
                check(MockFont(ttFont=ttFont, style=style)),
                expected_result,
                expected_msg,
                f"with italic-angle:{value} style:{style}...",
            )
        else:
            assert_PASS(
                check(MockFont(ttFont=ttFont, style=style)),
                f"with italic-angle:{value} style:{style}...",
            )

    # Cairo, check left and right-leaning explicitly
    ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.rightslanted.ttf"))
    assert_PASS(check(MockFont(ttFont=ttFont, style="Italic")))
    ttFont["post"].italicAngle *= -1
    assert_results_contain(
        check(MockFont(ttFont=ttFont, style="Italic")), WARN, "positive"
    )

    ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.leftslanted.ttf"))
    assert_PASS(check(MockFont(ttFont=ttFont, style="Italic")))
    ttFont["post"].italicAngle *= -1
    assert_results_contain(
        check(MockFont(ttFont=ttFont, style="Italic")), WARN, "negative"
    )

    ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.rightslanted.ttf"))
    assert_PASS(check(MockFont(ttFont=ttFont, style="Italic")))
    ttFont["glyf"]["I"].endPtsOfContours = []
    ttFont["glyf"]["I"].coordinates = []
    ttFont["glyf"]["I"].flags = []
    ttFont["glyf"]["I"].numberOfContours = 0
    assert_results_contain(
        check(MockFont(ttFont=ttFont, style="Italic")), WARN, "empty-glyphs"
    )
