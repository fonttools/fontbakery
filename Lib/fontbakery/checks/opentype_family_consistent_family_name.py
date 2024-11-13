from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import (
    NameID,
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)


@check(
    id="opentype/family/consistent_family_name",
    rationale="""
        Per the OpenType spec:

            * "...many existing applications that use this pair of names assume that a
              Font Family name is shared by at most four fonts that form a font
              style-linking group"

            * "For extended typographic families that includes fonts other than the
              four basic styles(regular, italic, bold, bold italic), it is strongly
              recommended that name IDs 16 and 17 be used in fonts to create an
              extended, typographic grouping."

            * "If name ID 16 is absent, then name ID 1 is considered to be the
              typographic family name."

        https://learn.microsoft.com/en-us/typography/opentype/spec/name

        Fonts within a font family all must have consistent names
        in the Typographic Family name (nameID 16)
        or Font Family name (nameID 1), depending on which it uses.

        Inconsistent font/typographic family names across fonts in a family
        can result in unexpected behaviors, such as broken style linking.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4112",
)
def check_consistent_font_family_name(ttFonts):
    """
    Verify that family names in the name table are consistent across all fonts in the
    family. Checks Typographic Family name (nameID 16) if present, otherwise uses Font
    Family name (nameID 1)
    """
    from fontbakery.utils import get_name_entry_strings
    from collections import defaultdict
    import os

    name_dict = defaultdict(list)
    for ttFont in ttFonts:
        filename = os.path.basename(ttFont.reader.file.name)
        # try nameID 16
        nameID = NameID.TYPOGRAPHIC_FAMILY_NAME
        names_list = get_name_entry_strings(
            ttFont,
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            PlatformID.WINDOWS,
            WindowsEncodingID.UNICODE_BMP,
            WindowsLanguageID.ENGLISH_USA,
        )
        if len(names_list) == 0:
            # use nameID 1 instead
            nameID = NameID.FONT_FAMILY_NAME
            names_list = get_name_entry_strings(
                ttFont,
                NameID.FONT_FAMILY_NAME,
                PlatformID.WINDOWS,
                WindowsEncodingID.UNICODE_BMP,
                WindowsLanguageID.ENGLISH_USA,
            )
        name_dict[frozenset(names_list)].append((filename, nameID))

    if len(name_dict) > 1:
        detail_str_arr = []
        indent = "\n  - "
        for name_set, font_tuple_list in name_dict.items():
            detail_str = f"\n\n* '{next(iter(name_set), '')}' was found in:"

            fonts_str_arr = []
            for ft in font_tuple_list:
                fonts_str_arr.append(f"{ft[0]} (nameID {ft[1]})")

            detail_str_arr.append(f"{detail_str}{indent}{indent.join(fonts_str_arr)}")

        msg = (
            f"{len(name_dict)} different Font Family names were found:"
            f"{''.join(detail_str_arr)}"
        )
        yield FAIL, Message("inconsistent-family-name", msg)
