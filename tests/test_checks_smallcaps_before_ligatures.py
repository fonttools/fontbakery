from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import Feature, FeatureRecord

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


@check_id("smallcaps_before_ligatures")
def test_check_smallcaps_before_ligatures(check):
    """Ensure 'smcp' lookups are defined before 'liga' lookups in the 'GSUB' table."""

    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    smcp_feature = Feature()
    smcp_feature.LookupListIndex = [0]
    liga_feature = Feature()
    liga_feature.LookupListIndex = [1]

    smcp_record = FeatureRecord()
    smcp_record.FeatureTag = "smcp"
    smcp_record.Feature = smcp_feature

    liga_record = FeatureRecord()
    liga_record.FeatureTag = "liga"
    liga_record.Feature = liga_feature

    # Test both 'smcp' and 'liga' lookups are present
    ttFont["GSUB"].table.FeatureList.FeatureRecord = [smcp_record, liga_record]
    assert_PASS(check(ttFont))

    # Test 'liga' lookup before 'smcp' lookup
    smcp_feature.LookupListIndex = [1]
    liga_feature.LookupListIndex = [0]
    assert_results_contain(check(ttFont), FAIL, "feature-ordering")
