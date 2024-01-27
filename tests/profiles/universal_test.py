import os
import io
from unittest.mock import patch, MagicMock

from fontTools.ttLib import TTFont
import pytest
import requests

from fontbakery.status import INFO, WARN, FAIL, SKIP
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.profiles import universal as universal_profile
from fontbakery.profiles.shared_conditions import style
from fontbakery.profiles.universal import is_up_to_date
from fontbakery.utils import glyph_has_ink


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


cabin_fonts = [
    TEST_FILE("cabin/Cabin-BoldItalic.ttf"),
    TEST_FILE("cabin/Cabin-Bold.ttf"),
    TEST_FILE("cabin/Cabin-Italic.ttf"),
    TEST_FILE("cabin/Cabin-MediumItalic.ttf"),
    TEST_FILE("cabin/Cabin-Medium.ttf"),
    TEST_FILE("cabin/Cabin-Regular.ttf"),
    TEST_FILE("cabin/Cabin-SemiBoldItalic.ttf"),
    TEST_FILE("cabin/Cabin-SemiBold.ttf"),
]

cabin_condensed_fonts = [
    TEST_FILE("cabincondensed/CabinCondensed-Regular.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-Medium.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-Bold.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-SemiBold.ttf"),
]


@pytest.fixture
def cabin_ttFonts():
    return [TTFont(path) for path in cabin_fonts]


@pytest.fixture
def cabin_condensed_ttFonts():
    return [TTFont(path) for path in cabin_condensed_fonts]


def test_style_condition():
    # VFs
    assert (
        style(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")) == "Regular"
    )
    assert (
        style(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
        == "Italic"
    )
    assert (
        style(TEST_FILE("shantell/ShantellSans-FakeVFBold[BNCE,INFM,SPAC,wght].ttf"))
        == "Bold"
    )
    assert (
        style(
            TEST_FILE("shantell/ShantellSans-FakeVFBoldItalic[BNCE,INFM,SPAC,wght].ttf")
        )
        == "BoldItalic"
    )
    # Statics
    assert (
        style(TEST_FILE("bad_fonts/style_linking_issues/NotoSans-Regular.ttf"))
        == "Regular"
    )
    assert (
        style(TEST_FILE("bad_fonts/style_linking_issues/NotoSans-Italic.ttf"))
        == "Italic"
    )
    assert (
        style(TEST_FILE("bad_fonts/style_linking_issues/NotoSans-Bold.ttf")) == "Bold"
    )
    assert (
        style(TEST_FILE("bad_fonts/style_linking_issues/NotoSans-BoldItalic.ttf"))
        == "BoldItalic"
    )
    # Badly named statics, fail them
    assert style(TEST_FILE("bad_fonts/bad_stylenames/NotoSans-Fat.ttf")) is None
    assert style(TEST_FILE("bad_fonts/bad_stylenames/NotoSans.ttf")) is None


def test_check_valid_glyphnames():
    """Glyph names are all valid?"""
    check = CheckTester(universal_profile, "com.google.fonts/check/valid_glyphnames")
    pass_msg = "Glyph names are all valid."

    # We start with a good font file:
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    message = assert_PASS(check(ttFont))
    assert message == pass_msg

    # There used to be a 31 char max-length limit.
    # This was considered good:
    ttFont.glyphOrder[2] = "a" * 31
    message = assert_PASS(check(ttFont))
    assert message == pass_msg

    # And this was considered bad:
    legacy_too_long = "a" * 32
    ttFont.glyphOrder[2] = legacy_too_long
    message = assert_results_contain(check(ttFont), WARN, "legacy-long-names")
    assert legacy_too_long in message

    # Nowadays, it seems most implementations can deal with
    # up to 63 char glyph names:
    good_name1 = "b" * 63
    # colr font may have a color layer in .notdef so allow these layers
    good_name2 = ".notdef.color0"
    bad_name1 = "a" * 64
    bad_name2 = "3cents"
    bad_name3 = ".threecents"
    ttFont.glyphOrder[2] = bad_name1
    ttFont.glyphOrder[3] = bad_name2
    ttFont.glyphOrder[4] = bad_name3
    ttFont.glyphOrder[5] = good_name1
    ttFont.glyphOrder[6] = good_name2
    message = assert_results_contain(check(ttFont), FAIL, "found-invalid-names")
    assert good_name1 not in message
    assert good_name2 not in message
    assert bad_name1 in message
    assert bad_name2 in message
    assert bad_name3 in message

    # TrueType fonts with a format 3 post table contain
    # no glyph names, so the check must be SKIP'd in that case.
    #
    # Upgrade to post format 3 and roundtrip data to update TTF object.
    ttf_skip_msg = "TrueType fonts with a format 3 post table"
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont["post"].formatType = 3
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    message = assert_SKIP(check(ttFont))
    assert ttf_skip_msg in message

    # Also test with CFF...
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    message = assert_PASS(check(ttFont))
    assert message == pass_msg

    # ... and CFF2 fonts
    cff2_skip_msg = "OpenType-CFF2 fonts with a format 3 post table"
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))
    message = assert_SKIP(check(ttFont))
    assert cff2_skip_msg in message


def test_check_unique_glyphnames():
    """Font contains unique glyph names?"""
    check = CheckTester(universal_profile, "com.google.fonts/check/unique_glyphnames")
    pass_msg = "Glyph names are all unique."

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    message = assert_PASS(check(ttFont))
    assert message == pass_msg

    # Fonttools renames duplicate glyphs with #1, #2, ... on load.
    # Code snippet from https://github.com/fonttools/fonttools/issues/149
    glyph_names = ttFont.getGlyphOrder()
    glyph_names[2] = glyph_names[3]

    # Load again, we changed the font directly.
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont.setGlyphOrder(glyph_names)
    # Just access the data to make fonttools generate it.
    ttFont["post"]  # pylint:disable=pointless-statement
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    message = assert_results_contain(check(ttFont), FAIL, "duplicated-glyph-names")
    assert "space" in message

    # Upgrade to post format 3 and roundtrip data to update TTF object.
    ttf_skip_msg = "TrueType fonts with a format 3 post table"
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont.setGlyphOrder(glyph_names)
    ttFont["post"].formatType = 3
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    message = assert_SKIP(check(ttFont))
    assert ttf_skip_msg in message

    # Also test with CFF...
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    message = assert_PASS(check(ttFont))
    assert message == pass_msg

    # ... and CFF2 fonts
    cff2_skip_msg = "OpenType-CFF2 fonts with a format 3 post table"
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))
    message = assert_SKIP(check(ttFont))
    assert cff2_skip_msg in message


def test_check_ttx_roundtrip():
    """Checking with fontTools.ttx"""
    check = CheckTester(universal_profile, "com.google.fonts/check/ttx_roundtrip")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font))

    # TODO: Can anyone show us a font file that fails ttx roundtripping?!
    #
    # font = TEST_FILE("...")
    # assert_results_contain(check(font),
    #                        FAIL, None) # FIXME: This needs a message keyword


def test_check_name_trailing_spaces():
    """Name table entries must not have trailing spaces."""
    check = CheckTester(
        universal_profile, "com.google.fonts/check/name/trailing_spaces"
    )

    # Our reference Cabin Regular is known to be good:
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    for i, entry in enumerate(ttFont["name"].names):
        good_string = ttFont["name"].names[i].toUnicode()
        bad_string = good_string + " "
        ttFont["name"].names[i].string = bad_string.encode(entry.getEncoding())
        assert_results_contain(
            check(ttFont),
            FAIL,
            "trailing-space",
            f'with a bad name table entry ({i}: "{bad_string}")...',
        )

        # restore good entry before moving to the next one:
        ttFont["name"].names[i].string = good_string.encode(entry.getEncoding())


def test_check_family_single_directory():
    """Fonts are all in the same directory."""
    check = CheckTester(
        universal_profile, "com.google.fonts/check/family/single_directory"
    )
    same_dir = [
        TEST_FILE("cabin/Cabin-Thin.ttf"),
        TEST_FILE("cabin/Cabin-ExtraLight.ttf"),
    ]
    multiple_dirs = [
        TEST_FILE("mada/Mada-Regular.ttf"),
        TEST_FILE("cabin/Cabin-ExtraLight.ttf"),
    ]

    assert_PASS(check(same_dir), f"with same dir: {same_dir}")

    assert_results_contain(
        check(multiple_dirs),
        FAIL,
        "single-directory",
        f"with multiple dirs: {multiple_dirs}",
    )


def test_check_ots():
    """Checking with ots-sanitize."""
    check = CheckTester(universal_profile, "com.google.fonts/check/ots")

    fine_font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(fine_font))

    warn_font = TEST_FILE("bad_fonts/ots/bad_post_version.otf")
    message = assert_results_contain(check(warn_font), WARN, "ots-sanitize-warn")
    assert (
        "WARNING: post: Only version supported for fonts with CFF table is"
        " 0x00030000 not 0x20000" in message
    )

    bad_font = TEST_FILE("bad_fonts/ots/no_glyph_data.ttf")
    message = assert_results_contain(check(bad_font), FAIL, "ots-sanitize-error")
    assert "ERROR: no supported glyph data table(s) present" in message
    assert "Failed to sanitize file!" in message


@pytest.mark.parametrize(
    "installed, latest, result",
    [
        # True when installed >= latest
        ("0.5.0", "0.5.0", True),
        ("0.5.1", "0.5.0", True),
        ("0.5.1", "0.5.0.post2", True),
        ("2.0.0", "1.5.1", True),
        ("0.8.10", "0.8.9", True),
        ("0.5.2.dev73+g8c9ebc0.d20181023", "0.5.1", True),
        ("0.8.10.dev1+g666b3425", "0.8.9", True),
        ("0.8.10.dev2+gfa9260bf", "0.8.9.post2", True),
        ("0.8.10a9", "0.8.9", True),
        ("0.8.10rc1.dev3+g494879af.d20220825", "0.8.9", True),
        # False when installed < latest
        ("0.4.1", "0.5.0", False),
        ("0.3.4", "0.3.5", False),
        ("1.0.0", "1.0.1", False),
        ("0.8.9", "0.8.10", False),
        ("0.5.0", "0.5.0.post2", False),
        ("0.8.9.dev1+g666b3425", "0.8.9.post2", False),
        ("0.5.2.dev73+g8c9ebc0.d20181023", "0.5.2", False),
        ("0.5.2.dev73+g8c9ebc0.d20181023", "0.5.3", False),
        ("0.8.10rc0", "0.8.10", False),
        ("0.8.10rc0", "0.8.10.post", False),
        ("0.8.10rc1.dev3+g494879af.d20220825", "0.8.10", False),
        ("0.8.10rc1.dev3+g494879af.d20220825", "0.8.10.post", False),
    ],
)
def test_is_up_to_date(installed, latest, result):
    assert is_up_to_date(installed, latest) is result


class MockDistribution:
    """Helper class to mock pip-api's Distribution class."""

    def __init__(self, version: str):
        self.name = "fontbakery"
        self.version = version

    def __repr__(self):
        return f"<Distribution(name='{self.name}', version='{self.version}')>"


# We don't want to make an actual GET request to PyPI.org, so we'll mock it.
# We'll also mock pip-api's 'installed_distributions' method.
@patch("pip_api.installed_distributions")
@patch("requests.get")
def test_check_fontbakery_version(mock_get, mock_installed):
    """Check if FontBakery is up-to-date"""
    check = CheckTester(universal_profile, "com.google.fonts/check/fontbakery_version")

    # Any of the test fonts can be used here.
    # The check requires a 'font' argument but it doesn't do anything with it.
    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    mock_response = MagicMock()
    mock_response.status_code = 200

    # Test the case of installed version being the same as PyPI's version.
    latest_ver = installed_ver = "0.1.0"
    mock_response.json.return_value = {"info": {"version": latest_ver}}
    mock_get.return_value = mock_response
    mock_installed.return_value = {"fontbakery": MockDistribution(installed_ver)}
    msg = assert_PASS(check(font))
    assert msg == "FontBakery is up-to-date."

    # Test the case of installed version being newer than PyPI's version.
    installed_ver = "0.1.1"
    mock_installed.return_value = {"fontbakery": MockDistribution(installed_ver)}
    msg = assert_PASS(check(font))
    assert msg == "FontBakery is up-to-date."

    # Test the case of installed version being older than PyPI's version.
    installed_ver = "0.0.1"
    mock_installed.return_value = {"fontbakery": MockDistribution(installed_ver)}
    msg = assert_results_contain(check(font), FAIL, "outdated-fontbakery")
    assert (
        f"Current FontBakery version is {installed_ver},"
        f" while a newer {latest_ver} is already available."
    ) in msg

    # Test the case of an unsuccessful response to the GET request.
    mock_response.status_code = 500
    mock_response.content = "500 Internal Server Error"
    msg = assert_results_contain(check(font), FAIL, "unsuccessful-request-500")
    assert "Request to PyPI.org was not successful" in msg

    # Test the case of the GET request failing due to a connection error.
    mock_get.side_effect = requests.exceptions.ConnectionError
    msg = assert_results_contain(check(font), FAIL, "connection-error")
    assert "Request to PyPI.org failed with this message" in msg


def test_check_fontbakery_version_live_apis():
    """Check if FontBakery is up-to-date. (No API-mocking edition)"""
    check = CheckTester(universal_profile, "com.google.fonts/check/fontbakery_version")

    # Any of the test fonts can be used here.
    # The check requires a 'font' argument but it doesn't do anything with it.
    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    # The check will make an actual request to PyPI.org,
    # and will query 'pip' to determine which version of 'fontbakery' is installed.
    # The check should PASS.
    msg = assert_PASS(check(font))
    assert msg == "FontBakery is up-to-date."


def test_check_mandatory_glyphs():
    """Font contains the first few mandatory glyphs (.null or NULL, CR and space)?"""
    from fontTools import subset

    check = CheckTester(universal_profile, "com.google.fonts/check/mandatory_glyphs")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert assert_PASS(check(ttFont)) == "OK"

    options = subset.Options()
    options.glyph_names = True  # Preserve glyph names
    # By default, the subsetter keeps the '.notdef' glyph but removes its outlines
    subsetter = subset.Subsetter(options)
    subsetter.populate(text="mn")  # Arbitrarily remove everything except 'm' and 'n'
    subsetter.subset(ttFont)
    message = assert_results_contain(check(ttFont), FAIL, "notdef-is-blank")
    assert message == "The '.notdef' glyph should contain a drawing, but it is blank."

    options.notdef_glyph = False  # Drop '.notdef' glyph
    subsetter = subset.Subsetter(options)
    subsetter.populate(text="mn")
    subsetter.subset(ttFont)
    message = assert_results_contain(check(ttFont), WARN, "notdef-not-found")
    assert message == "Font should contain the '.notdef' glyph."

    # Change the glyph name from 'n' to '.notdef'
    # (Must reload the font here since we already decompiled the glyf table)
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont.glyphOrder = ["m", ".notdef"]
    for subtable in ttFont["cmap"].tables:
        if subtable.isUnicode():
            subtable.cmap[110] = ".notdef"
            if 0 in subtable.cmap:
                del subtable.cmap[0]
    results = check(ttFont)
    message = assert_results_contain([results[0]], WARN, "notdef-not-first")
    assert message == "The '.notdef' should be the font's first glyph."

    message = assert_results_contain([results[1]], WARN, "notdef-has-codepoint")
    assert message == (
        "The '.notdef' glyph should not have a Unicode codepoint value assigned,"
        " but has 0x006E."
    )


def _remove_cmap_entry(font, cp):
    """Helper method that removes a codepoint entry from all the tables in cmap."""
    for subtable in font["cmap"].tables:
        subtable.cmap.pop(cp, None)


def test_check_whitespace_glyphs():
    """Font contains glyphs for whitespace characters?"""
    check = CheckTester(universal_profile, "com.google.fonts/check/whitespace_glyphs")

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # We remove the nbsp char (0x00A0)
    _remove_cmap_entry(ttFont, 0x00A0)

    # And make sure the problem is detected:
    assert_results_contain(
        check(ttFont),
        FAIL,
        "missing-whitespace-glyph-0x00A0",
        "with a font lacking a nbsp (0x00A0)...",
    )

    # restore original Mada Regular font:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # And finally do the same with the space character (0x0020):
    _remove_cmap_entry(ttFont, 0x0020)
    assert_results_contain(
        check(ttFont),
        FAIL,
        "missing-whitespace-glyph-0x0020",
        "with a font lacking a space (0x0020)...",
    )


def test_check_whitespace_glyphnames():
    """Font has **proper** whitespace glyph names?"""
    check = CheckTester(
        universal_profile, "com.google.fonts/check/whitespace_glyphnames"
    )

    def editCmap(font, cp, name):
        """Corrupt the cmap by changing the glyph name
        for a given code point.
        """
        for subtable in font["cmap"].tables:
            if subtable.isUnicode():
                # Copy the map
                subtable.cmap = subtable.cmap.copy()
                # edit it
                subtable.cmap[cp] = name

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    value = ttFont["post"].formatType
    ttFont["post"].formatType = 3.0
    assert_SKIP(check(ttFont), "with post.formatType == 3.0 ...")

    # restore good value:
    ttFont["post"].formatType = value

    _remove_cmap_entry(ttFont, 0x0020)
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not missing_whitespace_chars" in msg.message

    # restore the original font object in preparation for the next test-case:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    _remove_cmap_entry(ttFont, 0x00A0)
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not missing_whitespace_chars" in msg.message

    # restore the original font object in preparation for the next test-case:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # See https://github.com/fonttools/fontbakery/issues/2624
    # nbsp is not Adobe Glyph List compliant.
    editCmap(ttFont, 0x00A0, "nbsp")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "non-compliant-00a0",
        'with not AGL-compliant glyph name "nbsp" for char 0x00A0...',
    )

    editCmap(ttFont, 0x00A0, "nbspace")
    assert_results_contain(
        check(ttFont), WARN, "not-recommended-00a0", 'for naming 0x00A0 "nbspace"...'
    )

    editCmap(ttFont, 0x0020, "foo")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "non-compliant-0020",
        'with not AGL-compliant glyph name "foo" for char 0x0020...',
    )

    editCmap(ttFont, 0x0020, "uni0020")
    assert_results_contain(
        check(ttFont), WARN, "not-recommended-0020", 'for naming 0x0020 "uni0020"...'
    )

    editCmap(ttFont, 0x0020, "space")
    editCmap(ttFont, 0x00A0, "uni00A0")
    assert assert_PASS(check(ttFont)) == (
        "Font has **AGL recommended** names for whitespace glyphs."
    )


def test_check_whitespace_ink():
    """Whitespace glyphs have ink?"""
    check = CheckTester(universal_profile, "com.google.fonts/check/whitespace_ink")

    test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(test_font))

    test_font["cmap"].tables[0].cmap[0x1680] = "a"
    assert_PASS(check(test_font), "because Ogham space mark does have ink.")

    test_font["cmap"].tables[0].cmap[0x0020] = "uni1E17"
    assert_results_contain(
        check(test_font),
        FAIL,
        "has-ink",
        "for whitespace character having composites (with ink).",
    )

    test_font["cmap"].tables[0].cmap[0x0020] = "scedilla"
    assert_results_contain(
        check(test_font),
        FAIL,
        "has-ink",
        "for whitespace character having outlines (with ink).",
    )

    import fontTools.pens.ttGlyphPen

    pen = fontTools.pens.ttGlyphPen.TTGlyphPen(test_font.getGlyphSet())
    pen.addComponent("space", (1, 0, 0, 1, 0, 0))
    test_font["glyf"].glyphs["uni200B"] = pen.glyph()
    assert_results_contain(
        check(test_font),
        FAIL,
        "has-ink",  # should we give is a separate keyword? This looks wrong.
        "for whitespace character having composites (without ink).",
    )


def test_check_legacy_accents():
    """Check that legacy accents aren't used in composite glyphs."""
    check = CheckTester(universal_profile, "com.google.fonts/check/legacy_accents")

    test_font = TTFont(TEST_FILE("montserrat/Montserrat-Regular.ttf"))
    assert_PASS(check(test_font))

    test_font = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_results_contain(
        check(test_font),
        FAIL,
        "legacy-accents-gdef",
        "for legacy accents being defined in GDEF as marks.",
    )

    test_font = TTFont(TEST_FILE("lugrasimo/Lugrasimo-Regular.ttf"))
    assert_results_contain(
        check(test_font),
        WARN,
        "legacy-accents-component",
        "for legacy accents being used in composites.",
    )
    assert_results_contain(
        check(test_font),
        FAIL,
        "legacy-accents-width",
        "for legacy accents having zero width.",
    )


def test_check_required_tables():
    """Font contains all required tables ?"""
    check = CheckTester(universal_profile, "com.google.fonts/check/required_tables")

    REQUIRED_TABLES = ["cmap", "head", "hhea", "hmtx", "maxp", "name", "OS/2", "post"]

    OPTIONAL_TABLES = [
        "cvt ",
        "fpgm",
        "loca",
        "prep",
        "VORG",
        "EBDT",
        "EBLC",
        "EBSC",
        "BASE",
        "GPOS",
        "GSUB",
        "JSTF",
        "gasp",
        "hdmx",
        "LTSH",
        "PCLT",
        "VDMX",
        "vhea",
        "vmtx",
        "kern",
    ]

    # Valid reference fonts, one for each format.
    # TrueType: Mada Regular
    # OpenType-CFF: SourceSansPro-Black
    # OpenType-CFF2: SourceSansVariable-Italic
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    cff_font = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Black.otf"))
    cff2_font = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.otf"))

    # The TrueType font contains all required tables, so it must PASS the check.
    msg = assert_PASS(check(ttFont), "with a good font...")
    assert msg == "Font contains all required tables."

    # Here we confirm that the check also yields INFO with
    # a list of table tags specific to the font.
    msg = assert_results_contain(check(ttFont), INFO, "optional-tables")
    for tag in ("loca", "GPOS", "GSUB"):
        assert tag in msg

    # The OpenType-CFF font contains all required tables, so it must PASS the check.
    msg = assert_PASS(check(cff_font), "with a good font...")
    assert msg == "Font contains all required tables."

    # Here we confirm that the check also yields INFO with
    # a list of table tags specific to the OpenType-CFF font.
    msg = assert_results_contain(check(cff_font), INFO, "optional-tables")
    for tag in ("BASE", "GPOS", "GSUB"):
        assert tag in msg

    # The font must also contain the table that holds the outlines, "CFF " in this case.
    del cff_font.reader.tables["CFF "]
    msg = assert_results_contain(check(cff_font), FAIL, "required-tables")
    assert "CFF " in msg

    # The OpenType-CFF2 font contains all required tables, so it must PASS the check.
    msg = assert_PASS(check(cff2_font), "with a good font...")
    assert msg == "Font contains all required tables."

    # Here we confirm that the check also yields INFO with
    # a list of table tags specific to the OpenType-CFF2 font.
    msg = assert_results_contain(check(cff2_font), INFO, "optional-tables")
    for tag in ("BASE", "GPOS", "GSUB"):
        assert tag in msg

    # The font must also contain the table that holds the outlines, "CFF2" in this case.
    del cff2_font.reader.tables["CFF2"]
    msg = assert_results_contain(check(cff2_font), FAIL, "required-tables")
    assert "CFF2" in msg

    # The OT-CFF2 font is variable, so a "STAT" table is also required.
    # Here we confirm that the check fails when the "STAT" table is removed.
    del cff2_font.reader.tables["STAT"]
    msg = assert_results_contain(check(cff2_font), FAIL, "required-tables")
    assert "STAT" in msg

    # Here we also remove the "fvar" table from the OT-CFF2 font.
    # Without an "fvar" table the font is validated as if it were a stactic font,
    # leading the check to FAIL with a message about the lack of a "CFF " table.
    del cff2_font.reader.tables["fvar"]
    msg = assert_results_contain(check(cff2_font), FAIL, "required-tables")
    assert "CFF " in msg

    # Now we test the special cases for variable fonts:
    #
    # Note: A TTF with an fvar table but no STAT table
    #       is probably a GX font. For now we're OK with
    #       rejecting those by emitting a FAIL in this case.
    #
    # TODO: Maybe we could someday emit a more explicit
    #       message to the users regarding that...
    ttFont.reader.tables["fvar"] = "foo"
    msg = assert_results_contain(
        check(ttFont), FAIL, "required-tables", "with fvar but no STAT..."
    )
    assert "STAT" in msg

    del ttFont.reader.tables["fvar"]
    ttFont.reader.tables["STAT"] = "foo"
    msg = assert_PASS(check(ttFont), "with STAT on a non-variable font...")
    assert msg == "Font contains all required tables."

    # and finally remove what we've just added:
    del ttFont.reader.tables["STAT"]

    # Now we remove required tables one-by-one to validate the FAIL code-path:
    # The font must also contain the table that holds the outlines, "glyf" in this case.
    for required in REQUIRED_TABLES + ["glyf"]:
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        if required in ttFont.reader.tables:
            del ttFont.reader.tables[required]
        msg = assert_results_contain(
            check(ttFont),
            FAIL,
            "required-tables",
            f"with missing mandatory table {required} ...",
        )
        assert required in msg

    # Then, in preparation for the next step, we make sure
    # there's no optional table (by removing them all):
    for optional in OPTIONAL_TABLES:
        if optional in ttFont.reader.tables:
            del ttFont.reader.tables[optional]

    # Then re-insert them one by one to validate the INFO code-path:
    for optional in OPTIONAL_TABLES:
        ttFont.reader.tables[optional] = "foo"
        # and ensure that the second to last logged message is an
        # INFO status informing the user about it:
        msg = assert_results_contain(
            check(ttFont),
            INFO,
            "optional-tables",
            f"with optional table {required} ...",
        )
        assert optional in msg

        # remove the one we've just inserted before trying the next one:
        del ttFont.reader.tables[optional]


def test_check_unwanted_tables():
    """Are there unwanted tables ?"""
    check = CheckTester(universal_profile, "com.google.fonts/check/unwanted_tables")

    unwanted_tables = [
        "FFTM",  # FontForge
        "TTFA",  # TTFAutohint
        "TSI0",  # TSI* = VTT
        "TSI1",
        "TSI2",
        "TSI3",
        "TSI5",
        "prop",  # FIXME: Why is this one unwanted?
    ]
    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    # We now add unwanted tables one-by-one to validate the FAIL code-path:
    for unwanted in unwanted_tables:
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        ttFont.reader.tables[unwanted] = "foo"
        assert_results_contain(
            check(ttFont),
            FAIL,
            "unwanted-tables",
            f"with unwanted table {unwanted} ...",
        )


def test_glyph_has_ink():
    print()  # so next line doesn't start with '.....'

    cff_test_font = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    print("Test if CFF glyph with ink has ink")
    assert glyph_has_ink(cff_test_font, ".notdef") is True
    print("Test if CFF glyph without ink has ink")
    assert glyph_has_ink(cff_test_font, "space") is False

    ttf_test_font = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Regular.ttf"))
    print("Test if TTF glyph with ink has ink")
    assert glyph_has_ink(ttf_test_font, ".notdef") is True
    print("Test if TTF glyph without ink has ink")
    assert glyph_has_ink(ttf_test_font, "space") is False

    cff2_test_font = TTFont(
        TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf")
    )
    print("Test if CFF2 glyph with ink has ink")
    assert glyph_has_ink(cff2_test_font, ".notdef") is True
    print("Test if CFF2 glyph without ink has ink")
    assert glyph_has_ink(cff2_test_font, "space") is False


mada_fonts = [
    # ⚠️ 'test_check_family_win_ascent_and_descent' expects the Regular font to be first
    TEST_FILE("mada/Mada-Regular.ttf"),
    TEST_FILE("mada/Mada-Black.ttf"),
    TEST_FILE("mada/Mada-Bold.ttf"),
    TEST_FILE("mada/Mada-ExtraLight.ttf"),
    TEST_FILE("mada/Mada-Light.ttf"),
    TEST_FILE("mada/Mada-Medium.ttf"),
    TEST_FILE("mada/Mada-SemiBold.ttf"),
]


@pytest.fixture
def mada_ttFonts():
    return [TTFont(path) for path in mada_fonts]


def test_check_family_win_ascent_and_descent(mada_ttFonts):
    """Checking OS/2 usWinAscent & usWinDescent."""
    check = CheckTester(
        universal_profile, "com.google.fonts/check/family/win_ascent_and_descent"
    )

    # Mada Regular is know to be bad
    # single font input
    ttFont = TTFont(mada_fonts[0])
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
    message = assert_PASS(check(ttFont))
    assert message == "OS/2 usWinAscent & usWinDescent values look good!"

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


def test_check_os2_metrics_match_hhea():
    """Checking OS/2 Metrics match hhea Metrics."""
    check = CheckTester(
        universal_profile, "com.google.fonts/check/os2_metrics_match_hhea"
    )

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


def test_check_family_vertical_metrics(montserrat_ttFonts):
    check = CheckTester(
        universal_profile, "com.google.fonts/check/family/vertical_metrics"
    )

    msg = assert_PASS(check(montserrat_ttFonts), "with multiple good fonts...")
    assert msg == "Vertical metrics are the same across the family."

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


def test_check_superfamily_list():
    check = CheckTester(universal_profile, "com.google.fonts/check/superfamily/list")

    msg = assert_results_contain(
        check([], {"superfamily": [cabin_fonts]}), INFO, "family-path"
    )
    assert msg == os.path.normpath("data/test/cabin")


def test_check_superfamily_vertical_metrics(
    montserrat_ttFonts, cabin_ttFonts, cabin_condensed_ttFonts
):
    check = CheckTester(
        universal_profile, "com.google.fonts/check/superfamily/vertical_metrics"
    )

    msg = assert_SKIP(check([], {"superfamily_ttFonts": [cabin_ttFonts[0]]}))
    assert msg == "Sibling families were not detected."

    assert_PASS(
        check([], {"superfamily_ttFonts": [cabin_ttFonts, cabin_condensed_ttFonts]}),
        "with multiple good families...",
    )

    assert_results_contain(
        check([], {"superfamily_ttFonts": [cabin_ttFonts, montserrat_ttFonts]}),
        WARN,
        "superfamily-vertical-metrics",
        "with families that diverge on vertical metric values...",
    )


def test_check_STAT_strings():
    check = CheckTester(universal_profile, "com.google.fonts/check/STAT_strings")

    good = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Roman.ttf"))
    assert_PASS(check(good))

    bad = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Italic.ttf"))
    assert_results_contain(check(bad), FAIL, "bad-italic")


def test_check_rupee():
    """Ensure indic fonts have the Indian Rupee Sign glyph."""
    check = CheckTester(universal_profile, "com.google.fonts/check/rupee")

    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_indic_font" in msg.message

    # This one is good:
    ttFont = TTFont(
        TEST_FILE("indic-font-with-rupee-sign/NotoSerifDevanagari-Regular.ttf")
    )
    assert assert_PASS(check(ttFont)) == "Looks good!"

    # But this one lacks the glyph:
    ttFont = TTFont(
        TEST_FILE("indic-font-without-rupee-sign/NotoSansOlChiki-Regular.ttf")
    )
    msg = assert_results_contain(check(ttFont), FAIL, "missing-rupee")
    assert msg == "Please add a glyph for Indian Rupee Sign (₹) at codepoint U+20B9."


def test_check_unreachable_glyphs():
    """Check font contains no unreachable glyphs."""
    check = CheckTester(universal_profile, "com.google.fonts/check/unreachable_glyphs")

    font = TEST_FILE("noto_sans_tamil_supplement/NotoSansTamilSupplement-Regular.ttf")
    assert_PASS(check(font))

    # Also ensure it works correctly with a color font in COLR v0 format:
    font = TEST_FILE("color_fonts/AmiriQuranColored.ttf")
    assert_PASS(check(font))

    # And also with a color font in COLR v1 format:
    font = TEST_FILE("color_fonts/noto-glyf_colr_1.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    message = assert_results_contain(check(font), WARN, "unreachable-glyphs")
    for glyph in [
        "Gtilde",
        "eight.dnom",
        "four.dnom",
        "three.dnom",
        "two.dnom",
        "i.dot",
        "five.numr",
        "seven.numr",
        "bullet.cap",
        "periodcentered.cap",
        "ampersand.sc",
        "I.uc",
    ]:
        assert glyph in message

    for glyph in [
        "caronvertical",
        "acute.cap",
        "breve.cap",
        "caron.cap",
        "circumflex.cap",
        "dotaccent.cap",
        "dieresis.cap",
        "grave.cap",
        "hungarumlaut.cap",
        "macron.cap",
        "ring.cap",
        "tilde.cap",
        "breve.r",
        "breve.rcap",
    ]:
        assert glyph not in message


def test_check_soft_hyphen(montserrat_ttFonts):
    """Check glyphs contain the recommended contour count"""
    check = CheckTester(universal_profile, "com.google.fonts/check/soft_hyphen")
    for ttFont in montserrat_ttFonts:
        # Montserrat has a softhyphen...
        assert_results_contain(check(ttFont), WARN, "softhyphen")

        _remove_cmap_entry(ttFont, 0x00AD)
        assert_PASS(check(ttFont))


def test_check_contour_count(montserrat_ttFonts):
    """Check glyphs contain the recommended contour count"""
    from fontTools import subset

    check = CheckTester(universal_profile, "com.google.fonts/check/contour_count")

    ttFont = TTFont(TEST_FILE("rokkitt/Rokkitt-Regular.otf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_ttf" in msg.message

    ttFont = TTFont(TEST_FILE("mutatorsans-vf/MutatorSans-VF.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg.message

    ttFont = montserrat_ttFonts[0]

    # Lets swap the glyf 'a' (2 contours) with glyf 'c' (1 contour)
    ttFont["glyf"]["a"] = ttFont["glyf"]["c"]
    msg = assert_results_contain(check(ttFont), WARN, "contour-count")
    assert "Glyph name: a\tContours detected: 1\tExpected: 2" in msg

    # Lets swap the glyf 'a' (2 contours) with space (0 contour) to get a FAIL
    ttFont["glyf"]["a"] = ttFont["glyf"]["space"]
    msg = assert_results_contain(check(ttFont), FAIL, "no-contour")
    assert "Glyph name: a\tExpected: 2" in msg

    # Subset the font to just the 'c' glyph to get a PASS
    subsetter = subset.Subsetter()
    subsetter.populate(text="c")
    subsetter.subset(ttFont)
    msg = assert_PASS(check(ttFont))
    assert msg == "All glyphs have the recommended amount of contours"

    # Now delete the 'cmap' table to trigger a FAIL
    del ttFont["cmap"]
    msg = assert_results_contain(check(ttFont), FAIL, "lacks-cmap")
    assert msg == "This font lacks cmap data."


def test_check_cjk_chws_feature():
    """Does the font contain chws and vchw features?"""
    check = CheckTester(universal_profile, "com.google.fonts/check/cjk_chws_feature")

    cjk_font = TEST_FILE("cjk/SourceHanSans-Regular.otf")
    ttFont = TTFont(cjk_font)
    assert_results_contain(
        check(ttFont), WARN, "missing-chws-feature", "for Source Han Sans"
    )

    assert_results_contain(
        check(ttFont), WARN, "missing-vchw-feature", "for Source Han Sans"
    )

    # Insert them.
    from fontTools.ttLib.tables.otTables import FeatureRecord

    chws = FeatureRecord()
    chws.FeatureTag = "chws"
    vchw = FeatureRecord()
    vchw.FeatureTag = "vchw"
    ttFont["GPOS"].table.FeatureList.FeatureRecord.extend([chws, vchw])

    assert_PASS(check(ttFont))


def test_check_transformed_components():
    """Ensure component transforms do not perform scaling or rotation."""
    check = CheckTester(
        universal_profile, "com.google.fonts/check/transformed_components"
    )

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    # DM Sans v1.100 had some transformed components
    # and it's hinted
    font = TEST_FILE("dm-sans-v1.100/DMSans-Regular.ttf")
    assert_results_contain(check(font), FAIL, "transformed-components")

    # Amiri is unhinted, but it contains four transformed components
    # that result in reversed outline direction
    font = TEST_FILE("amiri/AmiriQuranColored.ttf")
    assert_results_contain(check(font), FAIL, "transformed-components")


def test_check_gpos7():
    """Check if font contains any GPOS 7 lookups
    which are not widely supported."""
    check = CheckTester(universal_profile, "com.google.fonts/check/gpos7")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    font = TEST_FILE("notosanskhudawadi/NotoSansKhudawadi-Regular.ttf")
    assert_results_contain(check(font), WARN, "has-gpos7")


def test_check_freetype_rasterizer():
    """Ensure that the font can be rasterized by FreeType."""
    check = CheckTester(universal_profile, "com.adobe.fonts/check/freetype_rasterizer")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    msg = assert_PASS(check(font), "with a good font...")
    assert msg == "Font can be rasterized by FreeType."

    font = TEST_FILE("ancho/AnchoGX.ttf")
    msg = assert_results_contain(check(font), FAIL, "freetype-crash")
    assert "FT_Exception:  (too many function definitions)" in msg

    font = TEST_FILE("rubik/Rubik-Italic.ttf")
    msg = assert_results_contain(check(font), FAIL, "freetype-crash")
    assert "FT_Exception:  (stack overflow)" in msg

    # Example that segfaults with 'freetype-py' version 2.4.0
    font = TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.ttf")
    msg = assert_PASS(check(font), "with a good font...")
    assert msg == "Font can be rasterized by FreeType."


def test_check_sfnt_version():
    """Ensure that the font has the proper sfntVersion value."""
    check = CheckTester(universal_profile, "com.adobe.fonts/check/sfnt_version")

    # Valid TrueType font; the check must PASS.
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    msg = assert_PASS(check(ttFont))
    assert msg == "Font has the correct sfntVersion value."

    # Change the sfntVersion to an improper value for TrueType fonts.
    # The check should FAIL.
    ttFont.sfntVersion = "OTTO"
    msg = assert_results_contain(check(ttFont), FAIL, "wrong-sfnt-version-ttf")
    assert msg == "Font with TrueType outlines has incorrect sfntVersion value: 'OTTO'"

    # Valid CFF font; the check must PASS.
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf"))
    msg = assert_PASS(check(ttFont))
    assert msg == "Font has the correct sfntVersion value."

    # Change the sfntVersion to an improper value for CFF fonts. The check should FAIL.
    ttFont.sfntVersion = "\x00\x01\x00\x00"
    msg = assert_results_contain(check(ttFont), FAIL, "wrong-sfnt-version-cff")
    assert msg == (
        "Font with CFF data has incorrect sfntVersion value: '\x00\x01\x00\x00'"
    )

    # Valid CFF2 font; the check must PASS.
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))
    msg = assert_PASS(check(ttFont))
    assert msg == "Font has the correct sfntVersion value."

    # Change the sfntVersion to an improper value for CFF fonts. The check should FAIL.
    ttFont.sfntVersion = "\x00\x01\x00\x00"
    msg = assert_results_contain(check(ttFont), FAIL, "wrong-sfnt-version-cff")
    assert msg == (
        "Font with CFF data has incorrect sfntVersion value: '\x00\x01\x00\x00'"
    )


def test_check_whitespace_widths():
    """Whitespace glyphs have coherent widths?"""
    check = CheckTester(universal_profile, "com.google.fonts/check/whitespace_widths")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont["hmtx"].metrics["space"] = (0, 1)
    assert_results_contain(check(ttFont), FAIL, "different-widths")


def test_check_interpolation_issues():
    """Detect any interpolation issues in the font."""
    check = CheckTester(
        universal_profile, "com.google.fonts/check/interpolation_issues"
    )
    # With a good font
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("notosansbamum/NotoSansBamum[wght].ttf"))
    assert_results_contain(check(ttFont), WARN, "interpolation-issues")

    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_variable_font" in msg.message

    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.otf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_ttf" in msg.message


def test_check_math_signs_width():
    """Check font math signs have the same width."""
    check = CheckTester(universal_profile, "com.google.fonts/check/math_signs_width")

    # The STIXTwo family was the reference font project
    # that we used to come up with the initial list of math glyphs
    # that should ideally have the same width.
    font = TEST_FILE("stixtwomath/STIXTwoMath-Regular.ttf")
    assert_PASS(check(font))

    # In our reference Montserrat Regular, the logicalnot
    # (also known as negation sign) '¬' has a width of 555 while
    # all other 12 math glyphs have width = 494.
    font = TEST_FILE("montserrat/Montserrat-Regular.ttf")
    assert_results_contain(check(font), WARN, "width-outliers")


def test_check_linegaps():
    """Checking Vertical Metric Linegaps."""
    check = CheckTester(universal_profile, "com.google.fonts/check/linegaps")

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


def test_check_STAT_in_statics():
    """Checking STAT table on static fonts."""
    check = CheckTester(universal_profile, "com.google.fonts/check/STAT_in_statics")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: has_STAT_table" in msg.message

    ttFont = TTFont(TEST_FILE("varfont/RobotoSerif[GRAD,opsz,wdth,wght].ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg.message

    # Remove fvar table to make FontBakery think it is dealing with a static font
    del ttFont["fvar"]

    # We know that our reference RobotoSerif varfont (which the check is induced
    # here to think it is a static font) has multiple records per design axis in its
    # STAT table:
    msg = assert_results_contain(check(ttFont), FAIL, "multiple-STAT-entries")
    assert "The STAT table has more than a single entry for the 'opsz' axis (5)" in msg

    # Remove all entries except the very first one:
    stat = ttFont["STAT"].table
    stat.AxisValueArray.AxisCount = 1
    stat.AxisValueArray.AxisValue = [stat.AxisValueArray.AxisValue[0]]

    # It should PASS now
    assert assert_PASS(check(ttFont)) == "Looks good!"


def test_check_alt_caron():
    """Check accent of Lcaron, dcaron, lcaron, tcaron"""
    check = CheckTester(universal_profile, "com.google.fonts/check/alt_caron")

    ttFont = TTFont(TEST_FILE("annie/AnnieUseYourTelescope-Regular.ttf"))
    assert_results_contain(check(ttFont), WARN, "bad-mark")
    assert_results_contain(check(ttFont), FAIL, "wrong-mark")

    ttFont = TTFont(TEST_FILE("cousine/Cousine-Bold.ttf"))
    assert_results_contain(check(ttFont), WARN, "decomposed-outline")

    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_PASS(check(ttFont))


def DISABLED_test_check_caps_vertically_centered():
    """Check if uppercase glyphs are vertically centered."""

    check = CheckTester(
        universal_profile, "com.google.fonts/check/caps_vertically_centered"
    )

    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("cjk/SourceHanSans-Regular.otf"))
    assert_SKIP(check(ttFont))

    ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.leftslanted.ttf"))
    assert_results_contain(check(ttFont), WARN, "vertical-metrics-not-centered")
