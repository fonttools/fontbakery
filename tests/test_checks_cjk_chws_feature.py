from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import FeatureRecord

from conftest import check_id
from fontbakery.status import WARN
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("cjk_chws_feature")
def test_check_cjk_chws_feature(check):
    """Does the font contain chws and vchw features?"""

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
