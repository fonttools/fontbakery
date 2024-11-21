from fontbakery.prelude import FAIL, Message, check


def is_covered_in_STAT(ttFont, axis_tag, value):
    if "STAT" not in ttFont:
        return False
    STAT_table = ttFont["STAT"].table
    if STAT_table.AxisValueCount == 0:
        return False
    for ax_value in STAT_table.AxisValueArray.AxisValue:
        ax_value_format = ax_value.Format
        STAT_value = []
        if ax_value_format in (1, 2, 3):
            axis_tag_STAT = STAT_table.DesignAxisRecord.Axis[ax_value.AxisIndex].AxisTag
            if axis_tag != axis_tag_STAT:
                continue

            if ax_value_format in (1, 3):
                STAT_value.append(ax_value.Value)

            if ax_value_format == 3:
                STAT_value.append(ax_value.LinkedValue)

            if ax_value_format == 2:
                STAT_value.append(ax_value.NominalValue)

        if ax_value_format == 4:
            # TODO: Need to implement
            #  locations check as well
            pass

        if value in STAT_value:
            return True

    return False


@check(
    id="inconsistencies_between_fvar_STAT",
    rationale="""
        Check for inconsistencies in names and values between the fvar instances
        and STAT table. Inconsistencies may cause issues in apps like Adobe InDesign.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3636",
)
def check_inconsistencies_between_fvar_STAT(ttFont):
    """Checking if STAT entries matches fvar and vice versa."""

    if "STAT" not in ttFont:
        return FAIL, Message(
            "missing-STAT-table", "Missing STAT table in variable font."
        )
    fvar = ttFont["fvar"]
    name = ttFont["name"]

    for ins in fvar.instances:
        instance_name = name.getDebugName(ins.subfamilyNameID)
        if instance_name is None:
            yield FAIL, Message(
                "missing-name-id",
                f"The name ID {ins.subfamilyNameID} used in an"
                f" fvar instance is missing in the name table.",
            )
            continue

        for axis_tag, value in ins.coordinates.items():
            if not is_covered_in_STAT(ttFont, axis_tag, value):
                yield FAIL, Message(
                    "missing-fvar-instance-axis-value",
                    f"{instance_name}: '{axis_tag}' axis value '{value}'"
                    f" missing in STAT table.",
                )

        # TODO: Compare fvar instance name with constructed STAT table name.
