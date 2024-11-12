from fontTools.pens.boundsPen import BoundsPen
from fontbakery.prelude import check, Message, PASS, WARN, SKIP


@check(
    id="caps_vertically_centered",
    rationale="""
        This check suggests one possible approach to designing vertical metrics,
        but can be ingnored if you follow a different approach.
        In order to center text in buttons, lists, and grid systems
        with minimal additional CSS work, the uppercase glyphs should be
        vertically centered in the em box.
        This check mainly applies to Latin, Greek, Cyrillic, and other similar scripts.
        For non-latin scripts like Arabic, this check might not be applicable.
        There is a detailed description of this subject at:
        https://x.com/romanshamin_en/status/1562801657691672576
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4139",
)
def check_caps_vertically_centered(ttFont):
    """Check if uppercase glyphs are vertically centered."""

    from copy import deepcopy

    ttFont_copy = deepcopy(ttFont)

    SOME_UPPERCASE_GLYPHS = ["A", "B", "C", "D", "E", "H", "I", "M", "O", "S", "T", "X"]
    glyphSet = ttFont_copy.getGlyphSet()

    for glyphname in SOME_UPPERCASE_GLYPHS:
        if glyphname not in glyphSet.keys():
            yield SKIP, Message(
                "lacks-ascii",
                "The implementation of this check relies on a few samples"
                " of uppercase latin characters that are not available in this font.",
            )
            return

    highest_point_list = []
    lowest_point_list = []
    for glyphName in SOME_UPPERCASE_GLYPHS:
        pen = BoundsPen(glyphSet)
        glyphSet[glyphName].draw(pen)
        _, lowest_point, _, highest_point = pen.bounds
        highest_point_list.append(highest_point)
        lowest_point_list.append(lowest_point)

    upm = ttFont_copy["head"].unitsPerEm
    line_spacing_factor = 1.20
    error_margin = (line_spacing_factor * upm) * 0.18
    average_cap_height = sum(highest_point_list) / len(highest_point_list)
    average_descender = sum(lowest_point_list) / len(lowest_point_list)

    top_margin = ttFont["hhea"].ascent - average_cap_height
    bottom_margin = abs(ttFont["hhea"].descent) + average_descender

    difference = abs(top_margin - bottom_margin)

    if difference > error_margin:
        yield WARN, Message(
            "vertical-metrics-not-centered",
            "Uppercase glyphs are not vertically centered in the em box.",
        )
    else:
        yield PASS, "Uppercase glyphs are vertically centered in the em box."
