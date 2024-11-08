import os

from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    portable_path,
    TEST_FILE,
)


@check_id("adobefonts/family/consistent_upm")
def test_check_family_consistent_upm(check):
    """A group of fonts designed & produced as a family should have consistent
    units per em."""

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


def _get_nameid_1_win_eng_record(name_table):
    """Helper method that returns the Windows nameID 1 US-English record"""
    for rec in name_table.names:
        if (rec.nameID, rec.platformID, rec.platEncID, rec.langID) == (1, 3, 1, 0x409):
            return rec
    return None


@check_id("adobefonts/nameid_1_win_english")
def test_check_nameid_1_win_english(check):
    """Validate that font has a good nameID 1, Windows/Unicode/US-English
    `name` table record."""

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


@check_id("adobefonts/unsupported_tables")
def test_check_unsupported_tables(check):
    """Check if font has any unsupported tables."""

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("hinting/Roboto-VF.ttf"))
    msg = assert_results_contain(check(ttFont), FAIL, "unsupported-tables")
    assert "TSI0" in msg


@check_id("adobefonts/STAT_strings")
def test_check_STAT_strings(check):
    """Check adobefonts/STAT_strings."""

    # This should FAIL (like `STAT_strings`, that it is based on)
    # because it uses "Italic" in names for 'wght' and 'wdth' axes.
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
