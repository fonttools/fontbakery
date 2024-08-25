from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    # assert_PASS,  FIXME: We must also have PASS test-cases!
    assert_results_contain,
    CheckTester,
    TEST_FILE,
    MockFont,
)
from fontbakery.status import FAIL, WARN, SKIP


def test_check_kerning_for_non_ligated_sequences():
    """Is there kerning info for non-ligated sequences ?"""
    check = CheckTester("kerning_for_non_ligated_sequences")

    # Our reference Mada Medium doesn't have a GSUB 'liga' feature, so it is skipped
    # because of an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: ligatures" in msg

    # Simulate an error coming from the 'ligatures' condition;
    # this is to exercise the 'malformed' code path.
    font = TEST_FILE("mada/Mada-Medium.ttf")
    msg = assert_results_contain(
        check(MockFont(file=font, ligatures=-1)), FAIL, "malformed"
    )
    assert "Failed to lookup ligatures. This font file seems to be malformed." in msg

    # And Merriweather Regular doesn't have a GPOS 'kern' feature, so it is skipped
    # because of an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: has_kerning_info" in msg

    # SourceSansPro Bold is known to not kern the non-ligated glyph sequences.
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf"))
    msg = assert_results_contain(check(ttFont), WARN, "lacks-kern-info")
    assert msg == (
        "GPOS table lacks kerning info for the following non-ligated sequences:\n\n"
        "\t- f + f\n\n\t- f + t"
    )

    # Simulate handling of multi-component ligatures
    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf")
    msg = assert_results_contain(
        check(MockFont(file=font, ligatures={"f": [["f", "i"], ["f", "l"]]})),
        WARN,
        "lacks-kern-info",
    )
    assert msg == (
        "GPOS table lacks kerning info for the following non-ligated sequences:\n\n"
        "\t- f + f\n\n\t- f + i\n\n\t- f + l"
    )
