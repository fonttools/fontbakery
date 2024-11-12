from fontbakery.constants import NameID
from fontbakery.prelude import check, Message, FAIL, SKIP


@check(
    id="name/italic_names",
    conditions=["style"],
    rationale="""
        This check ensures that several entries in the name table
        conform to the font's Upright or Italic style,
        namely IDs 1 & 2 as well as 16 & 17 if they're present.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3666",
)
def check_name_italic_names(ttFont, style):
    """Check name table IDs 1, 2, 16, 17 to conform to Italic style."""

    def get_name(nameID):
        for entry in ttFont["name"].names:
            if entry.nameID == nameID:
                return entry.toUnicode()

    if "Italic" not in style:
        yield SKIP, ("Font is not Italic.")
    else:
        # Name ID 1 (Family Name)
        if "Italic" in get_name(NameID.FONT_FAMILY_NAME):
            yield FAIL, Message(
                "bad-familyname", "Name ID 1 (Family Name) must not contain 'Italic'."
            )

        # Name ID 2 (Subfamily Name)
        subfamily_name = get_name(NameID.FONT_SUBFAMILY_NAME)
        if subfamily_name not in ("Italic", "Bold Italic"):
            yield FAIL, Message(
                "bad-subfamilyname",
                "Name ID 2 (Subfamily Name) does not conform to specs."
                " Only R/I/B/BI are allowed.\n"
                f"Got: '{subfamily_name}'.",
            )

        # Name ID 16 (Typographic Family Name)
        if get_name(NameID.TYPOGRAPHIC_FAMILY_NAME):
            if "Italic" in get_name(NameID.TYPOGRAPHIC_FAMILY_NAME):
                yield FAIL, Message(
                    "bad-typographicfamilyname",
                    "Name ID 16 (Typographic Family Name) must not contain 'Italic'.",
                )

        # Name ID 17 (Typographic Subfamily Name)
        if get_name(NameID.TYPOGRAPHIC_SUBFAMILY_NAME):
            if not get_name(NameID.TYPOGRAPHIC_SUBFAMILY_NAME).endswith("Italic"):
                yield FAIL, Message(
                    "bad-typographicsubfamilyname",
                    "Name ID 17 (Typographic Subfamily Name) must contain 'Italic'.",
                )
