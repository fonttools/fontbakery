from fontbakery.prelude import FAIL, Message, check


@check(
    id="STAT_strings",
    conditions=["has_STAT_table"],
    rationale="""
        On the STAT table, the "Italic" keyword must not be used on AxisValues
        for variation axes other than 'ital'.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2863",
)
def check_STAT_strings(ttFont):
    """Check correctness of STAT table strings"""
    ital_axis_index = None
    for index, axis in enumerate(ttFont["STAT"].table.DesignAxisRecord.Axis):
        if axis.AxisTag == "ital":
            ital_axis_index = index
            break

    nameIDs = set()
    if ttFont["STAT"].table.AxisValueArray:
        for value in ttFont["STAT"].table.AxisValueArray.AxisValue:
            if hasattr(value, "AxisIndex"):
                if value.AxisIndex != ital_axis_index:
                    nameIDs.add(value.ValueNameID)

            if hasattr(value, "AxisValueRecord"):
                for record in value.AxisValueRecord:
                    if record.AxisIndex != ital_axis_index:
                        nameIDs.add(value.ValueNameID)

    bad_values = set()
    for name in ttFont["name"].names:
        if name.nameID in nameIDs and "italic" in name.toUnicode().lower():
            bad_values.add(f"nameID {name.nameID}: {name.toUnicode()}")

    if bad_values:
        yield FAIL, Message(
            "bad-italic",
            "The following AxisValue entries on the STAT table"
            f' should not contain "Italic":\n{sorted(bad_values)}',
        )


@check(
    id="STAT_in_statics",
    conditions=["not is_variable_font", "has_STAT_table"],
    rationale="""
        Adobe feature syntax allows for the definition of a STAT table. Fonts built
        with a hand-coded STAT table in feature syntax may be built either as static
        or variable, but will end up with the same STAT table.

        This is a problem, because a STAT table which works on variable fonts
        will not be appropriate for static instances. The examples in the OpenType spec
        of non-variable fonts with a STAT table show that the table entries must be
        restricted to those entries which refer to the static font's position in
        the designspace. i.e. a Regular weight static should only have the following
        entry for the weight axis:

        <AxisIndex value="0"/>
        <Flags value="2"/>  <!-- ElidableAxisValueName -->
        <ValueNameID value="265"/>  <!-- Regular -->
        <Value value="400.0"/>

        However, if the STAT table intended for a variable font is compiled into a
        static, it will have many entries for this axis. In this case, Windows will
        read the first entry only, causing all instances to report themselves
        as "Thin Condensed".
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4149",
)
def check_STAT_in_statics(ttFont):
    """Checking STAT table entries in static fonts."""

    entries = {}

    def count_entries(tag_name):
        if tag_name in entries:
            entries[tag_name] += 1
        else:
            entries[tag_name] = 1

    stat = ttFont["STAT"].table
    designAxes = stat.DesignAxisRecord.Axis
    for axisValueTable in stat.AxisValueArray.AxisValue:
        axisValueFormat = axisValueTable.Format
        if axisValueFormat in (1, 2, 3):
            axisTag = designAxes[axisValueTable.AxisIndex].AxisTag
            count_entries(axisTag)
        elif axisValueFormat == 4:
            for rec in axisValueTable.AxisValueRecord:
                axisTag = designAxes[rec.AxisIndex].AxisTag
                count_entries(axisTag)

    for tag_name in entries:
        if entries[tag_name] > 1:
            yield FAIL, Message(
                "multiple-STAT-entries",
                "The STAT table has more than a single entry for the"
                f" '{tag_name}' axis ({entries[tag_name]}) on this"
                " static font which will causes problems on Windows.",
            )


def is_covered_in_stat(ttFont, axis_tag, value):
    if "STAT" not in ttFont:
        return False
    stat_table = ttFont["STAT"].table
    if stat_table.AxisValueCount == 0:
        return False
    for ax_value in stat_table.AxisValueArray.AxisValue:
        ax_value_format = ax_value.Format
        stat_value = []
        if ax_value_format in (1, 2, 3):
            axis_tag_stat = stat_table.DesignAxisRecord.Axis[ax_value.AxisIndex].AxisTag
            if axis_tag != axis_tag_stat:
                continue

            if ax_value_format in (1, 3):
                stat_value.append(ax_value.Value)

            if ax_value_format == 3:
                stat_value.append(ax_value.LinkedValue)

            if ax_value_format == 2:
                stat_value.append(ax_value.NominalValue)

        if ax_value_format == 4:
            # TODO: Need to implement
            #  locations check as well
            pass

        if value in stat_value:
            return True

    return False


@check(
    id="inconsistencies_between_fvar_stat",
    rationale="""
        Check for inconsistencies in names and values between the fvar instances
        and STAT table. Inconsistencies may cause issues in apps like Adobe InDesign.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3636",
)
def check_inconsistencies_between_fvar_stat(ttFont):
    """Checking if STAT entries matches fvar and vice versa."""

    if "STAT" not in ttFont:
        return FAIL, Message(
            "missing-stat-table", "Missing STAT table in variable font."
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
            if not is_covered_in_stat(ttFont, axis_tag, value):
                yield FAIL, Message(
                    "missing-fvar-instance-axis-value",
                    f"{instance_name}: '{axis_tag}' axis value '{value}'"
                    f" missing in STAT table.",
                )

        # TODO: Compare fvar instance name with constructed STAT table name.
