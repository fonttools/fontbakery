from fontbakery.prelude import PASS, FAIL, Message, check


@check(
    id="sfnt_version",
    severity=10,
    rationale="""
        OpenType fonts that contain TrueType outlines should use the value of 0x00010000
        for the sfntVersion. OpenType fonts containing CFF data (version 1 or 2) should
        use 0x4F54544F ('OTTO', when re-interpreted as a Tag) for sfntVersion.

        Fonts with the wrong sfntVersion value are rejected by FreeType.

        https://docs.microsoft.com/en-us/typography/opentype/spec/otff#table-directory
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3388",
)
def check_sfnt_version(ttFont, is_ttf, is_cff, is_cff2):
    """Font has the proper sfntVersion value?"""
    sfnt_version = ttFont.sfntVersion

    if is_ttf and sfnt_version != "\x00\x01\x00\x00":
        yield FAIL, Message(
            "wrong-sfnt-version-ttf",
            "Font with TrueType outlines has incorrect sfntVersion value:"
            f" '{sfnt_version}'",
        )

    elif (is_cff or is_cff2) and sfnt_version != "OTTO":
        yield FAIL, Message(
            "wrong-sfnt-version-cff",
            f"Font with CFF data has incorrect sfntVersion value: '{sfnt_version}'",
        )

    else:
        yield PASS, "Font has the correct sfntVersion value."
