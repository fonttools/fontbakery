from fontbakery.constants import RIBBI_STYLE_NAMES
from fontbakery.prelude import check, Message, FAIL, SKIP


@check(
    id="googlefonts/metadata/valid_full_name_values",
    conditions=["style", "font_metadata"],
    rationale="""
        This check ensures that the font.full_name field in the METADATA.pb
        file contains the family name of the font.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_valid_full_name_values(font):
    """METADATA.pb font.full_name field contains font name in right format?"""
    if font.style in RIBBI_STYLE_NAMES:
        familynames = font.font_familynames
        if familynames == []:
            yield SKIP, "No FONT_FAMILYNAME"
    else:
        familynames = font.typographic_familynames
        if familynames == []:
            yield SKIP, "No TYPOGRAPHIC_FAMILYNAME"

    if not any((name in font.font_metadata.full_name) for name in familynames):
        familynames = ", ".join(familynames)
        yield FAIL, Message(
            "mismatch",
            f"METADATA.pb font.full_name field"
            f' ("{font.font_metadata.full_name}")'
            f" does not match correct font name format"
            f' ("{familynames}").',
        )
