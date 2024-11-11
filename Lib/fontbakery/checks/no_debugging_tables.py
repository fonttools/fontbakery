from fontbakery.prelude import check, Message, WARN


@check(
    id="no_debugging_tables",
    rationale="""
        Tables such as `Debg` are useful in the pre-production stages of font
        development, but add unnecessary bloat to a production font and should
        be removed before release.
    """,
    severity=6,
    proposal="https://github.com/fonttools/fontbakery/issues/3357",
)
def check_no_debugging_tables(ttFont):
    """Ensure fonts do not contain any pre-production tables."""

    DEBUGGING_TABLES = ["Debg", "FFTM"]
    found = [t for t in DEBUGGING_TABLES if t in ttFont]
    if found:
        tables_list = ", ".join(found)
        yield WARN, Message(
            "has-debugging-tables",
            f"This font file contains the following"
            f" pre-production tables: {tables_list}",
        )
