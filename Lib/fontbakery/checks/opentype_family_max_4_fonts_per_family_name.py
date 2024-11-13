from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import (
    NameID,
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)


@check(
    id="opentype/family/max_4_fonts_per_family_name",
    rationale="""
        Per the OpenType spec:

        'The Font Family name [...] should be shared among at most four fonts that
        differ only in weight or style [...]'
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2372",
)
def check_family_max_4_fonts_per_family_name(ttFonts):
    """Verify that each group of fonts with the same nameID 1 has maximum of 4 fonts."""
    from collections import Counter
    from fontbakery.utils import get_name_entry_strings

    family_names = []
    for ttFont in ttFonts:
        names_list = get_name_entry_strings(
            ttFont,
            NameID.FONT_FAMILY_NAME,
            PlatformID.WINDOWS,
            WindowsEncodingID.UNICODE_BMP,
            WindowsLanguageID.ENGLISH_USA,
        )
        # names_list may contain multiple entries.
        # We use set() below to remove the duplicates and only store
        # the unique family name(s) used for a given font
        names_set = set(names_list)
        family_names.extend(names_set)

    counter = Counter(family_names)
    for family_name, count in counter.items():
        if count > 4:
            yield FAIL, Message(
                "too-many",
                f"Family '{family_name}' has {count} fonts" f" (should be 4 or fewer).",
            )
