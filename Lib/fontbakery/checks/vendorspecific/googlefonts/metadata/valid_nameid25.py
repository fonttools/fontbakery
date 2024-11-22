from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/valid_nameid25",
    conditions=["style"],
    rationale="""
        Due to a bug in (at least) Adobe Indesign, name ID 25
        needs to be different for Italic VFs than their Upright counterparts.
        Google Fonts chooses to append "Italic" here.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3024",
        "https://github.com/googlefonts/gftools/issues/297",
        "https://typo.social/@arrowtype/110430680157544757",
    ],
)
def check_metadata_valid_nameid25(font, style):
    'Check name ID 25 to end with "Italic" for Italic VFs.'
    ttFont = font.ttFont

    def get_name(font, ID):
        for entry in font["name"].names:
            if entry.nameID == 25:
                return entry.toUnicode()
        return ""

    if "Italic" in style and font.is_variable_font:
        if not get_name(ttFont, 25).endswith("Italic"):
            yield FAIL, Message(
                "nameid25-missing-italic",
                'Name ID 25 must end with "Italic" for Italic fonts.',
            )
        if " " in get_name(ttFont, 25):
            yield FAIL, Message(
                "nameid25-has-spaces", "Name ID 25 must not contain spaces."
            )
