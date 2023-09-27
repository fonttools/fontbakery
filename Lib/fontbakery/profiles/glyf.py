from fontTools.ttLib import TTLibError

from fontbakery.message import Message
from fontbakery.callable import check
from fontbakery.status import FAIL, PASS, WARN

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory  # noqa:F401 pylint:disable=W0611


@check(
    id="com.google.fonts/check/glyf_unused_data",
    conditions=["is_ttf"],
    proposal="legacy:check/069",
)
def com_google_fonts_check_glyf_unused_data(ttFont):
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
    id="com.google.fonts/check/points_out_of_bounds",
    conditions=["is_ttf"],
    proposal="https://github.com/fonttools/fontbakery/issues/735",
)
def com_google_fonts_check_points_out_of_bounds(ttFont, config):
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
    else:
        yield PASS, "All glyph paths have coordinates within bounds!"


@check(
    id="com.google.fonts/check/glyf_non_transformed_duplicate_components",
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
def com_google_fonts_check_glyf_non_transformed_duplicate_components(ttFont, config):
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
    else:
        yield PASS, (
            "Glyphs do not contain duplicate components which have"
            " the same x,y coordinates."
        )
