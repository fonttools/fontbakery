from typing import List

from fontTools.varLib.interpolatable import test as interpolation_test
from fontTools.varLib.interpolatableHelpers import InterpolatableProblem
from fontTools.varLib.models import piecewiseLinearMap

from fontbakery.prelude import check, Message, PASS, WARN
from fontbakery.utils import bullet_list


@check(
    id="interpolation_issues",
    conditions=["is_variable_font", "is_ttf"],
    severity=4,
    rationale="""
        When creating a variable font, the designer must make sure that corresponding
        paths have the same start points across masters, as well as that corresponding
        component shapes are placed in the same order within a glyph across masters.
        If this is not done, the glyph will not interpolate correctly.

        Here we check for the presence of potential interpolation errors using the
        fontTools.varLib.interpolatable module.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3930",
)
def check_interpolation_issues(ttFont, config):
    """Detect any interpolation issues in the font."""

    gvar = ttFont["gvar"]
    # This code copied from fontTools.varLib.interpolatable
    locs = set()
    for variations in gvar.variations.values():
        for var in variations:
            loc = []
            for tag, val in sorted(var.axes.items()):
                loc.append((tag, val[1]))
            locs.add(tuple(loc))

    # Rebuild locs as dictionaries
    new_locs = [{}]
    for loc in sorted(locs, key=lambda v: (len(v), v)):
        location = {}
        for tag, val in loc:
            location[tag] = val
        new_locs.append(location)

    axis_maps = {
        ax.axisTag: {-1: ax.minValue, 0: ax.defaultValue, 1: ax.maxValue}
        for ax in ttFont["fvar"].axes
    }

    locs = new_locs
    glyphsets = [ttFont.getGlyphSet(location=loc, normalized=True) for loc in locs]

    # Name glyphsets by their full location. Different versions of fonttools
    # have differently-typed default names, and so this optional argument must
    # be provided to ensure that returned names are always strings.
    # See: https://github.com/fonttools/fontbakery/issues/4356
    names: List[str] = []
    for glyphset in glyphsets:
        full_location: List[str] = []
        for ax in ttFont["fvar"].axes:
            normalized = glyphset.location.get(ax.axisTag, 0)
            denormalized = int(piecewiseLinearMap(normalized, axis_maps[ax.axisTag]))
            full_location.append(f"{ax.axisTag}={denormalized}")
        names.append(",".join(full_location))

    # Inputs are ready; run the tests.
    results = interpolation_test(glyphsets, names=names)

    # Most of the potential problems varLib.interpolatable finds can't
    # exist in a built binary variable font. We focus on those which can.
    report = []
    for glyph, glyph_problems in results.items():
        for p in glyph_problems:
            if p["type"] == InterpolatableProblem.CONTOUR_ORDER:
                report.append(
                    f"Contour order differs in glyph '{glyph}':"
                    f" {p['value_1']} in {p['master_1']},"
                    f" {p['value_2']} in {p['master_2']}."
                )
            elif p["type"] == InterpolatableProblem.WRONG_START_POINT:
                report.append(
                    f"Contour {p['contour']} start point"
                    f" differs in glyph '{glyph}' between"
                    f" location {p['master_1']} and"
                    f" location {p['master_2']}"
                )
            elif p["type"] == InterpolatableProblem.KINK:
                report.append(
                    f"Contour {p['contour']} point {p['value']} in glyph '{glyph}' "
                    f"has a kink between location {p['master_1']} and"
                    f" location {p['master_2']}"
                )
            elif p["type"] == InterpolatableProblem.UNDERWEIGHT:
                report.append(
                    f"Contour {p['contour']} in glyph '{glyph}':"
                    f" becomes underweight between {p['master_1']}"
                    f" and {p['master_2']}."
                )
            elif p["type"] == InterpolatableProblem.OVERWEIGHT:
                report.append(
                    f"Contour {p['contour']} in glyph '{glyph}':"
                    f" becomes overweight between {p['master_1']}"
                    f" and {p['master_2']}."
                )

    if not report:
        yield PASS, "No interpolation issues found"
    else:
        yield WARN, Message(
            "interpolation-issues",
            f"Interpolation issues were found in the font:\n\n"
            f"{bullet_list(config, report)}",
        )
