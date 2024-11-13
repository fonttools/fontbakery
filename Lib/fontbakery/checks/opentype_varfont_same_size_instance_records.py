from fontbakery.prelude import check, Message, FAIL, SKIP


@check(
    id="opentype/varfont/same_size_instance_records",
    rationale="""
        According to the 'fvar' documentation in OpenType spec v1.9
        https://docs.microsoft.com/en-us/typography/opentype/spec/fvar

        All of the instance records in a given font must be the same size, with
        all either including or omitting the postScriptNameID field. [...]
        If the value is 0xFFFF, then the value is ignored, and no PostScript name
        equivalent is provided for the instance.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3705",
)
def check_varfont_same_size_instance_records(ttFont):
    """Validates that all of the instance records in a given font have the same size."""

    if not ttFont["fvar"].instances:
        yield SKIP, Message("no-instance-records", "Font has no instance records.")
        return

    font_ps_nameids_not_provided = set(
        inst.postscriptNameID == 0xFFFF for inst in ttFont["fvar"].instances
    )

    # 'font_ps_nameids_not_provided' is a set whose values can only be
    # {True}, {False}, or {True, False}. So if the size of the set is not 1,
    # it means that some instance records have postscriptNameID values while
    # others do not.
    if len(font_ps_nameids_not_provided) != 1:
        yield FAIL, Message(
            "different-size-instance-records",
            "Instance records don't all have the same size.",
        )
