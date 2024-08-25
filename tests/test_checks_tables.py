from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    TEST_FILE,
    CheckTester,
    assert_PASS,
    assert_results_contain,
)
from fontbakery.status import FAIL, WARN


def test_check_unwanted_aat_tables():
    """Are there unwanted Apple tables ?"""
    check = CheckTester("unwanted_aat_tables")

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


def test_check_no_debugging_tables():
    """Ensure fonts do not contain any preproduction tables."""
    check = CheckTester("no_debugging_tables")

    ttFont = TTFont(TEST_FILE("overpassmono/OverpassMono-Regular.ttf"))
    assert_results_contain(check(ttFont), WARN, "has-debugging-tables")

    del ttFont["FFTM"]
    assert_PASS(check(ttFont))
