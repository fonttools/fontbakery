from fontbakery.prelude import check, PASS, FAIL


@check(
    id="microsoft/STAT_table_axis_order",
    conditions=["has_STAT_table"],
    rationale="""
        Validate STAT table axisOrder.
    """,
    # FIXME: Expanding this rationale detailing the reasons why
    #        this ordering is necessary.
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_STAT_table_axis_order(ttFont):
    """STAT table axis order."""

    # Reversed axis order for STAT table - note ital and slnt are rarely in same
    # font but if they are, ital should be last.
    AXIS_ORDER_REVERSED = ["ital", "slnt", "wdth", "wght", "opsz"]

    failed = False
    stat_table = ttFont["STAT"].table
    stat_design_axis = stat_table.DesignAxisRecord.Axis
    stat_design_axis_count = len(stat_design_axis)
    axis_record_list = []
    axis_set = set()
    for stat_axis in stat_design_axis:
        axis_record = {
            "AxisTag": stat_axis.AxisTag,
            "AxisOrdering": stat_axis.AxisOrdering,
        }
        tag = stat_axis.AxisTag
        axis_set.add(tag)
        axis_record_list.append(axis_record)
    sorted_list = sorted(axis_record_list, key=lambda k: k["AxisOrdering"])
    index = stat_design_axis_count - 1
    for axis in AXIS_ORDER_REVERSED:
        if axis in axis_set:
            if sorted_list[index]["AxisTag"] == axis:
                index -= 1
            else:
                failed = True
                yield FAIL, f"STAT table axisOrder for {axis} is not valid"
    if not failed:
        yield PASS, "STAT table axisOrder is valid"
