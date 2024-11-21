from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/maxadvancewidth",
    rationale="""
        The 'hhea' table contains a field which specifies the maximum
        advance width. This value should be consistent with the maximum
        advance width of all glyphs specified in the 'hmtx' table.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_maxadvancewidth(ttFont):
    """MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables?"""

    required_tables = {"hhea", "hmtx"}
    missing_tables = sorted(required_tables - set(ttFont.keys()))
    if missing_tables:
        for table_tag in missing_tables:
            yield FAIL, Message("lacks-table", f"Font lacks '{table_tag}' table.")
        return

    hhea_advance_width_max = ttFont["hhea"].advanceWidthMax
    hmtx_advance_width_max = None
    for g in ttFont["hmtx"].metrics.values():
        if hmtx_advance_width_max is None:
            hmtx_advance_width_max = max(0, g[0])
        else:
            hmtx_advance_width_max = max(g[0], hmtx_advance_width_max)

    if hmtx_advance_width_max != hhea_advance_width_max:
        yield FAIL, Message(
            "mismatch",
            f"AdvanceWidthMax mismatch:"
            f" expected {hmtx_advance_width_max} (from hmtx);"
            f" got {hhea_advance_width_max} (from hhea)",
        )
