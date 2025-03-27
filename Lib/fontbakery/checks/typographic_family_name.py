from fontbakery.prelude import check, FAIL, Message


@check(
    id="typographic_family_name",
    rationale="""
        Check whether Name ID 16 (Typographic Family name) is consistent
        across the set of fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_typographic_family_name(ttFonts):
    """Typographic Family name consistency."""
    values = set()
    for ttFont in ttFonts:
        name_record = ttFont["name"].getName(16, 3, 1, 0x0409)
        if name_record is None:
            name_record = ttFont["name"].getName(1, 3, 1, 0x0409)

        values.add(name_record.toUnicode())
    if len(values) != 1:
        yield FAIL, Message(
            "incosistent-family-name",
            f"Name ID 16 (Typographic Family name) is not consistent "
            f"across fonts. Values found: {sorted(values)}",
        )
