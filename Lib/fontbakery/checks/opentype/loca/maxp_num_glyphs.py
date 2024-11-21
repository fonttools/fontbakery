from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/loca/maxp_num_glyphs",
    conditions=["is_ttf"],
    rationale="""
        The 'maxp' table contains various statistics about the font, including the
        number of glyphs in the font. The 'loca' table contains the offsets to the
        locations of the glyphs in the font. The number of offsets in the 'loca' table
        should match the number of glyphs in the 'maxp' table. A failure here indicates
        a problem with the font compiler.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_loca_maxp_num_glyphs(ttFont):
    """Does the number of glyphs in the loca table match the maxp table?"""
    if len(ttFont["loca"]) < (ttFont["maxp"].numGlyphs + 1):
        yield FAIL, Message(
            "corrupt", 'Corrupt "loca" table or wrong numGlyphs in "maxp" table.'
        )
