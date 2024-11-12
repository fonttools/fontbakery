from fontbakery.prelude import check, FAIL


@check(
    id="name_id_2",
    rationale="""
        Presence of a name ID 2 entry is mandatory.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_name_id_2(ttFont):
    """Font has a name with ID 2."""
    if not ttFont["name"].getName(2, 3, 1, 0x409):
        yield FAIL, "Font lacks a name with ID 2."
