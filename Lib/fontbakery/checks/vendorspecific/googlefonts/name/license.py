from fontbakery.constants import NameID, PlatformID
from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="googlefonts/name/license",
    conditions=["license_filename"],
    rationale="""
        A known licensing description must be provided in the NameID 14
        (LICENSE DESCRIPTION) entries of the name table.

        The source of truth for this check (to determine which license is in use) is
        a file placed side-by-side to your font project including the licensing terms.

        Depending on the chosen license, one of the following string snippets is
        expected to be found on the NameID 13 (LICENSE DESCRIPTION) entries of the
        name table:

        - "This Font Software is licensed under the SIL Open Font License, Version 1.1.
          This license is available with a FAQ at: openfontlicense.org"

        - "Licensed under the Apache License, Version 2.0"

        - "Licensed under the Ubuntu Font Licence 1.0."


        Currently accepted licenses are Apache or Open Font License. For a small set
        of legacy families the Ubuntu Font License may be acceptable as well.

        When in doubt, please choose OFL for new font projects.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_license(ttFont, license_filename):
    """Check copyright namerecords match license file."""
    from fontbakery.constants import PLACEHOLDER_LICENSING_TEXT

    http_warn = False
    placeholder = PLACEHOLDER_LICENSING_TEXT[license_filename]
    entry_found = False
    for i, nameRecord in enumerate(ttFont["name"].names):
        if nameRecord.nameID == NameID.LICENSE_DESCRIPTION:
            entry_found = True
            value = nameRecord.toUnicode()
            if "http://" in value:
                yield WARN, Message(
                    "http-in-description",
                    f"Please consider using HTTPS URLs at"
                    f" name table entry [plat={nameRecord.platformID},"
                    f" enc={nameRecord.platEncID},"
                    f" name={nameRecord.nameID}]",
                )
                value = "https://".join(value.split("http://"))
                http_warn = True

            if "scripts.sil.org/OFL" in value:
                yield WARN, Message(
                    "old-url",
                    "Please consider updating the url from "
                    "'https://scripts.sil.org/OFL' to "
                    "'https://openfontlicense.org'.",
                )
                return
            if value != placeholder:
                yield FAIL, Message(
                    "wrong",
                    f"License file {license_filename} exists but"
                    f" NameID {NameID.LICENSE_DESCRIPTION}"
                    f" (LICENSE DESCRIPTION) value on platform"
                    f" {nameRecord.platformID}"
                    f" ({PlatformID(nameRecord.platformID).name})"
                    f" is not specified for that."
                    f' Value was: "{value}"'
                    f' Must be changed to "{placeholder}"',
                )
    if http_warn:
        yield WARN, Message(
            "http",
            "For now we're still accepting http URLs,"
            " but you should consider using https instead.\n",
        )

    if not entry_found:
        yield FAIL, Message(
            "missing",
            f"Font lacks NameID {NameID.LICENSE_DESCRIPTION}"
            f" (LICENSE DESCRIPTION). A proper licensing"
            f" entry must be set.",
        )
