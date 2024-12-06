from collections import defaultdict

from fontbakery.prelude import check, Message, FAIL, SKIP
from fontbakery.utils import all_kerning, bullet_list


@check(
    id="varfont/duplexed_axis_reflow",
    rationale="""
        Certain axes, such as grade (GRAD) or roundness (ROND), should not
        change any advanceWidth or kerning data across the font's design space.
        This is because altering the advance width of glyphs can cause text reflow.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3187",
)
def check_varfont_duplexed_axis_reflow(font, ttFont, config):
    """Ensure VFs with duplexed axes do not vary horizontal advance."""

    DUPLEXED_AXES = {"GRAD", "ROND"}
    relevant_axes = set(font.axes_by_tag.keys()) & DUPLEXED_AXES

    if not (relevant_axes):
        yield SKIP, Message("no-relevant-axes", "This font has no duplexed axes")
        return

    gvar = ttFont["gvar"]
    bad_glyphs_by_axis = defaultdict(set)
    for glyph, deltas in gvar.variations.items():
        for delta in deltas:
            for duplexed_axis in relevant_axes:
                if duplexed_axis not in delta.axes:
                    continue
                if any(c is not None and c != (0, 0) for c in delta.coordinates[-4:]):
                    bad_glyphs_by_axis[duplexed_axis].add(glyph)

    for duplexed_axis, bad_glyphs in bad_glyphs_by_axis.items():
        bad_glyphs_list = bullet_list(config, sorted(bad_glyphs))
        yield FAIL, Message(
            f"{duplexed_axis.lower()}-causes-reflow",
            f"The following glyphs have variation in horizontal"
            f" advance due to duplexed axis {duplexed_axis}:\n"
            f"{bad_glyphs_list}",
        )

    # Determine if any kerning rules vary the horizontal advance.
    # This is going to get grubby.

    if "GDEF" in ttFont and hasattr(ttFont["GDEF"].table, "VarStore"):
        effective_regions = set()
        varstore = ttFont["GDEF"].table.VarStore
        regions = varstore.VarRegionList.Region
        for axis in relevant_axes:
            axis_index = [x.axisTag == axis for x in ttFont["fvar"].axes].index(True)
            for ix, region in enumerate(regions):
                axis_tent = region.VarRegionAxis[axis_index]
                effective = (
                    axis_tent.StartCoord != axis_tent.PeakCoord
                    or axis_tent.PeakCoord != axis_tent.EndCoord
                )
                if effective:
                    effective_regions.add(ix)

        if effective_regions:
            kerning = all_kerning(ttFont)
            for left, right, v1, v2 in kerning:
                if v1 and hasattr(v1, "XAdvDevice") and v1.XAdvDevice:
                    variation = [v1.XAdvDevice.StartSize, v1.XAdvDevice.EndSize]
                    regions = varstore.VarData[variation[0]].VarRegionIndex
                    if any(region in effective_regions for region in regions):
                        deltas = varstore.VarData[variation[0]].Item[variation[1]]
                        effective_deltas = [
                            deltas[ix]
                            for ix, region in enumerate(regions)
                            if region in effective_regions
                        ]
                        if any(x for x in effective_deltas):
                            yield FAIL, Message(
                                "duplexed-kern-causes-reflow",
                                f"Kerning rules cause variation in"
                                f" horizontal advance on a duplexed axis"
                                f" (e.g. {left}/{right})",
                            )
                            break
