from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/varfont/valid_axis_nameid",
    rationale="""
        According to the 'fvar' documentation in OpenType spec v1.9
        https://docs.microsoft.com/en-us/typography/opentype/spec/fvar

        The axisNameID field provides a name ID that can be used to obtain strings
        from the 'name' table that can be used to refer to the axis in application
        user interfaces. The name ID must be greater than 255 and less than 32768.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3702",
)
def check_varfont_valid_axis_nameid(ttFont, has_name_table):
    """Validates that the value of axisNameID used by each VariationAxisRecord
    is greater than 255 and less than 32768."""

    if not has_name_table:
        yield FAIL, Message("lacks-table", "Font lacks 'name' table.")
        return

    name_table = ttFont["name"]
    font_axis_nameids = [axis.axisNameID for axis in ttFont["fvar"].axes]
    invalid_axis_nameids = [val for val in font_axis_nameids if not (255 < val < 32768)]

    for nameid in invalid_axis_nameids:
        inst_name = name_table.getDebugName(nameid) or "Unnamed"

        yield FAIL, Message(
            f"invalid-axis-nameid:{nameid}",
            f"{inst_name!r} instance has an axisNameID value that"
            " is not greater than 255 and less than 32768.",
        )


@check(
    id="opentype/varfont/valid_subfamily_nameid",
    rationale="""
        According to the 'fvar' documentation in OpenType spec v1.9
        https://docs.microsoft.com/en-us/typography/opentype/spec/fvar

        The subfamilyNameID field provides a name ID that can be used to obtain
        strings from the 'name' table that can be treated as equivalent to name
        ID 17 (typographic subfamily) strings for the given instance. Values of
        2 or 17 can be used; otherwise, values must be greater than 255 and less
        than 32768.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3703",
)
def check_varfont_valid_subfamily_nameid(ttFont, has_name_table):
    """Validates that the value of subfamilyNameID used by each InstanceRecord
    is 2, 17, or greater than 255 and less than 32768."""

    if not has_name_table:
        yield FAIL, Message("lacks-table", "Font lacks 'name' table.")
        return

    name_table = ttFont["name"]
    font_subfam_nameids = [inst.subfamilyNameID for inst in ttFont["fvar"].instances]
    invalid_subfam_nameids = [
        val
        for val in font_subfam_nameids
        if not (255 < val < 32768) and val not in {2, 17}
    ]

    for nameid in invalid_subfam_nameids:
        inst_name = name_table.getDebugName(nameid) or "Unnamed"

        yield FAIL, Message(
            f"invalid-subfamily-nameid:{nameid}",
            f"{inst_name!r} instance has a subfamilyNameID value that"
            " is neither 2, 17, or greater than 255 and less than 32768.",
        )


@check(
    id="opentype/varfont/valid_postscript_nameid",
    rationale="""
        According to the 'fvar' documentation in OpenType spec v1.9
        https://docs.microsoft.com/en-us/typography/opentype/spec/fvar

        The postScriptNameID field provides a name ID that can be used to obtain
        strings from the 'name' table that can be treated as equivalent to name
        ID 6 (PostScript name) strings for the given instance. Values of 6 and
        0xFFFF can be used; otherwise, values must be greater than 255 and less
        than 32768.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3704",
)
def check_varfont_valid_postscript_nameid(ttFont, has_name_table):
    """Validates that the value of postScriptNameID used by each InstanceRecord
    is 6, 0xFFFF, or greater than 255 and less than 32768."""

    if not has_name_table:
        yield FAIL, Message("lacks-table", "Font lacks 'name' table.")
        return

    name_table = ttFont["name"]
    font_postscript_nameids = [
        inst.postscriptNameID for inst in ttFont["fvar"].instances
    ]
    invalid_postscript_nameids = [
        val
        for val in font_postscript_nameids
        if not (255 < val < 32768) and val not in {6, 0xFFFF}
    ]

    for nameid in invalid_postscript_nameids:
        inst_name = name_table.getDebugName(nameid) or "Unnamed"

        yield FAIL, Message(
            f"invalid-postscript-nameid:{nameid}",
            f"{inst_name!r} instance has a postScriptNameID value that"
            f" is neither 6, 0xFFFF, or greater than 255 and less than 32768.",
        )
