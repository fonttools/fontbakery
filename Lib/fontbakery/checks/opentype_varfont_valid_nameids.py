from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/varfont/valid_nameids",
    rationale="""
        According to the 'fvar' documentation in OpenType spec v1.9
        https://docs.microsoft.com/en-us/typography/opentype/spec/fvar

        The axisNameID field provides a name ID that can be used to obtain strings
        from the 'name' table that can be used to refer to the axis in application
        user interfaces. The name ID must be greater than 255 and less than 32768.

        The postScriptNameID field provides a name ID that can be used to obtain
        strings from the 'name' table that can be treated as equivalent to name
        ID 6 (PostScript name) strings for the given instance. Values of 6 and
        "undefined" can be used; otherwise, values must be greater than 255 and
        less than 32768.

        The subfamilyNameID field provides a name ID that can be used to obtain
        strings from the 'name' table that can be treated as equivalent to name
        ID 17 (typographic subfamily) strings for the given instance. Values of
        2 or 17 can be used; otherwise, values must be greater than 255 and less
        than 32768.
    """,
    conditions=["is_variable_font"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3702",
        "https://github.com/fonttools/fontbakery/issues/3703",
    ],
)
def check_valid_nameids(ttFont, has_name_table):
    """Validates that all of the name IDs in an instance record
    are within the correct range"""

    font_axis_nameids = [axis.axisNameID for axis in ttFont["fvar"].axes]
    invalid_axis_nameids = [val for val in font_axis_nameids if not (255 < val < 32768)]

    for nameid in invalid_axis_nameids:
        name = ("name" in ttFont and ttFont["name"].getDebugName(nameid)) or "Unnamed"

        yield FAIL, Message(
            f"invalid-axis-nameid:{nameid}",
            f"Axis name ID {nameid} ({name}) is out of range."
            f" It must be greater than 255 and less than 32768.",
        )

    font_postscript_nameids = [
        inst.postscriptNameID for inst in ttFont["fvar"].instances
    ]
    invalid_postscript_nameids = [
        val
        for val in font_postscript_nameids
        if val not in [6, 0xFFFF] and not (255 < val < 32768)
    ]

    for nameid in invalid_postscript_nameids:
        name = ("name" in ttFont and ttFont["name"].getDebugName(nameid)) or "Unnamed"

        yield FAIL, Message(
            f"invalid-postscript-nameid:{nameid}",
            f"PostScript name ID {nameid} ({name}) is out of range."
            f" It must be greater than 255 and less than 32768, or 6 or 0xFFFF.",
        )

    font_subfam_nameids = [inst.subfamilyNameID for inst in ttFont["fvar"].instances]
    invalid_subfam_nameids = [
        val
        for val in font_subfam_nameids
        if not (255 < val < 32768) and val not in {2, 17}
    ]

    for nameid in invalid_subfam_nameids:
        name = ("name" in ttFont and ttFont["name"].getDebugName(nameid)) or "Unnamed"

        yield FAIL, Message(
            f"invalid-subfamily-nameid:{nameid}",
            f"Instance subfamily name ID {nameid} ({name}) is out of range."
            f" It must be greater than 255 and less than 32768.",
        )
