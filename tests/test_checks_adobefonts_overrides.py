from unittest.mock import patch

from fontTools.ttLib import TTFont
import requests

from conftest import check_id
from fontbakery.status import WARN, SKIP
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
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


@check_id("whitespace_glyphs", profile=adobefonts_profile)
def test_check_override_whitespace_glyphs(check):
    """Check that overridden test for nbsp yields WARN rather than FAIL."""

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    assert_PASS(check(ttFont))

    # remove U+00A0, status should be WARN (standard check would be FAIL)
    for subtable in ttFont["cmap"].tables:
        subtable.cmap.pop(0x00A0, None)
    assert_results_contain(check(ttFont), WARN, "missing-whitespace-glyph-0x00A0")


@check_id("valid_glyphnames", profile=adobefonts_profile)
def test_check_override_valid_glyphnames(check):
    """Check that overridden test yields WARN rather than FAIL."""

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


@check_id("family/win_ascent_and_descent", profile=adobefonts_profile)
def test_check_override_family_win_ascent_and_descent(check):
    """Check that overridden test yields WARN rather than FAIL."""

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
    assert_PASS(check(ttFont))

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


@check_id("os2_metrics_match_hhea", profile=adobefonts_profile)
def test_check_override_os2_metrics_match_hhea(check):
    """Check that overridden test yields WARN rather than FAIL."""

    # Our reference Mada Black is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Black.ttf"))
    assert_PASS(check(ttFont))

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


@check_id("opentype/varfont/valid_default_instance_nameids", profile=adobefonts_profile)
def test_check_override_varfont_valid_default_instance_nameids(check):
    """Check that overriden tests yield WARN instead of FAIL"""

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


@check_id("inconsistencies_between_fvar_STAT", profile=adobefonts_profile)
def test_check_override_inconsistencies_between_fvar_STAT(check):
    """Check that the overridden test yields WARN rather than FAIL"""

    ttFont = TTFont(TEST_FILE("bad_fonts/fvar_STAT_differences/AxisLocationVAR.ttf"))
    # add name with wrong order of name parts
    ttFont["name"].setName("Medium Text", 277, 3, 1, 0x409)
    assert_results_contain(
        check(ttFont), WARN, "missing-fvar-instance-axis-value", "missing in STAT table"
    )


@check_id("opentype/weight_class_fvar", profile=adobefonts_profile)
def test_check_override_weight_class_fvar(check):
    ttFont = TTFont(TEST_FILE("varfont/Oswald-VF.ttf"))
    ttFont["OS/2"].usWeightClass = 333
    assert_results_contain(
        check(ttFont), WARN, "bad-weight-class", "but should match fvar default value."
    )


# FIXME: how can we use @check_id here alongside @patch?
@patch("requests.get", side_effect=requests.exceptions.ConnectionError)
def test_check_override_fontbakery_version(mock_get):
    """Check that overridden test yields SKIP rather than FAIL."""
    from fontbakery.codetesting import CheckTester

    check = CheckTester("fontbakery_version", profile=adobefonts_profile)

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    msg = assert_results_contain(check(font), SKIP, "connection-error")
    assert "Request to PyPI.org failed with this message" in msg


@check_id("opentype/name/match_familyname_fullfont", profile=adobefonts_profile)
def test_check_override_match_familyname_fullfont(check):
    """Check that overridden test yields WARN rather than FAIL."""

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Semibold.otf"))
    assert_PASS(check(ttFont))

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


@check_id("name/trailing_spaces", profile=adobefonts_profile)
def test_check_override_trailing_spaces(check):
    """Check that overridden test yields WARN rather than FAIL."""

    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Semibold.otf"))
    assert_PASS(check(ttFont))

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


@check_id("varfont/bold_wght_coord", profile=adobefonts_profile)
def test_check_override_bold_wght_coord(check):
    """Check that overriden tests yield WARN rather than FAIL."""

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
