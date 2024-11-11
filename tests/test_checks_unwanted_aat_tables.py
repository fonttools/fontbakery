from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    TEST_FILE,
    assert_PASS,
    assert_results_contain,
)
from fontbakery.status import FAIL


@check_id("unwanted_aat_tables")
def test_check_unwanted_aat_tables(check):
    """Are there unwanted Apple tables ?"""

    unwanted_tables = [
        "EBSC",
        "Zaph",
        "acnt",
        "ankr",
        "bdat",
        "bhed",
        "bloc",
        "bmap",
        "bsln",
        "fdsc",
        "feat",
        "fond",
        "gcid",
        "just",
        "kerx",
        "lcar",
        "ltag",
        "mort",
        "morx",
        "opbd",
        "prop",
        "trak",
        "xref",
    ]
    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    # We now add unwanted tables one-by-one to validate the FAIL code-path:
    for unwanted in unwanted_tables:
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        ttFont.reader.tables[unwanted] = "foo"
        assert_results_contain(
            check(ttFont),
            FAIL,
            "has-unwanted-tables",
            f"with unwanted table {unwanted} ...",
        )
