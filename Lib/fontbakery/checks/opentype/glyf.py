from fontTools.ttLib import TTLibError

from fontbakery.message import Message
from fontbakery.callable import check
from fontbakery.status import FAIL, PASS, WARN


@check(
    id="opentype/glyf_unused_data",
    rationale="""
        This check validates the structural integrity of the glyf table,
        by checking that all glyphs referenced in the loca table are
        actually present in the glyf table and that there is no unused
        data at the end of the glyf table. A failure here indicates a
        problem with the font compiler.
    """,
    conditions=["is_ttf"],
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_glyf_unused_data(ttFont):
    """Is there any unused data at the end of the glyf table?"""
    expected_glyphs = len(ttFont.getGlyphOrder())
    try:
        actual_glyphs = len(ttFont["glyf"].glyphs)
        diff = actual_glyphs - expected_glyphs

        if diff < 0:
            yield FAIL, Message(
                "unreachable-data",
                f"Glyf table has unreachable data at the end of the table."
                f" Expected glyf table length {expected_glyphs} (from loca"
                f" table), got length {actual_glyphs}"
                f" (difference: {diff})",
            )
        elif not diff:  # negative diff -> exception below
            yield PASS, "There is no unused data at the end of the glyf table."
        else:
            raise Exception("Bug: fontTools did not raise an expected exception.")
    except TTLibError as error:
        if "not enough 'glyf' table data" in format(error):
            yield FAIL, Message(
                "missing-data",
                f"Loca table references data beyond"
                f" the end of the glyf table."
                f" Expected glyf table length {expected_glyphs}"
                f" (from loca table).",
            )
        else:
            raise Exception("Bug: Unexpected fontTools exception.")


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


@check(
    id="opentype/glyf_non_transformed_duplicate_components",
    rationale="""
        There have been cases in which fonts had faulty double quote marks, with each
        of them containing two single quote marks as components with the same
        x, y coordinates which makes them visually look like single quote marks.

        This check ensures that glyphs do not contain duplicate components
        which have the same x,y coordinates.
    """,
    conditions=["is_ttf"],
    proposal="https://github.com/fonttools/fontbakery/pull/2709",
)
def check_glyf_non_transformed_duplicate_components(ttFont, config):
    """
    Check glyphs do not have duplicate components which have the same x,y coordinates.
    """
    from fontbakery.utils import pretty_print_list

    failed = []
    for glyph_name in ttFont["glyf"].keys():
        glyph = ttFont["glyf"][glyph_name]
        if not glyph.isComposite():
            continue

        seen = []
        for comp in glyph.components:
            comp_info = {
                "glyph": glyph_name,
                "component": comp.glyphName,
                "x": comp.x,
                "y": comp.y,
            }
            if comp_info in seen:
                failed.append(comp_info)
            else:
                seen.append(comp_info)
    if failed:
        formatted_list = "\t* " + pretty_print_list(config, failed, sep="\n\t* ")
        yield FAIL, Message(
            "found-duplicates",
            f"The following glyphs have duplicate components which"
            f" have the same x,y coordinates:\n"
            f"{formatted_list}",
        )
