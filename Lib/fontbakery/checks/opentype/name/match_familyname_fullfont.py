from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import NameID


@check(
    id="opentype/name/match_familyname_fullfont",
    rationale="""
        The FULL_FONT_NAME entry in the ‘name’ table should start with the same string
        as the Family Name (FONT_FAMILY_NAME, TYPOGRAPHIC_FAMILY_NAME or
        WWS_FAMILY_NAME).

        If the Family Name is not included as the first part of the Full Font Name, and
        the user embeds the font in a document using a Microsoft Office app, the app
        will fail to render the font when it opens the document again.

        NOTE: Up until version 1.5, the OpenType spec included the following exception
        in the definition of Full Font Name:

            "An exception to the [above] definition of Full font name is for Microsoft
            platform strings for CFF OpenType fonts: in this case, the Full font name
            string must be identical to the PostScript FontName in the CFF Name INDEX."

        https://docs.microsoft.com/en-us/typography/opentype/otspec150/name#name-ids
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_match_familyname_fullfont(ttFont):
    """Does full font name begin with the font family name?"""

    name_table = ttFont["name"]
    names_compared = False  # Used for knowing if at least one comparison was attempted

    # Collect all the unique platformIDs, encodingIDs, and languageIDs
    # used in the font's name table.
    platform_ids = set(rec.platformID for rec in name_table.names)
    encoding_ids = set(rec.platEncID for rec in name_table.names)
    language_ids = set(rec.langID for rec in name_table.names)

    # Now iterate over the platform/encoding/languageID sets and compare
    # the full name and family name strings.
    # The full name string is always taken from nameID 4, but
    # the family name string can come from nameIDs 1, 16, or 21.
    # We'll compare all of the ones contained in the font.
    full_name_id = NameID.FULL_FONT_NAME
    for plat_id in sorted(platform_ids):
        for enc_id in sorted(encoding_ids):
            for lang_id in sorted(language_ids):
                # Check if the full name record exists
                if name_table.getName(full_name_id, plat_id, enc_id, lang_id) is None:
                    # The full_name_id wasn't found. No point in going further
                    continue

                # Iterate over all possible family name records
                for family_name_id in (
                    NameID.FONT_FAMILY_NAME,
                    NameID.TYPOGRAPHIC_FAMILY_NAME,
                    NameID.WWS_FAMILY_NAME,
                ):
                    if (
                        name_table.getName(family_name_id, plat_id, enc_id, lang_id)
                        is None
                    ):
                        # The family_name_id wasn't found. Move on to the next
                        continue

                    names_compared = True  # Yay! At least one comparison will be made!!

                    decode_error_msg_prefix = (
                        f"On the 'name' table, the name record"
                        f" for platformID {plat_id},"
                        f" encodingID {enc_id},"
                        f" languageID {lang_id}({lang_id:04X}),"
                    )
                    try:
                        family_name = name_table.getName(
                            family_name_id, plat_id, enc_id, lang_id
                        ).toUnicode()
                    except UnicodeDecodeError:
                        yield FAIL, Message(
                            f"cannot-decode-nameid-{family_name_id}",
                            f"{decode_error_msg_prefix} and nameID {family_name_id}"
                            " failed to be decoded.",
                        )
                        continue

                    try:
                        full_name = name_table.getName(
                            full_name_id, plat_id, enc_id, lang_id
                        ).toUnicode()
                    except UnicodeDecodeError:
                        yield FAIL, Message(
                            f"cannot-decode-nameid-{full_name_id}",
                            f"{decode_error_msg_prefix} and nameID {full_name_id}"
                            " failed to be decoded.",
                        )
                        continue

                    if not full_name.startswith(family_name):
                        yield FAIL, Message(
                            "mismatch-font-names",
                            f"On the 'name' table, the full font name {full_name!r}"
                            f" does not begin with the font family name {family_name!r}"
                            f" in platformID {plat_id},"
                            f" encodingID {enc_id},"
                            f" languageID {lang_id}({lang_id:04X}),"
                            f" and nameID {family_name_id}.",
                        )

    if not names_compared:
        yield FAIL, Message(
            "missing-font-names",
            f"The font's 'name' table lacks a pair of records with"
            f" nameID {NameID.FULL_FONT_NAME} (Full name),"
            f" and at least one of"
            f" nameID {NameID.FONT_FAMILY_NAME} (Font Family name),"
            f" {NameID.TYPOGRAPHIC_FAMILY_NAME} (Typographic Family name),"
            f" or {NameID.WWS_FAMILY_NAME} (WWS Family name).",
        )
