from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/varfont/valid_default_instance_nameids",
    rationale="""
        According to the 'fvar' documentation in OpenType spec v1.9.1
        https://docs.microsoft.com/en-us/typography/opentype/spec/fvar

        The default instance of a font is that instance for which the coordinate
        value of each axis is the defaultValue specified in the corresponding
        variation axis record. An instance record is not required for the default
        instance, though an instance record can be provided. When enumerating named
        instances, the default instance should be enumerated even if there is no
        corresponding instance record. If an instance record is included for the
        default instance (that is, an instance record has coordinates set to default
        values), then the nameID value should be set to either 2 or 17 or to a
        name ID with the same value as name ID 2 or 17. Also, if a postScriptNameID is
        included in instance records, and the postScriptNameID value should be set
        to 6 or to a name ID with the same value as name ID 6.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3708",
)
def check_varfont_valid_default_instance_nameids(ttFont, has_name_table):
    """Validates subfamilyNameID and postScriptNameID for the default instance record"""

    if not has_name_table:
        yield FAIL, Message("lacks-table", "Font lacks 'name' table.")
        return

    name_table = ttFont["name"]
    fvar_table = ttFont["fvar"]

    font_includes_ps_nameid = any(
        inst.postscriptNameID != 0xFFFF for inst in fvar_table.instances
    )
    axes_dflt_coords = {axis.axisTag: axis.defaultValue for axis in fvar_table.axes}
    name2 = name_table.getDebugName(2)
    name6 = name_table.getDebugName(6)
    name17 = name_table.getDebugName(17)
    font_subfam_name = name17 or name2

    for i, inst in enumerate(fvar_table.instances, 1):
        inst_coords = dict(inst.coordinates.items())

        # The instance record has the same coordinates as the default instance
        if inst_coords == axes_dflt_coords:
            subfam_nameid = inst.subfamilyNameID
            subfam_name = name_table.getDebugName(subfam_nameid) or f"Instance #{i}"
            postscript_nameid = inst.postscriptNameID
            postscript_name = name_table.getDebugName(postscript_nameid) or "None"

            # Special handle the 0xFFFF case, to avoid displaying the value as 65535
            if postscript_nameid == 0xFFFF:
                postscript_nameid = "0xFFFF"

            if name17 and subfam_name != font_subfam_name:
                yield FAIL, Message(
                    "invalid-default-instance-subfamily-name",
                    f"{subfam_name!r} instance has the same coordinates as the default"
                    f" instance; its subfamily name should be {font_subfam_name!r}.\n\n"
                    f"Note: It is alternatively possible that Name ID 17 is incorrect,"
                    f" and should be set to the default instance subfamily name, {subfam_name!r},"
                    f" rather than '{name17!r}'. If the default instance is {subfam_name!r},"
                    f" NameID 17 is probably the problem.",
                )

            if not name17 and subfam_name != font_subfam_name:
                yield FAIL, Message(
                    "invalid-default-instance-subfamily-name",
                    f"{subfam_name!r} instance has the same coordinates as the default"
                    f" instance; its subfamily name should be {font_subfam_name!r}.\n\n"
                    f"Note: If the default instance really is meant to be called {subfam_name!r},"
                    f" the problem may be that the font lacks NameID 17, which should"
                    f" probably be present and set to {subfam_name!r}.",
                )

            # Validate the postScriptNameID string only if
            # at least one instance record includes it
            if font_includes_ps_nameid and postscript_name != name6:
                yield FAIL, Message(
                    "invalid-default-instance-postscript-name",
                    f"{subfam_name!r} instance has the same coordinates as the default"
                    f" instance; its postscript name should be {name6!r}, instead of"
                    f" {postscript_name!r}.",
                )
