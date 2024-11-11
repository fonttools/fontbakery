from unittest.mock import MagicMock

from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)


def newTable(tag):
    obj = MagicMock()
    obj.loadData = lambda *args: b"foo"
    return obj


@check_id("unwanted_tables")
def test_check_unwanted_tables(check):
    """Are there unwanted tables ?"""
    unwanted_tables = [
        "DSIG",
        "FFTM",  # FontForge
        "TTFA",  # TTFAutohint
        "TSI0",  # TSI* = VTT
        "TSI1",
        "TSI2",
        "TSI3",
        "TSI5",
        "TSIC",
        "TSIV",
        "TSIP",
        "TSIS",
        "TSID",
        "TSIJ",
        "TSIB",
        "TSI3",
        "TSI5",
        "prop",  # FIXME: Why is this one unwanted?
    ]
    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    # We now add unwanted tables one-by-one to validate the FAIL code-path:
    for unwanted in unwanted_tables:
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        ttFont.reader.tables[unwanted] = newTable(unwanted)
        assert_results_contain(
            check(ttFont),
            FAIL,
            "unwanted-tables",
            f"with unwanted table {unwanted} ...",
        )
