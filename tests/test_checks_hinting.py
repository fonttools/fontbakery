from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.status import FAIL, INFO


def test_check_hinting_impact():
    """Show hinting filesize impact."""
    check = CheckTester("hinting_impact")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_results_contain(
        check(font), INFO, "size-impact", "this check always emits an INFO result..."
    )

    font = TEST_FILE("rokkitt/Rokkitt-Bold.otf")
    assert_results_contain(
        check(font), INFO, "size-impact", "this check always emits an INFO result..."
    )


def test_check_integer_ppem_if_hinted():
    """PPEM must be an integer on hinted fonts."""
    check = CheckTester("integer_ppem_if_hinted")

    # Our reference Merriweather Regular is hinted, but does not set
    # the "rounded PPEM" flag (bit 3 on the head table flags) as
    # described at https://docs.microsoft.com/en-us/typography/opentype/spec/head
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # So it must FAIL the check:
    assert_results_contain(check(ttFont), FAIL, "bad-flags", "with a bad font...")

    # hotfixing it should make it PASS:
    ttFont["head"].flags |= 1 << 3

    assert_PASS(check(ttFont), "with a good font...")


def test_check_smart_dropout():
    """Ensure smart dropout control is enabled in "prep" table instructions."""
    check = CheckTester("smart_dropout")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))

    # "Program at 'prep' table contains
    #  instructions enabling smart dropout control."
    assert_PASS(check(ttFont))

    # "Font does not contain TrueType instructions enabling
    #  smart dropout control in the 'prep' table program."
    import array

    ttFont["prep"].program.bytecode = array.array("B", [0])
    assert_results_contain(check(ttFont), FAIL, "lacks-smart-dropout")


def test_check_vttclean():
    """There must not be VTT Talk sources in the font."""
    check = CheckTester("vttclean")

    good_font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(good_font))

    bad_font = TEST_FILE("hinting/Roboto-VF.ttf")
    assert_results_contain(check(bad_font), FAIL, "has-vtt-sources")
