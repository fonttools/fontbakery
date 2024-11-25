from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import (
    RIBBI_STYLE_NAMES,
    NameID,
)


@check(
    id="googlefonts/name/mandatory_entries",
    conditions=["style"],
    rationale="""
        We require all fonts to have values for their font family name,
        font subfamily name, full font name, and postscript name. For RIBBI
        fonts, we also require values for the typographic family name and
        typographic subfamily name.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_mandatory_entries(ttFont, style):
    """Font has all mandatory 'name' table entries?"""
    from fontbakery.utils import get_name_entry_strings

    required_nameIDs = [
        NameID.FONT_FAMILY_NAME,
        NameID.FONT_SUBFAMILY_NAME,
        NameID.FULL_FONT_NAME,
        NameID.POSTSCRIPT_NAME,
    ]
    if style not in RIBBI_STYLE_NAMES:
        required_nameIDs += [
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
        ]

    # The font must have at least these name IDs:
    for nameId in required_nameIDs:
        if len(get_name_entry_strings(ttFont, nameId)) == 0:
            yield FAIL, Message(
                "missing-entry",
                f"Font lacks entry with nameId={nameId} ({NameID(nameId).name})",
            )
