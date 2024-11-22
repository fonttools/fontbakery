from fontbakery.prelude import check, Message, FAIL


@check(
    id="adobefonts/STAT_strings",
    conditions=["has_STAT_table"],
    rationale="""
        In the STAT table, the "Italic" keyword must not be used on AxisValues
        for variation axes other than 'ital' or 'slnt'. This is a more lenient
        implementation of googlefonts/STAT_strings which allows "Italic"
        only for the 'ital' axis.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2863",
)
def check_STAT_strings(ttFont):
    """Check correctness of STAT table strings"""
    stat_table = ttFont["STAT"].table
    ital_slnt_axis_indices = []
    for index, axis in enumerate(stat_table.DesignAxisRecord.Axis):
        if axis.AxisTag in ("ital", "slnt"):
            ital_slnt_axis_indices.append(index)

    nameIDs = set()
    if ttFont["STAT"].table.AxisValueArray:
        for value in stat_table.AxisValueArray.AxisValue:
            if hasattr(value, "AxisIndex"):
                if value.AxisIndex not in ital_slnt_axis_indices:
                    nameIDs.add(value.ValueNameID)

            if hasattr(value, "AxisValueRecord"):
                for record in value.AxisValueRecord:
                    if record.AxisIndex not in ital_slnt_axis_indices:
                        nameIDs.add(value.ValueNameID)

    bad_values = set()
    for name in ttFont["name"].names:
        if name.nameID in nameIDs and "italic" in name.toUnicode().lower():
            bad_values.add(f"nameID {name.nameID}: {name.toUnicode()}")

    if bad_values:
        yield FAIL, Message(
            "bad-italic",
            f"The following AxisValue entries in the STAT table"
            f' should not contain "Italic":\n'
            f" {sorted(bad_values)}",
        )
