from fontbakery.prelude import check, Message, PASS, FAIL, INFO
from fontbakery.constants import NameID


@check(
    id="typenetwork/name/mandatory_entries",
    conditions=["style"],
    rationale="""
        For proper functioning, fonts must have some specific records.
        Other name records are optional but desireable to be present.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_name_mandatory_entries(ttFont, style):
    """Font has all mandatory 'name' table entries?"""
    from fontbakery.utils import get_name_entry_strings
    from fontbakery.constants import RIBBI_STYLE_NAMES

    optional_nameIDs = [
        NameID.COPYRIGHT_NOTICE,
        NameID.UNIQUE_FONT_IDENTIFIER,
        NameID.VERSION_STRING,
        NameID.TRADEMARK,
        NameID.MANUFACTURER_NAME,
        NameID.DESIGNER,
        NameID.DESCRIPTION,
        NameID.VENDOR_URL,
        NameID.DESIGNER_URL,
        NameID.LICENSE_DESCRIPTION,
        NameID.LICENSE_INFO_URL,
    ]

    required_nameIDs = [
        NameID.FONT_FAMILY_NAME,
        NameID.FONT_SUBFAMILY_NAME,
        NameID.FULL_FONT_NAME,
        NameID.POSTSCRIPT_NAME,
    ]

    unnecessary_nameIDs = []

    if style not in RIBBI_STYLE_NAMES:
        required_nameIDs += [
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
        ]
    else:
        unnecessary_nameIDs += [
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
        ]

    passed = True
    # The font must have at least these name IDs:
    for nameId in required_nameIDs:
        for entry in get_name_entry_strings(ttFont, nameId):
            if len(entry) == 0:
                passed = False
                yield FAIL, Message(
                    "missing-required-entry",
                    f"Font lacks entry with nameId={nameId}"
                    f" ({NameID(nameId).name})",
                )

    # The font should have these name IDs:
    for nameId in optional_nameIDs:
        if len(get_name_entry_strings(ttFont, nameId)) == 0:
            passed = False
            yield INFO, Message(
                "missing-optional-entry",
                f"Font lacks entry with nameId={nameId} ({NameID(nameId).name})",
            )

    # The font should NOT have these name IDs:
    for nameId in unnecessary_nameIDs:
        if len(get_name_entry_strings(ttFont, nameId)) != 0:
            passed = False
            yield INFO, Message(
                "unnecessary-entry",
                f"Font have unnecessary name entry with nameId={nameId}"
                f" ({NameID(nameId).name})",
            )

    if passed:
        yield PASS, "Font contains values for all mandatory name table entries."
