from unittest.mock import MagicMock

from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL, INFO
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


def newTable(tag):
    obj = MagicMock()
    obj.loadData = lambda *args: b"foo"
    return obj


@check_id("required_tables")
def test_check_required_tables(check):
    """Font contains all required tables ?"""
    REQUIRED_TABLES = [
        "cmap",
        "head",
        "hhea",
        "hmtx",  # "maxp",
        "name",
        "OS/2",
        "post",
    ]

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
    assert_PASS(check(ttFont), "with a good font...")

    # Here we confirm that the check also yields INFO with
    # a list of table tags specific to the font.
    msg = assert_results_contain(check(ttFont), INFO, "optional-tables")
    for tag in ("loca", "GPOS", "GSUB"):
        assert tag in msg

    # The OpenType-CFF font contains all required tables, so it must PASS the check.
    assert_PASS(check(cff_font), "with a good font...")

    # Here we confirm that the check also yields INFO with
    # a list of table tags specific to the OpenType-CFF font.
    msg = assert_results_contain(check(cff_font), INFO, "optional-tables")
    for tag in ("BASE", "GPOS", "GSUB"):
        assert tag in msg

    # The OpenType-CFF2 font contains all required tables, so it must PASS the check.
    assert_PASS(check(cff2_font), "with a good font...")

    # Here we confirm that the check also yields INFO with
    # a list of table tags specific to the OpenType-CFF2 font.
    msg = assert_results_contain(check(cff2_font), INFO, "optional-tables")
    for tag in ("BASE", "GPOS", "GSUB"):
        assert tag in msg

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
        ttFont.reader.tables[optional] = newTable(optional)
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
