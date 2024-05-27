from fontbakery.prelude import FAIL, PASS, Message, check


@check(
    id="com.google.fonts/check/STAT_strings",
    conditions=["has_STAT_table"],
    rationale="""
        On the STAT table, the "Italic" keyword must not be used on AxisValues
        for variation axes other than 'ital'.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2863",
)
def com_google_fonts_check_STAT_strings(ttFont):
    """Check correctness of STAT table strings"""
    passed = True
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
            passed = False
            bad_values.add(f"nameID {name.nameID}: {name.toUnicode()}")

    if bad_values:
        yield FAIL, Message(
            "bad-italic",
            "The following AxisValue entries on the STAT table"
            f' should not contain "Italic":\n{sorted(bad_values)}',
        )

    if passed:
        yield PASS, "Looks good!"


@check(
    id="com.google.fonts/check/STAT_in_statics",
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
def com_google_fonts_check_STAT_in_statics(ttFont):
    """Checking STAT table entries in static fonts."""

    entries = {}

    def count_entries(tag_name):
        if tag_name in entries:
            entries[tag_name] += 1
        else:
            entries[tag_name] = 1

    passed = True
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
            passed = False
            yield FAIL, Message(
                "multiple-STAT-entries",
                "The STAT table has more than a single entry for the"
                f" '{tag_name}' axis ({entries[tag_name]}) on this"
                " static font which will causes problems on Windows.",
            )

    if passed:
        yield PASS, "Looks good!"
