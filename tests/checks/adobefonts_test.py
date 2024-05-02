"""
Unit tests for Adobe Fonts profile.
"""
import os
from unittest.mock import patch

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import AxisValueRecord
import requests

from fontbakery.status import WARN, FAIL, PASS, SKIP
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    portable_path,
    TEST_FILE,
    MockContext,
)
from fontbakery.constants import (
    NameID,
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)
from fontbakery.profiles import adobefonts as adobefonts_profile


def test_check_family_consistent_upm():
    """A group of fonts designed & produced as a family should have consistent
    units per em."""
    check = CheckTester("com.adobe.fonts/check/family/consistent_upm")

    # these fonts have a consistent unitsPerEm of 1000:
    filenames = [
        "SourceSansPro-Regular.otf",
        "SourceSansPro-Bold.otf",
        "SourceSansPro-Italic.otf",
    ]
    ttFonts = [
        TTFont(os.path.join(portable_path("data/test/source-sans-pro/OTF"), filename))
        for filename in filenames
    ]

    # try fonts with consistent UPM (i.e. 1000)
    assert_PASS(check(ttFonts))

    # now try with one font with a different UPM (i.e. 2048)
    ttFonts[1]["head"].unitsPerEm = 2048
    assert_results_contain(check(ttFonts), FAIL, "inconsistent-upem")


def test_check_find_empty_letters():
    """Validate that empty glyphs are found."""
    check = CheckTester("com.adobe.fonts/check/find_empty_letters")

    # this OT-CFF font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    assert_PASS(check(ttFont))

    # this OT-CFF2 font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Italic.otf"))
    assert_PASS(check(ttFont))

    # this TrueType font has inked glyphs for all letters
    ttFont = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Bold.ttf"))
    assert_PASS(check(ttFont))

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
    check = CheckTester("com.adobe.fonts/check/nameid_1_win_english")

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    assert_PASS(check(ttFont))

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
    check = CheckTester("com.adobe.fonts/check/unsupported_tables")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("hinting/Roboto-VF.ttf"))
    msg = assert_results_contain(check(ttFont), FAIL, "unsupported-tables")
    assert "TSI0" in msg


def test_check_override_whitespace_glyphs():
    """Check that overridden test for nbsp yields WARN rather than FAIL."""
    check = CheckTester(
        "com.google.fonts/check/whitespace_glyphs", profile=adobefonts_profile
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
        "com.google.fonts/check/valid_glyphnames", profile=adobefonts_profile
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
        "com.google.fonts/check/family/win_ascent_and_descent",
        profile=adobefonts_profile,
    )

    # Our reference Mada Regular is know to FAIL the original check.
    # The overridden check should just WARN.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), WARN, "ascent")
    assert (
        "OS/2.usWinAscent value should be equal or greater than 880,"
        " but got 776 instead"
    ) in msg
    assert "Overridden" in msg
    assert "For Adobe, this is not as severe as" in msg

    vm = MockContext(ttFonts=[ttFont]).vmetrics
    y_max = vm["ymax"]
    y_min = vm["ymin"]
    os2_table = ttFont["OS/2"]

    # Now change 'OS/2.usWinAscent' to be more than double 'head.yMax'.
    # The overridden check should just WARN.
    os2_table.usWinAscent = y_max * 2 + 1
    msg = assert_results_contain(check(ttFont), WARN, "ascent")
    assert (
        "OS/2.usWinAscent value 1761 is too large."
        " It should be less than double the yMax. Current yMax value is 880"
    ) in msg
    assert "Overridden" in msg
    assert "For Adobe, this is not as severe as" in msg

    # Now fix the value of 'OS/2.usWinAscent'. The overridden check should PASS.
    os2_table.usWinAscent = y_max
    assert_PASS(check(ttFont), PASS)

    # Now mess up the 'OS/2.usWinDescent' value. The overridden check should just WARN.
    os2_table.usWinDescent = abs(y_min) - 10
    msg = assert_results_contain(check(ttFont), WARN, "descent")
    assert (
        "OS/2.usWinDescent value should be equal or greater than 292,"
        " but got 282 instead"
    ) in msg
    assert "Overridden" in msg
    assert "For Adobe, this is not as severe as" in msg

    # Now change 'OS/2.usWinDescent' to be more than double 'head.yMin'.
    # The overridden check should just WARN.
    os2_table.usWinDescent = abs(y_min) * 2 + 1
    msg = assert_results_contain(check(ttFont), WARN, "descent")
    assert (
        "OS/2.usWinDescent value 585 is too large."
        " It should be less than double the yMin. Current absolute yMin value is 292"
    ) in msg
    assert "Overridden" in msg
    assert "For Adobe, this is not as severe as" in msg


def test_check_override_os2_metrics_match_hhea():
    """Check that overridden test yields WARN rather than FAIL."""
    check = CheckTester(
        "com.google.fonts/check/os2_metrics_match_hhea",
        profile=adobefonts_profile,
    )

    # Our reference Mada Black is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Black.ttf"))
    assert_PASS(check(ttFont), PASS)

    os2_table = ttFont["OS/2"]
    hhea_table = ttFont["hhea"]
    ascent = hhea_table.ascent
    descent = hhea_table.descent
    linegap = hhea_table.lineGap

    # Now we change sTypoAscender to be bad. The overridden check should just WARN.
    os2_table.sTypoAscender = ascent - 100
    msg = assert_results_contain(check(ttFont), WARN, "ascender")
    assert "OS/2 sTypoAscender (800) and hhea ascent (900) must be equal." in msg
    assert "Overridden" in msg

    # Restore 'sTypoAscender' to a good value.
    os2_table.sTypoAscender = ascent

    # And break the font again, now changing the sTypoDescender value.
    # The overridden check should just WARN.
    os2_table.sTypoDescender = descent + 100
    msg = assert_results_contain(check(ttFont), WARN, "descender")
    assert "OS/2 sTypoDescender (-200) and hhea descent (-300) must be equal." in msg
    assert "Overridden" in msg

    # Restore 'sTypoDescender' to a good value.
    os2_table.sTypoDescender = descent

    # And break the font one last time, now changing the sTypoLineGap value.
    # The overridden check should just WARN.
    os2_table.sTypoLineGap = linegap + 100
    msg = assert_results_contain(check(ttFont), WARN, "lineGap")
    assert "OS/2 sTypoLineGap (200) and hhea lineGap (100) must be equal." in msg
    assert "Overridden" in msg


def test_check_override_varfont_valid_default_instance_nameids():
    """Check that overriden tests yield WARN instead of FAIL"""
    check = CheckTester(
        "com.adobe.fonts/check/varfont/valid_default_instance_nameids",
        profile=adobefonts_profile,
    )

    ttFont_1 = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))

    # Change subfamilyNameID value of the default instance to another name ID whose
    # string doesn't match the font's Subfamily name, thus making the check fail.
    fvar_table_1 = ttFont_1["fvar"]
    dflt_inst = fvar_table_1.instances[0]
    dflt_inst.subfamilyNameID = 16  # the font doesn't have this record
    msg = assert_results_contain(
        check(ttFont_1), WARN, "invalid-default-instance-subfamily-name"
    )
    assert (
        "'Instance #1' instance has the same coordinates as the default"
        " instance; its subfamily name should be 'Regular'"
    ) in msg
    assert "Overridden" in msg

    # The value of postScriptNameID is 0xFFFF for all the instance records in CabinVF.
    # Change one of them, to make the check validate the postScriptNameID value of the
    # default instance (which is currently 0xFFFF).
    inst_2 = fvar_table_1.instances[1]
    inst_2.postscriptNameID = 256  # the font doesn't have this record
    msg = assert_results_contain(
        check(ttFont_1), WARN, "invalid-default-instance-postscript-name"
    )
    assert (
        "'Instance #1' instance has the same coordinates as the default instance;"
        " its postscript name should be 'Cabin-Regular', instead of 'None'."
    ) in msg
    assert "Overridden" in msg


def test_check_override_stat_has_axis_value_tables():
    """Check that overridden tests yield the right result."""
    check = CheckTester(
        "com.adobe.fonts/check/stat_has_axis_value_tables",
        profile=adobefonts_profile,
    )

    # Our reference Cabin[wdth,wght].ttf variable font has Axis Value tables.
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    # Remove the 4th Axis Value table (index 3), belonging to 'Medium' weight.
    # The overridden check should WARN.
    ttFont["STAT"].table.AxisValueArray.AxisValue.pop(3)
    msg = assert_results_contain(check(ttFont), WARN, "missing-axis-value-table")
    assert "STAT table is missing Axis Value for 'wght' value '500.0'" in msg
    assert "Overridden" in msg

    # Add a format 4 AxisValue table with a single AxisValueRecord. This overriden check
    # should WARN.
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    f4avt = type(ttFont["STAT"].table.AxisValueArray.AxisValue[0])()
    f4avt.Format = 4
    f4avt.Flags = 0
    f4avt.ValueNameID = 2
    avr0 = AxisValueRecord()
    avr0.AxisIndex = 0
    avr0.Value = 100
    f4avt.AxisValueRecord = [avr0]
    f4avt.AxisCount = len(f4avt.AxisValueRecord)
    ttFont["STAT"].table.AxisValueArray.AxisValue.append(f4avt)
    msg = assert_results_contain(check(ttFont), WARN, "format-4-axis-count")
    assert "STAT Format 4 Axis Value table has axis count <= 1." in msg
    assert "Overridden" in msg


def test_check_override_inconsistencies_between_fvar_stat():
    """Check that the overridden test yields WARN rather than FAIL"""
    check = CheckTester(
        "com.fontwerk/check/inconsistencies_between_fvar_stat",
        profile=adobefonts_profile,
    )

    ttFont = TTFont(TEST_FILE("bad_fonts/fvar_stat_differences/AxisLocationVAR.ttf"))
    # add name with wrong order of name parts
    ttFont["name"].setName("Medium Text", 277, 3, 1, 0x409)
    assert_results_contain(
        check(ttFont), WARN, "missing-fvar-instance-axis-value", "missing in STAT table"
    )


def test_check_override_weight_class_fvar():
    check = CheckTester(
        "com.fontwerk/check/weight_class_fvar", profile=adobefonts_profile
    )

    ttFont = TTFont(TEST_FILE("varfont/Oswald-VF.ttf"))
    ttFont["OS/2"].usWeightClass = 333
    assert_results_contain(
        check(ttFont), WARN, "bad-weight-class", "but should match fvar default value."
    )


@patch("requests.get", side_effect=requests.exceptions.ConnectionError)
def test_check_override_fontbakery_version(mock_get):
    """Check that overridden test yields SKIP rather than FAIL."""
    check = CheckTester(
        "com.google.fonts/check/fontbakery_version",
        profile=adobefonts_profile,
    )

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    msg = assert_results_contain(check(font), SKIP, "connection-error")
    assert "Request to PyPI.org failed with this message" in msg


def test_check_override_match_familyname_fullfont():
    """Check that overridden test yields WARN rather than FAIL."""
    check = CheckTester(
        "com.google.fonts/check/name/match_familyname_fullfont",
        profile=adobefonts_profile,
    )

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Semibold.otf"))
    assert_PASS(check(ttFont), PASS)

    # Change the Full Font Name string for Microsoft platform record
    full_font_name = "SourceSansPro-Semibold"
    ttFont["name"].setName(
        full_font_name,
        NameID.FULL_FONT_NAME,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA,
    )
    msg = assert_results_contain(check(ttFont), WARN, "mismatch-font-names")
    assert (
        f"the full font name {full_font_name!r}"
        " does not begin with the font family name"
    ) in msg


def test_check_override_trailing_spaces():
    """Check that overridden test yields WARN rather than FAIL."""
    check = CheckTester(
        "com.google.fonts/check/name/trailing_spaces",
        profile=adobefonts_profile,
    )

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Semibold.otf"))
    assert_PASS(check(ttFont), PASS)

    # Add a trailing space to the License string for Microsoft platform record
    name_table = ttFont["name"]
    license_string = name_table.getName(
        NameID.LICENSE_DESCRIPTION,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA,
    )
    license_string = f"{license_string.toUnicode()} "
    name_table.setName(
        license_string,
        NameID.LICENSE_DESCRIPTION,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA,
    )
    msg = assert_results_contain(check(ttFont), WARN, "trailing-space")
    assert "'This Font [...]Software. '" in msg
    assert "Overridden" in msg


def test_check_override_bold_wght_coord():
    """Check that overriden tests yield WARN rather than FAIL."""
    check = CheckTester(
        "com.google.fonts/check/varfont/bold_wght_coord",
        profile=adobefonts_profile,
    )

    ttFont = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))
    fvar_table = ttFont["fvar"]

    # change the Bold instance 'wght' coord to something other than 700
    fvar_table.instances[4].coordinates["wght"] = 725
    msg = assert_results_contain(check(ttFont), WARN, "wght-not-700")
    assert msg.startswith(
        'The "wght" axis coordinate of the "Bold" instance must be 700.'
    )

    # remove "Bold" named instance
    del fvar_table.instances[4]

    msg = assert_results_contain(check(ttFont), WARN, "no-bold-instance")
    assert '"Bold" instance not present.' in msg
    assert "Overridden" in msg


def test_check_STAT_strings():
    """Check com.adobe.fonts/check/STAT_strings."""
    check = CheckTester(
        "com.adobe.fonts/check/STAT_strings",
    )

    # This should FAIL (like com.google.fonts/check/STAT_strings that
    # it is based on) because it uses "Italic" in names for 'wght' and 'wdth' axes.
    ttFont = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Italic.ttf"))
    msg = assert_results_contain(check(ttFont), FAIL, "bad-italic")
    assert (
        'The following AxisValue entries in the STAT table should not contain "Italic"'
        in msg
    )

    # Now set up a font using "Italic" for the 'slnt' axis
    ttFont = TTFont(TEST_FILE("slant_direction/Cairo_correct_slnt_axis.ttf"))
    ttFont["name"].setName("Italic", 286, 3, 1, 1033)
    # This should PASS with our check
    assert_PASS(check(ttFont))
