from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0, KernTable_format_unkown

from fontbakery.status import INFO, FAIL, WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)

from fontbakery.profiles import opentype as opentype_profile


def test_check_kern_table():
    """Is there a "kern" table declared in the font?"""
    check = CheckTester(opentype_profile, "com.google.fonts/check/kern_table")

    # Our reference Mada Regular is known to be good
    # (does not have a 'kern' table):
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), 'with a font without a "kern" table...')

    # add a basic 'kern' table:
    kern = ttFont["kern"] = newTable("kern")
    kern.version = 0
    subtable = KernTable_format_0()
    subtable.coverage = 1
    subtable.version = 0
    subtable.kernTable = {("A", "V"): -50}
    kern.kernTables = [subtable]

    # and make sure the check emits an INFO message:
    assert_results_contain(
        check(ttFont), INFO, "kern-found", 'with a font containing a "kern" table...'
    )

    # and a FAIL message when a non-character glyph is used.
    subtable.kernTable.update({("A", "four.dnom"): -50})
    assert_results_contain(
        check(ttFont),
        FAIL,
        "kern-non-character-glyphs",
        "The following glyphs should not be used...",
    )

    # and a WARN message when a non-character glyph is used.
    subtable = KernTable_format_unkown(2)
    kern.kernTables = [subtable]
    assert_results_contain(
        check(ttFont),
        WARN,
        "kern-unknown-format",
        'The "kern" table does not have any format-0 subtable...',
    )
