from fontbakery.prelude import check, Message, FAIL, PASS


@check(
    id="opentype/family/underline_thickness",
    rationale="""
        Dave C Lemon (Adobe Type Team) recommends setting the underline thickness to be
        consistent across the family.

        If thicknesses are not family consistent, words set on the same line which have
        different styles look strange.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    misc_metadata={"affects": [("InDesign", "unspecified")]},
)
def check_family_underline_thickness(ttFonts):
    """Fonts have consistent underline thickness?"""
    underTs = {}
    underlineThickness = None
    failed = False
    for ttfont in ttFonts:
        fontname = ttfont.reader.file.name
        # stylename = style(fontname)
        ut = ttfont["post"].underlineThickness
        underTs[fontname] = ut
        if underlineThickness is None:
            underlineThickness = ut
        if ut != underlineThickness:
            failed = True

    if failed:
        msg = (
            "Thickness of the underline is not"
            " the same across this family. In order to fix this,"
            " please make sure that the underlineThickness value"
            " is the same in the 'post' table of all of this family"
            " font files.\n"
            "Detected underlineThickness values are:\n"
        )
        for style in underTs.keys():
            msg += f"\t{style}: {underTs[style]}\n"
        yield FAIL, Message("inconsistent-underline-thickness", msg)
    else:
        yield PASS, "Fonts have consistent underline thickness."
