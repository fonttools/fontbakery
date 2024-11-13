from fontbakery.prelude import check, Message, WARN


@check(
    id="opentype/points_out_of_bounds",
    conditions=["is_ttf"],
    rationale="""
        The glyf table specifies a bounding box for each glyph. This check
        ensures that all points in all glyph paths are within the bounding
        box. Glyphs with out-of-bounds points can cause rendering issues in
        some software, and should be corrected.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/735",
)
def check_points_out_of_bounds(ttFont, config):
    """Check for points out of bounds."""
    from fontbakery.utils import pretty_print_list

    passed = True
    out_of_bounds = []
    for glyphName in ttFont["glyf"].keys():
        glyph = ttFont["glyf"][glyphName]
        coords = glyph.getCoordinates(ttFont["glyf"])[0]
        for x, y in coords:
            if (
                round(x) < glyph.xMin
                or round(x) > glyph.xMax
                or round(y) < glyph.yMin
                or round(y) > glyph.yMax
                or abs(x) > 32766
                or abs(y) > 32766
            ):
                passed = False
                out_of_bounds.append((glyphName, x, y))

    if not passed:
        formatted_list = "\t* " + pretty_print_list(config, out_of_bounds, sep="\n\t* ")
        yield WARN, Message(
            "points-out-of-bounds",
            f"The following glyphs have coordinates"
            f" which are out of bounds:\n"
            f"{formatted_list}\n"
            f"\n"
            f"This happens a lot when points are not extremes,"
            f" which is usually bad. However, fixing this alert"
            f" by adding points on extremes may do more harm"
            f" than good, especially with italics,"
            f" calligraphic-script, handwriting, rounded and"
            f" other fonts. So it is common to ignore this message.",
        )
