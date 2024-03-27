from fontbakery.callable import check
from fontbakery.status import FAIL
from fontbakery.message import Message


@check(
    id="com.google.fonts/check/loca/maxp_num_glyphs",
    conditions=["is_ttf"],
    proposal="legacy:check/180",
    rationale="""
        The 'maxp' table contains various statistics about the font, including the
        number of glyphs in the font. The 'loca' table contains the offsets to the
        locations of the glyphs in the font. The number of offsets in the 'loca' table
        should match the number of glyphs in the 'maxp' table. A failure here indicates
        a problem with the font compiler.
    """,
)
def com_google_fonts_check_loca_maxp_num_glyphs(ttFont):
    """Does the number of glyphs in the loca table match the maxp table?"""
    if len(ttFont["loca"]) < (ttFont["maxp"].numGlyphs + 1):
        yield FAIL, Message(
            "corrupt", 'Corrupt "loca" table or wrong numGlyphs in "maxp" table.'
        )
