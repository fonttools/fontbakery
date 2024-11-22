from fontbakery.constants import NameID
from fontbakery.prelude import check, Message, FAIL


# FIXME! This looks suspiciously similar to the now deprecated
#          googlefonts/metadata/nameid/family_name
#
#        Also similar to the current
#          googlefonts/metadata/nameid/family_and_full_names
#
#        See also: issue #4581
@check(
    id="googlefonts/metadata/nameid/font_name",
    rationale="""
        This check ensures consistency between the font name declared on the name table
        and the contents of the METADATA.pb file.
    """,
    conditions=["font_metadata", "style"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/4086",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_metadata_nameid_font_name(ttFont, style, font_metadata):
    """METADATA.pb font.name value should be same as
    the family name declared on the name table.
    """
    from fontbakery.utils import get_name_entry_strings

    font_familynames = get_name_entry_strings(
        ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME, langID=0x409
    )
    if len(font_familynames) == 0:
        # We'll only use nameid 1 (FONT_FAMILY_NAME) when the font
        # does not have nameid 16 (TYPOGRAPHIC_FAMILY_NAME).
        # https://github.com/fonttools/fontbakery/issues/4086
        font_familynames = get_name_entry_strings(
            ttFont, NameID.FONT_FAMILY_NAME, langID=0x409
        )

    nameid = NameID.FONT_FAMILY_NAME
    if len(font_familynames) == 0:
        yield FAIL, Message(
            "lacks-entry",
            f"This font lacks a {NameID(nameid).name} entry"
            f" (nameID = {nameid}) in the name table.",
        )
    else:
        for font_familyname in font_familynames:
            if font_familyname != font_metadata.name:
                yield FAIL, Message(
                    "mismatch",
                    f"Unmatched familyname in font:"
                    f' TTF has familyname = "{font_familyname}" while'
                    f' METADATA.pb has font.name = "{font_metadata.name}".',
                )
