from fontbakery.prelude import check, PASS, WARN, FAIL


@check(
    id="microsoft/STAT_axis_values",
    conditions=["has_STAT_table"],
    rationale="""
        Check whether STAT axis values are unique.
    """,  # FIXME: Expand this rationale detailing why the values must be unique.
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_STAT_axis_values(ttFont):
    """STAT axis values must be unique."""
    stat_table = ttFont["STAT"].table
    axis_values_format1 = set()  # set of (axisIndex, axisValue) tuples
    failed = False
    if stat_table.AxisValueArray is None:
        yield WARN, "STAT no axis values"
        return
    for axis_value_record in stat_table.AxisValueArray.AxisValue:
        if axis_value_record.Format == 1:
            axis_index = axis_value_record.AxisIndex
            axis_value = axis_value_record.Value
            key = (axis_index, axis_value)
            if key in axis_values_format1:
                failed = True
                yield FAIL, (
                    f"axis value {axis_value} (format 1) "
                    f"for axis #{axis_index} is not unique"
                )
            axis_values_format1.add(key)
    if not failed:
        yield PASS, "STAT axis values (format 1) are unique"
