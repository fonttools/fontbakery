import os

from fontbakery.prelude import check, Message, FAIL


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
