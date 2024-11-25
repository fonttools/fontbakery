from fontbakery.prelude import check, PASS, WARN, FAIL


@check(
    id="microsoft/STAT_table_eliding_bit",
    conditions=["has_STAT_table"],
    rationale="""
        Validate STAT table eliding bit.
    """,  # FIXME: Expand this rationale text.
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_STAT_table_eliding_bit(ttFont):
    """Validate STAT table eliding bit"""
    stat_table = ttFont["STAT"].table
    name_table = ttFont["name"]
    failed = False
    if stat_table.AxisValueArray is None:
        yield WARN, "STAT no axis values"
        return
    for axis_value_record in stat_table.AxisValueArray.AxisValue:
        if axis_value_record.Format in [1, 2, 3, 4]:
            value_name_id = axis_value_record.ValueNameID
            axis_value_flags = axis_value_record.Flags
            value_name = name_table.getName(value_name_id, 3, 1, 0x409).toUnicode()
            if value_name == "Regular" and axis_value_flags & 0x0002 == 0:
                failed = True
                yield FAIL, (
                    f"axis value {value_name} "
                    f"(format {axis_value_record.Format}) is not elided"
                )
    if not failed:
        yield PASS, "STAT table eliding bit is valid"
