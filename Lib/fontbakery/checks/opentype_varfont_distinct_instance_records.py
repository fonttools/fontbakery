from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="opentype/varfont/distinct_instance_records",
    rationale="""
        According to the 'fvar' documentation in OpenType spec v1.9
        https://docs.microsoft.com/en-us/typography/opentype/spec/fvar

        All of the instance records in a font should have distinct coordinates
        and distinct subfamilyNameID and postScriptName ID values. If two or more
        records share the same coordinates, the same nameID values or the same
        postScriptNameID values, then all but the first can be ignored.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3706",
)
def check_varfont_distinct_instance_records(ttFont, has_name_table):
    """Validates that all of the instance records in a given font have distinct data."""

    if not has_name_table:
        yield FAIL, Message("lacks-table", "Font lacks 'name' table.")
        return

    name_table = ttFont["name"]
    unique_inst_recs = set()

    for i, inst in enumerate(ttFont["fvar"].instances, 1):
        inst_coords = list(inst.coordinates.items())
        inst_subfam_nameid = inst.subfamilyNameID
        inst_postscript_nameid = inst.postscriptNameID
        inst_data = (tuple(inst_coords), inst_subfam_nameid, inst_postscript_nameid)

        if inst_data not in unique_inst_recs:
            unique_inst_recs.add(inst_data)

        else:  # non-unique instance was found
            inst_name = name_table.getDebugName(inst_subfam_nameid)

            if inst_name is None:
                inst_name = f"Instance #{i}"

            yield WARN, Message(
                f"repeated-instance-record:{inst_name}",
                f"{inst_name!r} is a repeated instance record.",
            )
