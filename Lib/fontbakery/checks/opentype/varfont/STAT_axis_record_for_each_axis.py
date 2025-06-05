from fontbakery.prelude import FAIL, PASS, SKIP, Message, check
from fontbakery.utils import bullet_list


@check(
    id="opentype/varfont/STAT_axis_record_for_each_axis",
    rationale="""
        According to the OpenType spec, there must be an Axis Record
        for every axis defined in the fvar table.

        https://docs.microsoft.com/en-us/typography/opentype/spec/stat#axis-records
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3017",
)
def check_varfont_STAT_axis_record_for_each_axis(ttFont, config):
    """All fvar axes have a correspondent Axis Record on STAT table?"""
    fvar_axes = set(a.axisTag for a in ttFont["fvar"].axes)
    if "STAT" not in ttFont:
        yield SKIP, Message("missing-axis-records", "The font has no STAT table.")
        return

    STAT_axes = set(a.AxisTag for a in ttFont["STAT"].table.DesignAxisRecord.Axis)
    missing_axes = fvar_axes - STAT_axes
    if len(missing_axes) > 0:
        yield FAIL, Message(
            "missing-axis-records",
            f"STAT table is missing Axis Records for the following axes:\n\n"
            f"{bullet_list(config, sorted(missing_axes))}",
        )
    else:
        yield PASS, "STAT table has all necessary Axis Records."
