"""
Unit tests for Adobe Fonts profile.
"""
import os
from unittest.mock import patch

from fontTools.ttLib import TTFont
from requests.exceptions import ConnectionError

from fontbakery.checkrunner import WARN, FAIL, PASS, SKIP
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    portable_path,
    TEST_FILE,
)
from fontbakery.constants import (
    NameID,
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)
from fontbakery.profiles import adobefonts as adobefonts_profile
from fontbakery.profiles.adobefonts import (
    ADOBEFONTS_PROFILE_CHECKS,
    OVERRIDDEN_CHECKS,
    profile,
    SET_EXPLICIT_CHECKS,
)
from fontbakery.profiles.shared_conditions import vmetrics

OVERRIDE_SUFFIX = ":adobefonts"


def test_get_family_checks():
    """Validate the set of family checks."""
    family_checks = profile.get_family_checks()
    family_check_ids = {check.id for check in family_checks}
    expected_family_check_ids = {
        "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",
        "com.adobe.fonts/check/family/consistent_upm",
        "com.adobe.fonts/check/family/max_4_fonts_per_family_name",
        "com.google.fonts/check/family/underline_thickness",
        "com.google.fonts/check/family/panose_proportion",
        "com.google.fonts/check/family/panose_familytype",
        "com.google.fonts/check/family/equal_unicode_encodings",
        "com.google.fonts/check/family/equal_font_versions",
        f"com.google.fonts/check/family/win_ascent_and_descent{OVERRIDE_SUFFIX}",
        "com.google.fonts/check/family/vertical_metrics",
        "com.google.fonts/check/family/single_directory",
        # should it be included here? or should we have
        # a get_superfamily_checks() method?
        # 'com.google.fonts/check/superfamily/vertical_metrics',
    }
    assert family_check_ids == expected_family_check_ids


def test_profile_check_set():
    """Confirm that the profile has the correct number of checks and the correct
    set of check IDs."""
    assert len(SET_EXPLICIT_CHECKS) == 79
    explicit_with_overrides = sorted(
        f"{check_id}{OVERRIDE_SUFFIX}" if check_id in OVERRIDDEN_CHECKS else check_id
        for check_id in SET_EXPLICIT_CHECKS
    )
    assert explicit_with_overrides == sorted(ADOBEFONTS_PROFILE_CHECKS)


def test_check_family_consistent_upm():
    """A group of fonts designed & produced as a family should have consistent
    units per em."""
    check = CheckTester(
        adobefonts_profile, "com.adobe.fonts/check/family/consistent_upm"
    )

    # these fonts have a consistent unitsPerEm of 1000:
    filenames = [
        "SourceSansPro-Regular.otf",
        "SourceSansPro-Bold.otf",
        "SourceSansPro-Italic.otf",
    ]
    fonts = [
        os.path.join(portable_path("data/test/source-sans-pro/OTF"), filename)
        for filename in filenames
    ]

    # try fonts with consistent UPM (i.e. 1000)
    assert_PASS(check(fonts))

    ttFonts = check["ttFonts"]
    # now try with one font with a different UPM (i.e. 2048)
    ttFonts[1]["head"].unitsPerEm = 2048
    assert_results_contain(check(ttFonts), FAIL, "inconsistent-upem")


def test_check_find_empty_letters():
    """Validate that empty glyphs are found."""
    check = CheckTester(adobefonts_profile, "com.adobe.fonts/check/find_empty_letters")

    PASS_MSG = "No empty glyphs for letters found."

    # this OT-CFF font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    assert assert_PASS(check(ttFont)) == PASS_MSG

    # this OT-CFF2 font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.otf"))
    assert assert_PASS(check(ttFont)) == PASS_MSG

    # this TrueType font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Bold.ttf"))
    assert assert_PASS(check(ttFont)) == PASS_MSG

    # Add 2 Korean hangul syllable characters to cmap table mapped to the 'space' glyph.
    # These characters are part of the set whose glyphs are allowed to be blank.
    # The check should only yield a WARN.
    for cmap_table in ttFont["cmap"].tables:
        if cmap_table.format != 4:
            cmap_table.cmap[0xB646] = "space"
            cmap_table.cmap[0xD7A0] = "space"
    msg = assert_results_contain(check(ttFont), WARN, "empty-hangul-letter")
    assert msg == "Found 2 empty hangul glyph(s)."

    # this font has empty glyphs for several letters,
    # the first of which is 'B' (U+0042)
    ttFont = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), FAIL, "empty-letter")
    assert msg == "U+0042 should be visible, but its glyph ('B') is empty."


def _get_nameid_1_win_eng_record(name_table):
    """Helper method that returns the Windows nameID 1 US-English record"""
    for rec in name_table.names:
        if (rec.nameID, rec.platformID, rec.platEncID, rec.langID) == (1, 3, 1, 0x409):
            return rec
    return None


def test_check_nameid_1_win_english():
    """Validate that font has a good nameID 1, Windows/Unicode/US-English
    `name` table record."""
    check = CheckTester(
        adobefonts_profile, "com.adobe.fonts/check/nameid_1_win_english"
    )

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    msg = assert_PASS(check(ttFont))
    assert msg == "Font contains a good Windows nameID 1 US-English record."

    name_table = ttFont["name"]
    nameid_1_win_eng_rec = _get_nameid_1_win_eng_record(name_table)

    # Replace the nameID 1 string with an empty string
    nameid_1_win_eng_rec.string = ""
    msg = assert_results_contain(check(ttFont), FAIL, "nameid-1-empty")
    assert msg == "Windows nameID 1 US-English record is empty."

    # Replace the nameID 1 string with data that can't be 'utf_16_be'-decoded
    nameid_1_win_eng_rec.string = "\xff".encode("utf_7")
    msg = assert_results_contain(check(ttFont), FAIL, "nameid-1-decoding-error")
    assert msg == "Windows nameID 1 US-English record could not be decoded."

    # Delete all 'name' table records
    name_table.names = []
    msg = assert_results_contain(check(ttFont), FAIL, "nameid-1-not-found")
    assert msg == "Windows nameID 1 US-English record not found."

    # Delete 'name' table
    del ttFont["name"]
    msg = assert_results_contain(check(ttFont), FAIL, "name-table-not-found")
    assert msg == "Font has no 'name' table."


def test_check_unsupported_tables():
    """Check if font has any unsupported tables."""
    check = CheckTester(
        adobefonts_profile, "com.adobe.fonts/check/unsupported_tables"
    )

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    msg = assert_PASS(check(ttFont))
    assert msg == "No unsupported tables were found."

    ttFont = TTFont(TEST_FILE("hinting/Roboto-VF.ttf"))
    msg = assert_results_contain(check(ttFont), FAIL, "unsupported-tables")
    assert "TSI0" in msg


def test_check_override_whitespace_glyphs():
    """Check that overridden test for nbsp yields WARN rather than FAIL."""
    check = CheckTester(
        adobefonts_profile, f"com.google.fonts/check/whitespace_glyphs{OVERRIDE_SUFFIX}"
    )

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    assert_PASS(check(ttFont))

    # remove U+00A0, status should be WARN (standard check would be FAIL)
    for subtable in ttFont["cmap"].tables:
        subtable.cmap.pop(0x00A0, None)
    assert_results_contain(check(ttFont), WARN, "missing-whitespace-glyph-0x00A0")


def test_check_override_valid_glyphnames():
    """Check that overridden test yields WARN rather than FAIL."""
    check = CheckTester(
        adobefonts_profile, f"com.google.fonts/check/valid_glyphnames{OVERRIDE_SUFFIX}"
    )

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    good_name = "b" * 63
    bad_name1 = "a" * 64
    bad_name2 = "3cents"
    bad_name3 = ".threecents"
    ttFont.glyphOrder[2] = bad_name1
    ttFont.glyphOrder[3] = bad_name2
    ttFont.glyphOrder[4] = bad_name3
    ttFont.glyphOrder[5] = good_name
    message = assert_results_contain(check(ttFont), WARN, "found-invalid-names")
    assert good_name not in message
    assert bad_name1 in message
    assert bad_name2 in message
    assert bad_name3 in message


def test_check_override_family_win_ascent_and_descent():
    """Check that overridden test yields WARN rather than FAIL."""
    check = CheckTester(
        adobefonts_profile,
        f"com.google.fonts/check/family/win_ascent_and_descent{OVERRIDE_SUFFIX}",
    )

    # Our reference Mada Regular is know to FAIL the original check.
    # The overridden check should just WARN.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), WARN, "ascent")
    assert msg == (
        "OS/2.usWinAscent value should be equal or greater than 880,"
        " but got 776 instead"
    )

    vm = vmetrics([ttFont])
    y_max = vm["ymax"]
    y_min = vm["ymin"]
    os2_table = ttFont["OS/2"]

    # Now change 'OS/2.usWinAscent' to be more than double 'head.yMax'.
    # The overridden check should just WARN.
    os2_table.usWinAscent = y_max * 2 + 1
    msg = assert_results_contain(check(ttFont), WARN, "ascent")
    assert msg == (
        "OS/2.usWinAscent value 1761 is too large."
        " It should be less than double the yMax. Current yMax value is 880"
    )

    # Now fix the value of 'OS/2.usWinAscent'. The overridden check should PASS.
    os2_table.usWinAscent = y_max
    msg = assert_PASS(check(ttFont), PASS)
    assert msg == "OS/2 usWinAscent & usWinDescent values look good!"

    # Now mess up the 'OS/2.usWinDescent' value. The overridden check should just WARN.
    os2_table.usWinDescent = abs(y_min) - 10
    msg = assert_results_contain(check(ttFont), WARN, "descent")
    assert msg == (
        "OS/2.usWinDescent value should be equal or greater than 292,"
        " but got 282 instead."
    )

    # Now change 'OS/2.usWinDescent' to be more than double 'head.yMin'.
    # The overridden check should just WARN.
    os2_table.usWinDescent = abs(y_min) * 2 + 1
    msg = assert_results_contain(check(ttFont), WARN, "descent")
    assert msg == (
        "OS/2.usWinDescent value 585 is too large."
        " It should be less than double the yMin. Current absolute yMin value is 292"
    )


def test_check_override_os2_metrics_match_hhea():
    """Check that overridden test yields WARN rather than FAIL."""
    check = CheckTester(
        adobefonts_profile,
        f"com.google.fonts/check/os2_metrics_match_hhea{OVERRIDE_SUFFIX}",
    )

    # Our reference Mada Black is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Black.ttf"))
    msg = assert_PASS(check(ttFont), PASS)
    assert msg == "OS/2.sTypoAscender/Descender values match hhea.ascent/descent."

    os2_table = ttFont["OS/2"]
    hhea_table = ttFont["hhea"]
    ascent = hhea_table.ascent
    descent = hhea_table.descent
    linegap = hhea_table.lineGap

    # Now we change sTypoAscender to be bad. The overridden check should just WARN.
    os2_table.sTypoAscender = ascent - 100
    msg = assert_results_contain(check(ttFont), WARN, "ascender")
    assert msg == "OS/2 sTypoAscender (800) and hhea ascent (900) must be equal."

    # Restore 'sTypoAscender' to a good value.
    os2_table.sTypoAscender = ascent

    # And break the font again, now changing the sTypoDescender value.
    # The overridden check should just WARN.
    os2_table.sTypoDescender = descent + 100
    msg = assert_results_contain(check(ttFont), WARN, "descender")
    assert msg == "OS/2 sTypoDescender (-200) and hhea descent (-300) must be equal."

    # Restore 'sTypoDescender' to a good value.
    os2_table.sTypoDescender = descent

    # And break the font one last time, now changing the sTypoLineGap value.
    # The overridden check should just WARN.
    os2_table.sTypoLineGap = linegap + 100
    msg = assert_results_contain(check(ttFont), WARN, "lineGap")
    assert msg == "OS/2 sTypoLineGap (200) and hhea lineGap (100) must be equal."


@patch("freetype.Face", side_effect=ImportError)
def test_check_override_freetype_rasterizer(mock_import_error):
    """Check that overridden test yields FAIL rather than SKIP."""
    check = CheckTester(
        adobefonts_profile,
        f"com.adobe.fonts/check/freetype_rasterizer{OVERRIDE_SUFFIX}",
    )

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    msg = assert_results_contain(check(font), FAIL, "freetype-not-installed")
    assert "FreeType is not available" in msg


@patch("requests.get", side_effect=ConnectionError)
def test_check_override_fontbakery_version(mock_get):
    """Check that overridden test yields SKIP rather than FAIL."""
    check = CheckTester(
        adobefonts_profile,
        f"com.google.fonts/check/fontbakery_version{OVERRIDE_SUFFIX}",
    )

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    msg = assert_results_contain(check(font), SKIP, "connection-error")
    assert "Request to PyPI.org failed with this message" in msg


def test_check_override_match_familyname_fullfont():
    """Check that overridden test yields WARN rather than FAIL."""
    check = CheckTester(
        adobefonts_profile,
        f"com.google.fonts/check/name/match_familyname_fullfont{OVERRIDE_SUFFIX}",
    )

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Semibold.otf"))
    msg = assert_PASS(check(ttFont), PASS)
    assert msg == "Full font name begins with the font family name."

    # Change the Full Font Name string for Microsoft platform record
    full_font_name = "SourceSansPro-Semibold"
    ttFont["name"].setName(full_font_name,
                           NameID.FULL_FONT_NAME,
                           PlatformID.WINDOWS,
                           WindowsEncodingID.UNICODE_BMP,
                           WindowsLanguageID.ENGLISH_USA)
    msg = assert_results_contain(check(ttFont), WARN, "mismatch-font-names")
    assert (f"the full font name {full_font_name!r}"
            " does not begin with the font family name") in msg


def test_check_override_trailing_spaces():
    """Check that overridden test yields WARN rather than FAIL."""
    check = CheckTester(
        adobefonts_profile,
        f"com.google.fonts/check/name/trailing_spaces{OVERRIDE_SUFFIX}",
    )

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Semibold.otf"))
    msg = assert_PASS(check(ttFont), PASS)
    assert msg == "No trailing spaces on name table entries."

    # Add a trailing space to the License string for Microsoft platform record
    name_table = ttFont["name"]
    license_string = name_table.getName(NameID.LICENSE_DESCRIPTION,
                                        PlatformID.WINDOWS,
                                        WindowsEncodingID.UNICODE_BMP,
                                        WindowsLanguageID.ENGLISH_USA)
    license_string = f"{license_string.toUnicode()} "
    name_table.setName(license_string,
                       NameID.LICENSE_DESCRIPTION,
                       PlatformID.WINDOWS,
                       WindowsEncodingID.UNICODE_BMP,
                       WindowsLanguageID.ENGLISH_USA)
    msg = assert_results_contain(check(ttFont), WARN, "trailing-space")
    assert msg.endswith("'This Font [...]Software. '")


def test_check_override_bold_wght_coord():
    """Check that overriden test yields WARN rather than FAIL."""
    check = CheckTester(
        adobefonts_profile,
        f"com.google.fonts/check/varfont/bold_wght_coord{OVERRIDE_SUFFIX}",
    )

    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))

    # remove "Bold" named instance
    fvar_table = ttFont["fvar"]
    del fvar_table.instances[4]

    msg = assert_results_contain(check(ttFont), WARN, 'no-bold-instance')
    assert msg == '"Bold" instance not present.'
