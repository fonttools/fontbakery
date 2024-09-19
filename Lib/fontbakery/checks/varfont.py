import os
from collections import defaultdict

from fontbakery.prelude import check, condition, Message, WARN, FAIL, SKIP
from fontbakery.testable import Font
from fontbakery.utils import bullet_list


@check(
    id="fvar_name_entries",
    conditions=["is_variable_font"],
    rationale="""
        The purpose of this check is to make sure that all name entries referenced
        by variable font instances do exist in the name table.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2069",
)
def check_fvar_name_entries(ttFont):
    """All name entries referenced by fvar instances exist on the name table?"""

    for instance in ttFont["fvar"].instances:
        entries = [
            entry
            for entry in ttFont["name"].names
            if entry.nameID == instance.subfamilyNameID
        ]
        if len(entries) == 0:
            yield FAIL, Message(
                "missing-name",
                f"Named instance with coordinates {instance.coordinates}"
                f" lacks an entry on the name table"
                f" (nameID={instance.subfamilyNameID}).",
            )


@check(
    id="varfont/consistent_axes",
    rationale="""
        In order to facilitate the construction of intuitive and friendly user
        interfaces, all variable font files in a given family should have the same set
        of variation axes. Also, each axis must have a consistent setting of min/max
        value ranges accross all the files.
    """,
    conditions=["VFs"],
    proposal="https://github.com/fonttools/fontbakery/issues/2810",
)
def check_varfont_consistent_axes(VFs):
    """Ensure that all variable font files have the same set of axes and axis ranges."""
    ref_ranges = {}
    for vf in VFs:
        ref_ranges.update(
            {k.axisTag: (k.minValue, k.maxValue) for k in vf["fvar"].axes}
        )

    for vf in VFs:
        for axis in ref_ranges:
            if axis not in map(lambda x: x.axisTag, vf["fvar"].axes):
                yield FAIL, Message(
                    "missing-axis",
                    f"{os.path.basename(vf.reader.file.name)}:"
                    f" lacks a '{axis}' variation axis.",
                )

    expected_ranges = {
        axis: {
            (
                vf["fvar"].axes[vf["fvar"].axes.index(axis)].minValue,
                vf["fvar"].axes[vf["fvar"].axes.index(axis)].maxValue,
            )
            for vf in VFs
        }
        for axis in ref_ranges
        if axis in vf["fvar"].axes
    }

    for axis, ranges in expected_ranges:
        if len(ranges) > 1:
            yield FAIL, Message(
                "inconsistent-axis-range",
                "Axis 'axis' has diverging ranges accross the family: {ranges}.",
            )


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
    from fontbakery.utils import all_kerning, pretty_print_list

    DUPLEXED_AXES = {"GRAD", "ROND"}
    relevant_axes = set(font.axes_by_tag.keys()) & DUPLEXED_AXES
    relevant_axes_display = " or ".join(relevant_axes)

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
        bad_glyphs_list = pretty_print_list(config, sorted(bad_glyphs))
        yield FAIL, Message(
            f"{duplexed_axis.lower()}-causes-reflow",
            "The following glyphs have variation in horizontal"
            f" advance due to duplexed axis {duplexed_axis}:"
            f" {bad_glyphs_list}",
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

        # Some regions vary *something* along the axis. But what?
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
                                f" horizontal advance on a duplexed axis "
                                f" ({relevant_axes_display})"
                                f" (e.g. {left}/{right})",
                            )
                            break


@check(
    id="varfont/unsupported_axes",
    rationale="""
        The 'ital' axis is not supported yet in Google Chrome.

        For the time being, we need to ensure that VFs do not contain this axis.
        Once browser support is better, we can deprecate this check.

        For more info regarding browser support, see:
        https://arrowtype.github.io/vf-slnt-test/
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2866",
)
def check_varfont_unsupported_axes(font):
    """Ensure VFs do not contain (yet) the ital axis."""
    if font.ital_axis:
        yield FAIL, Message(
            "unsupported-ital",
            'The "ital" axis is not yet well supported on Google Chrome.',
        )


@check(
    id="mandatory_avar_table",
    rationale="""
        Most variable fonts should include an avar table to correctly define
        axes progression rates.

        For example, a weight axis from 0% to 100% doesn't map directly to 100 to 1000,
        because a 10% progression from 0% may be too much to define the 200,
        while 90% may be too little to define the 900.

        If the progression rates of axes is linear, this check can be ignored.
        Fontmake will also skip adding an avar table if the progression rates
        are linear. However, it is still recommended that designers visually proof
        each instance is at the expected weight, width etc.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3100"
    # NOTE: This is a high-priority WARN.
)
def check_mandatory_avar_table(ttFont):
    """Ensure variable fonts include an avar table."""
    if "avar" not in ttFont:
        yield WARN, Message(
            "missing-avar",
            (
                "This variable font does not have an avar table."
                " Most variable fonts should include an avar table to correctly"
                " define axes progression rates."
            ),
        )


@condition(Font)
def uharfbuzz_blob(font):
    import uharfbuzz as hb

    return hb.Blob.from_file_path(font.file)


@check(
    id="varfont/instances_in_order",
    rationale="""
        Ensure that the fvar table instances are in ascending order of weight.
        Some software, such as Canva, displays the instances in the order they
        are defined in the fvar table, which can lead to confusion if the
        instances are not in order of weight.
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/3334",
    severity=2,  # It only affects a few applications
    conditions=["has_wght_axis"],
)
def check_varfont_instances_in_order(ttFont, config):
    """Ensure the font's instances are in the correct order."""

    coords = [i.coordinates for i in ttFont["fvar"].instances]
    # Partition into sub-lists based on the other axes values.
    # e.g. "Thin Regular", "Bold Regular", "Thin Condensed", "Bold Condensed"
    # becomes [ ["Thin Regular", "Bold Regular"], ["Thin Condensed", "Bold Condensed"] ]
    sublists = [[]]
    last_non_wght = {}
    for coord in coords:
        non_wght = {k: v for k, v in coord.items() if k != "wght"}
        if non_wght != last_non_wght:
            sublists.append([])
            last_non_wght = non_wght
        sublists[-1].append(coord)

    for lst in sublists:
        wght_values = [i["wght"] for i in lst]
        if wght_values != sorted(wght_values):
            yield FAIL, Message(
                "instances-not-in-order",
                "The fvar table instances are not in ascending order of weight:\n"
                + bullet_list(config, lst),
            )
