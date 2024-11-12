from fontbakery.prelude import check, FAIL


@check(
    id="name_id_1",
    rationale="""
        Presence of a name ID 1 entry is mandatory.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_name_id_1(ttFont):
    """Font has a name with ID 1."""
    if not ttFont["name"].getName(1, 3, 1, 0x409):
        yield FAIL, "Font lacks a name with ID 1."
