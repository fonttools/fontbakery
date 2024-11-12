import re

from fontbakery.prelude import FAIL, PASS, SKIP, Message, check


@check(
    id="unique_glyphnames",
    rationale="""
        Duplicate glyph names prevent font installation on Mac OS X.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    misc_metadata={"affects": [("Mac", "unspecified")]},
)
def check_unique_glyphnames(ttFont):
    """Font contains unique glyph names?"""
    if (
        ttFont.sfntVersion == "\x00\x01\x00\x00"
        and ttFont.get("post")
        and ttFont["post"].formatType == 3
    ):
        yield SKIP, (
            "TrueType fonts with a format 3 post table contain no glyph names."
        )
    elif (
        ttFont.sfntVersion == "OTTO"
        and ttFont.get("CFF2")
        and ttFont.get("post")
        and ttFont["post"].formatType == 3
    ):
        yield SKIP, (
            "OpenType-CFF2 fonts with a format 3 post table contain no glyph names."
        )
    else:
        glyph_names = set()
        dup_glyph_names = set()
        for gname in ttFont.getGlyphOrder():
            # On font load, Fonttools adds #1, #2, ... suffixes to duplicate glyph names
            glyph_name = re.sub(r"#\w+", "", gname)
            if glyph_name in glyph_names:
                dup_glyph_names.add(glyph_name)
            else:
                glyph_names.add(glyph_name)

        if not dup_glyph_names:
            yield PASS, "Glyph names are all unique."
        else:
            yield FAIL, Message(
                "duplicated-glyph-names",
                f"These glyph names occur more than once: {sorted(dup_glyph_names)}",
            )
