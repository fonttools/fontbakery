from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    TEST_FILE,
    MockFont,
    assert_PASS,
    assert_results_contain,
    portable_path,
)
from fontbakery.profiles import googlefonts as googlefonts_profile
from fontbakery.status import FAIL, FATAL, PASS, WARN


@check_id("opentype/italic_angle", profile=googlefonts_profile)
def test_check_italic_angle(check):
    """Checking post.italicAngle value."""

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    ttFont = TTFont(font)

    # italic-angle, style, fail_message
    test_cases = [
        [1, "Italic", FAIL, "positive"],
        [0, "Regular", PASS, None],  # This must PASS as it is a non-italic
        [-21, "ThinItalic", WARN, "over-20-degrees"],
        [-30, "ThinItalic", WARN, "over-20-degrees"],
        [-31, "ThinItalic", FAIL, "over-30-degrees"],
        [-91, "ThinItalic", FAIL, "over-90-degrees"],
        [0, "Italic", FAIL, "zero-italic"],
        [-1, "ExtraBold", FAIL, "non-zero-upright"],
    ]

    for value, style, expected_result, expected_msg in test_cases:
        ttFont["post"].italicAngle = value

        if expected_result != PASS:
            assert_results_contain(
                check(MockFont(file=font, ttFont=ttFont, style=style)),
                expected_result,
                expected_msg,
                f"with italic-angle:{value} style:{style}...",
            )
        else:
            assert_PASS(
                check(MockFont(file=font, ttFont=ttFont, style=style)),
                f"with italic-angle:{value} style:{style}...",
            )

    # Cairo, check left and right-leaning explicitly
    ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.rightslanted.ttf"))
    assert_PASS(check(MockFont(file=font, ttFont=ttFont, style="Italic")))
    ttFont["post"].italicAngle *= -1
    assert_results_contain(
        check(MockFont(file=font, ttFont=ttFont, style="Italic")), FAIL, "positive"
    )

    ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.leftslanted.ttf"))
    assert_PASS(check(MockFont(file=font, ttFont=ttFont, style="Italic")))
    ttFont["post"].italicAngle *= -1
    assert_results_contain(
        check(MockFont(file=font, ttFont=ttFont, style="Italic")), FAIL, "negative"
    )


@check_id("opentype/STAT/ital_axis", profile=googlefonts_profile)
def test_check_STAT_ital_axis__axes_values_and_flags(check):
    """Ensure 'ital' STAT axis is boolean value"""

    # PASS
    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    results = check(TTFont(font))
    results = [r for r in results if r.message.code == "wrong-ital-axis-value"]
    assert_PASS(results)

    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    results = check(TTFont(font))
    results = [r for r in results if r.message.code == "wrong-ital-axis-value"]
    assert_PASS(results)

    # FAIL
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].Value = 1
    assert_results_contain(check(ttFont), FAIL, "wrong-ital-axis-value")

    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].Flags = 0
    assert_results_contain(check(ttFont), FAIL, "wrong-ital-axis-flag")

    ttFonts = [
        TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")),
        TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")),
    ]
    ttFonts[1]["STAT"].table.AxisValueArray.AxisValue[6].Value = 0
    assert_results_contain(check(ttFonts), FAIL, "wrong-ital-axis-value")

    ttFonts = [
        TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")),
        TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")),
    ]
    ttFonts[1]["STAT"].table.AxisValueArray.AxisValue[6].Flags = 2
    assert_results_contain(check(ttFonts), FAIL, "wrong-ital-axis-flag")

    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].LinkedValue = None
    assert_results_contain(check(ttFont), FAIL, "wrong-ital-axis-linkedvalue")


@check_id("opentype/STAT/ital_axis", profile=googlefonts_profile)
def test_check_STAT_ital_axis(check):
    """Ensure VFs have 'ital' STAT axis."""

    ttFonts = [
        TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")),
        TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")),
    ]
    # Move last axis (ital) to the front
    ttFonts[1]["STAT"].table.DesignAxisRecord.Axis = [
        ttFonts[1]["STAT"].table.DesignAxisRecord.Axis[-1]
    ] + ttFonts[1]["STAT"].table.DesignAxisRecord.Axis[:-1]
    assert_results_contain(check(ttFonts), FAIL, "ital-axis-not-last")

    fonts = [
        TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"),
        TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"),
    ]
    assert_PASS(check(fonts))


@check_id("alt_caron", profile=googlefonts_profile)
def test_check_alt_caron(check):
    """Check accent of Lcaron, dcaron, lcaron, tcaron"""

    ttFont = TTFont(TEST_FILE("annie/AnnieUseYourTelescope-Regular.ttf"))
    assert_results_contain(
        check(ttFont), FAIL, "bad-mark"  # deviation from universal profile
    )

    assert_results_contain(check(ttFont), FAIL, "wrong-mark")

    ttFont = TTFont(TEST_FILE("cousine/Cousine-Bold.ttf"))
    assert_results_contain(check(ttFont), WARN, "decomposed-outline")

    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_PASS(check(ttFont))


@check_id("linegaps", profile=googlefonts_profile)
def test_check_linegaps(check):
    """Checking Vertical Metric Linegaps."""

    # Our reference Mada Regular is know to be bad here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # But just to be sure, we first explicitely set
    # the values we're checking for:
    ttFont["hhea"].lineGap = 1
    ttFont["OS/2"].sTypoLineGap = 0
    assert_results_contain(check(ttFont), FAIL, "hhea", "with non-zero hhea.lineGap...")

    # Then we run the check with a non-zero OS/2.sTypoLineGap:
    ttFont["hhea"].lineGap = 0
    ttFont["OS/2"].sTypoLineGap = 1
    assert_results_contain(
        check(ttFont), FAIL, "OS/2", "with non-zero OS/2.sTypoLineGap..."
    )

    # And finaly we fix it by making both values equal to zero:
    ttFont["hhea"].lineGap = 0
    ttFont["OS/2"].sTypoLineGap = 0
    assert_PASS(check(ttFont))

    # Confirm the check yields FAIL if the font doesn't have a required table
    del ttFont["OS/2"]
    assert_results_contain(check(ttFont), FAIL, "lacks-table")


@check_id("googlefonts/article/images", profile=googlefonts_profile)
def test_check_article_images(check):
    """Test article page visual content, length requirements, and image properties."""

    # Test case for missing ARTICLE
    family_directory = portable_path("data/test/missing_article")
    assert_results_contain(
        check(MockFont(family_directory=family_directory)), WARN, "lacks-article"
    )

    # Test case for ARTICLE not meeting length requirements
    family_directory = portable_path("data/test/short_article")
    assert_results_contain(
        check(MockFont(family_directory=family_directory)),
        WARN,
        "length-requirements-not-met",
    )

    # Test case for ARTICLE missing visual asset
    family_directory = portable_path("data/test/article_no_visual")
    assert_results_contain(
        check(MockFont(family_directory=family_directory)), WARN, "missing-visual-asset"
    )

    # Test case for ARTICLE with missing visual files
    family_directory = portable_path("data/test/article_missing_visual_file")
    assert_results_contain(
        check(MockFont(family_directory=family_directory)), FATAL, "missing-visual-file"
    )

    #    TODO:
    #    # Test case for image file exceeding size limit
    #    family_directory = portable_path("data/test/large_image_file")
    #    assert_results_contain(
    #        check(MockFont(family_directory=family_directory)), FAIL, "filesize"
    #    )

    #    TODO:
    #    # Test case for image file exceeding resolution limit
    #    family_directory = portable_path("data/test/large_resolution_image")
    #    assert_results_contain(
    #        check(MockFont(family_directory=family_directory)), FAIL, "image-too-large"
    #    )

    # Test case for ARTICLE meeting requirements
    family_directory = portable_path("data/test/article_valid")
    assert_PASS(check(MockFont(family_directory=family_directory)))
