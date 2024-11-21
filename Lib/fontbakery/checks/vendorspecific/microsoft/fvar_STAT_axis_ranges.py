from fontbakery.prelude import check, PASS, WARN, FAIL


@check(
    id="microsoft/fvar_STAT_axis_ranges",
    conditions=["has_STAT_table", "is_variable_font"],
    rationale="""
        Check fvar named instance axis values lie within a single STAT axis range.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_fvar_STAT_axis_ranges(ttFont):
    """Requirements for named instances and STAT axis ranges."""
    stat_table = ttFont["STAT"].table
    stat_design_axis = stat_table.DesignAxisRecord.Axis
    stat_design_axis_count = len(stat_design_axis)
    fvar_table = ttFont["fvar"]
    failed = False
    if stat_table.AxisValueArray is None:
        yield WARN, "STAT no axis values"
        return
    # for each named instance in fvar
    for fvar_instance in fvar_table.instances:
        # for each axis of the named instance
        # first look for an exact match format 4
        format4_match = False
        instance_coord_set = set(fvar_instance.coordinates.items())
        for stat_axis_value_record in stat_table.AxisValueArray.AxisValue:
            if stat_axis_value_record.Format == 4:
                stat_coord_set = set()
                for axis_index, axis_value in stat_axis_value_record.AxisValue.items():
                    if axis_index >= stat_design_axis_count:
                        failed = True
                        yield FAIL, (
                            f"axis index {axis_index} (format 4) "
                            f"is greater than STAT axis count {stat_design_axis_count}"
                        )
                    stat_axis = stat_design_axis[axis_index].AxisTag
                    stat_coord_set.add((stat_axis, axis_value))
                if instance_coord_set == stat_coord_set:
                    format4_match = True
                    break
        # if no exact match for format 4, look for matches by axis in formats 1, 2 and 3
        if not format4_match:
            for instance_axis, instance_value in fvar_instance.coordinates.items():
                found_instance_axis = False
                # for each axis value record in STAT
                for stat_axis_value_record in stat_table.AxisValueArray.AxisValue:
                    # format 1, format 3
                    if stat_axis_value_record.Format in {1, 3}:
                        axis_index = stat_axis_value_record.AxisIndex
                        axis_value = stat_axis_value_record.Value
                        if axis_index >= stat_design_axis_count:
                            failed = True
                            yield FAIL, (
                                f"axis index {axis_index} (format {stat_axis_value_record.Format}) "
                                f"is greater than STAT axis count {stat_design_axis_count}"
                            )
                        stat_axis = stat_design_axis[axis_index].AxisTag
                        if instance_axis == stat_axis and instance_value == axis_value:
                            if found_instance_axis:
                                failed = True
                                yield FAIL, (
                                    f"axis value {instance_value} "
                                    f"(format {stat_axis_value_record.Format}) "
                                    f"for axis {instance_axis} is not unique"
                                )
                            found_instance_axis = True
                    # format 2
                    elif stat_axis_value_record.Format == 2:
                        axis_index = stat_axis_value_record.AxisIndex
                        axis_min_value = stat_axis_value_record.RangeMinValue
                        axis_max_value = stat_axis_value_record.RangeMaxValue
                        # axis_nominal_value = stat_axis_value_record.NominalValue
                        if axis_index >= stat_design_axis_count:
                            failed = True
                            yield FAIL, (
                                f"axis index {axis_index} (format 2) "
                                f"is greater than STAT axis count {stat_design_axis_count}"
                            )
                        stat_axis = stat_design_axis[axis_index].AxisTag
                        if (
                            instance_axis == stat_axis
                            and axis_min_value <= instance_value <= axis_max_value
                        ):
                            if found_instance_axis:
                                failed = True
                                yield FAIL, (
                                    f"axis value {instance_value} (format 2) "
                                    f"for axis {instance_axis} is not unique"
                                )
                            found_instance_axis = True
                if not found_instance_axis:
                    failed = True
                    yield FAIL, (
                        f"axis value {instance_value} "
                        f"for axis {instance_axis} not found in STAT table"
                    )
    if not failed:
        yield PASS, "fvar axis ranges found in STAT table"
