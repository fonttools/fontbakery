from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import FeatureRecord

from fontbakery.status import WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)


def test_check_cjk_chws_feature():
    """Does the font contain chws and vchw features?"""
    check = CheckTester("cjk_chws_feature")

    cjk_font = TEST_FILE("cjk/SourceHanSans-Regular.otf")
    ttFont = TTFont(cjk_font)
    assert_results_contain(
        check(ttFont), WARN, "missing-chws-feature", "for Source Han Sans"
    )

    assert_results_contain(
        check(ttFont), WARN, "missing-vchw-feature", "for Source Han Sans"
    )

    # Insert them.
    chws = FeatureRecord()
    chws.FeatureTag = "chws"
    vchw = FeatureRecord()
    vchw.FeatureTag = "vchw"
    ttFont["GPOS"].table.FeatureList.FeatureRecord.extend([chws, vchw])

    assert_PASS(check(ttFont))
