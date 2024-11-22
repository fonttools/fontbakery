from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import NameID
from fontbakery.utils import get_name_entry_strings


@check(
    id="googlefonts/metadata/nameid/family_and_full_names",
    conditions=["font_metadata"],
    rationale="""
        This check ensures that the family name declared in the METADATA.pb file
        matches the family name declared in the name table of the font file,
        and that the font full name declared in the METADATA.pb file
        matches the font full name declared in the name table of the font file.
        If the font was uploaded by the packager, this should always be the
        case. But if there were manual changes to the METADATA.pb file, a mismatch
        could occur.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_nameid_family_and_full_names(ttFont, font_metadata):
    """METADATA.pb font.name and font.full_name fields match
    the values declared on the name table?
    """

    font_familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
    if font_familynames:
        font_familyname = font_familynames[0]
    else:
        font_familyname = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)[0]

    font_fullname = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)[0]
    # FIXME: common condition/name-id check to other checks.

    if font_fullname != font_metadata.full_name:
        yield FAIL, Message(
            "fullname-mismatch",
            (
                f'METADATA.pb: Fullname "{font_metadata.full_name}"'
                f' does not match name table entry "{font_fullname}"!'
            ),
        )

    elif font_familyname != font_metadata.name:
        yield FAIL, Message(
            "familyname-mismatch",
            (
                f'METADATA.pb Family name "{font_metadata.name}"'
                f' does not match name table entry "{font_familyname}"!'
            ),
        )
