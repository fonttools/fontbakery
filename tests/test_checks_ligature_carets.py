from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    # assert_PASS,  FIXME: We must also have PASS test-cases!
    assert_results_contain,
    CheckTester,
    TEST_FILE,
    MockFont,
)
from fontbakery.status import FAIL, WARN, SKIP


def test_check_ligature_carets():
    """Is there a caret position declared for every ligature?"""
    check = CheckTester("ligature_carets")

    # Our reference Mada Medium doesn't have a GSUB 'liga' feature, so it is skipped
    # because of an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: ligature_glyphs" in msg

    # Simulate an error coming from the 'ligature_glyphs' condition;
    # this is to exercise the 'malformed' code path.
    font = TEST_FILE("mada/Mada-Medium.ttf")
    msg = assert_results_contain(
        check(MockFont(file=font, ligature_glyphs=-1)), FAIL, "malformed"
    )
    assert "Failed to lookup ligatures. This font file seems to be malformed." in msg

    # SourceSansPro Bold has ligatures and GDEF table, but lacks caret position data.
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf"))
    msg = assert_results_contain(check(ttFont), WARN, "lacks-caret-pos")
    assert msg == (
        "This font lacks caret position values"
        " for ligature glyphs on its GDEF table."
    )

    # Remove the GDEF table to exercise the 'GDEF-missing' code path.
    del ttFont["GDEF"]
    msg = assert_results_contain(check(ttFont), WARN, "GDEF-missing")
    assert "GDEF table is missing, but it is mandatory" in msg

    # TODO: test the following code-paths:
    # - WARN "incomplete-caret-pos-data"
    # - PASS (We currently lack a reference family that PASSes this check!)
