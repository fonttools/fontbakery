from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    # assert_PASS,  FIXME: We must also have PASS test-cases!
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import WARN, SKIP


@check_id("ligature_carets")
def test_check_ligature_carets(check):
    """Is there a caret position declared for every ligature?"""

    # Our reference Mada Medium doesn't have a GSUB 'liga' feature, so it is skipped
    # because of an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "no-ligatures")

    # SourceSansPro Bold has ligatures and GDEF table, but lacks caret position data.
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf"))
    msg = assert_results_contain(check(ttFont), WARN, "lacks-caret-pos")
    assert msg == (
        "This font lacks caret position values"
        " for ligature glyphs on its GDEF table."
    )

    # TODO:
    # assert_results_contain(check(ttFont), WARN, "incomplete-caret-pos-data")
