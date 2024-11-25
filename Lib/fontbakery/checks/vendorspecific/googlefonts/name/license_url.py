from fontbakery.constants import NameID
from fontbakery.prelude import check, Message, PASS, FAIL, WARN, SKIP


@check(
    id="googlefonts/name/license_url",
    rationale="""
        A known license URL must be provided in the NameID 14 (LICENSE INFO URL)
        entry of the name table.

        The source of truth for this check is the licensing text found on the NameID 13
        entry (LICENSE DESCRIPTION).

        The string snippets used for detecting licensing terms are:

        - "This Font Software is licensed under the SIL Open Font License, Version 1.1.
          This license is available with a FAQ at: openfontlicense.org"

        - "Licensed under the Apache License, Version 2.0"

        - "Licensed under the Ubuntu Font Licence 1.0."


        Currently accepted licenses are Apache or Open Font License. For a small set of
        legacy families the Ubuntu Font License may be acceptable as well.

        When in doubt, please choose OFL for new font projects.
    """,
    conditions=["familyname"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/4358",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_name_license_url(ttFont, familyname):
    """License URL matches License text on name table?"""
    from fontbakery.constants import PLACEHOLDER_LICENSING_TEXT

    LEGACY_UFL_FAMILIES = ["Ubuntu", "UbuntuCondensed", "UbuntuMono"]
    LICENSE_URL = {
        "OFL.txt": "https://openfontlicense.org",
        "LICENSE.txt": "https://www.apache.org/licenses/LICENSE-2.0",
        "UFL.txt": "https://www.ubuntu.com/legal/terms-and-policies/font-licence",
    }
    LICENSE_NAME = {
        "OFL.txt": "Open Font",
        "LICENSE.txt": "Apache",
        "UFL.txt": "Ubuntu Font License",
    }
    detected_license = False
    http_warn = False
    for license_filename in ["OFL.txt", "LICENSE.txt", "UFL.txt"]:
        placeholder = PLACEHOLDER_LICENSING_TEXT[license_filename]
        for nameRecord in ttFont["name"].names:
            string = nameRecord.string.decode(nameRecord.getEncoding())
            if nameRecord.nameID == NameID.LICENSE_DESCRIPTION:
                if "http://" in string:
                    yield WARN, Message(
                        "http-in-description",
                        f"Please consider using HTTPS URLs at"
                        f" name table entry [plat={nameRecord.platformID},"
                        f" enc={nameRecord.platEncID},"
                        f" name={nameRecord.nameID}]",
                    )
                    string = "https://".join(string.split("http://"))
                    http_warn = True

                if string == placeholder:
                    detected_license = license_filename
                    break

    if detected_license == "UFL.txt" and familyname not in LEGACY_UFL_FAMILIES:
        yield FAIL, Message(
            "ufl",
            "The Ubuntu Font License is only acceptable on"
            " the Google Fonts collection for legacy font"
            " families that already adopted such license."
            " New Families should use eigther Apache or"
            " Open Font License.",
        )
    else:
        found_good_entry = False
        if not detected_license:
            yield SKIP, (
                "Could not infer the font license."
                " Please ensure NameID 13 (LICENSE DESCRIPTION) is properly set."
            )
            return
        else:
            passed = True
            expected = LICENSE_URL[detected_license]
            for nameRecord in ttFont["name"].names:
                if nameRecord.nameID == NameID.LICENSE_INFO_URL:
                    string = nameRecord.string.decode(nameRecord.getEncoding())
                    if "http://" in string:
                        yield WARN, Message(
                            "http-in-license-info",
                            f"Please consider using HTTPS URLs at"
                            f" name table entry [plat={nameRecord.platformID},"
                            f" enc={nameRecord.platEncID},"
                            f" name={nameRecord.nameID}]",
                        )
                        string = "https://".join(string.split("http://"))
                    if string == expected:
                        found_good_entry = True
                    elif "scripts.sil.org/OFL" in string:
                        found_good_entry = True
                        yield WARN, Message(
                            "deprecated-ofl-url",
                            'OFL url is no longer "https://scripts.sil.org/OFL". '
                            "Use 'https://openfontlicense.org' instead.",
                        )
                    else:
                        passed = False
                        yield FAIL, Message(
                            "licensing-inconsistency",
                            f"Licensing inconsistency in name table entries!"
                            f" NameID={NameID.LICENSE_DESCRIPTION}"
                            f" (LICENSE DESCRIPTION) indicates"
                            f" {LICENSE_NAME[detected_license]} licensing,"
                            f" but NameID={NameID.LICENSE_INFO_URL}"
                            f" (LICENSE URL) has '{string}'."
                            f" Expected: '{expected}'",
                        )
        if http_warn:
            yield WARN, Message(
                "http",
                "For now we're still accepting http URLs,"
                " but you should consider using https instead.\n",
            )

        if not found_good_entry:
            yield FAIL, Message(
                "no-license-found",
                f"A known license URL must be provided in"
                f" the NameID {NameID.LICENSE_INFO_URL}"
                f" (LICENSE INFO URL) entry."
                f" Currently accepted licenses are"
                f" Apache: '{LICENSE_URL['LICENSE.txt']}'"
                f" or Open Font License: '{LICENSE_URL['OFL.txt']}'"
                f"\n"
                f"For a small set of legacy families the Ubuntu"
                f" Font License '{LICENSE_URL['UFL.txt']}' may be"
                f" acceptable as well."
                f"\n"
                f"When in doubt, please choose OFL for"
                f" new font projects.",
            )
        else:
            if passed:
                yield PASS, "Font has a valid license URL in NAME table."
            else:
                yield FAIL, Message(
                    "bad-entries",
                    f"Even though a valid license URL was seen in the"
                    f" name table, there were also bad entries."
                    f" Please review NameIDs {NameID.LICENSE_DESCRIPTION}"
                    f" (LICENSE DESCRIPTION) and {NameID.LICENSE_INFO_URL}"
                    f" (LICENSE INFO URL).",
                )
