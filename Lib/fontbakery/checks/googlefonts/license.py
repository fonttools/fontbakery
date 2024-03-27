from difflib import Differ
import os

from fontbakery.constants import NameID, PlatformID
from fontbakery.prelude import check, condition, Message, INFO, PASS, FAIL, WARN, SKIP
from fontbakery.testable import Font
from fontbakery.checks.googlefonts.constants import (
    DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    EXPECTED_COPYRIGHT_PATTERN,
)


def git_rootdir(family_dir):
    if not family_dir:
        return None

    original_dir = os.getcwd()
    root_dir = None
    import subprocess

    try:
        os.chdir(family_dir)
        git_cmd = ["git", "rev-parse", "--show-toplevel"]
        git_output = subprocess.check_output(git_cmd, stderr=subprocess.STDOUT)
        root_dir = git_output.decode("utf-8").strip()

    except (OSError, IOError, subprocess.CalledProcessError):
        pass  # Not a git repo, or git is not installed.

    os.chdir(original_dir)
    return root_dir


@condition(Font)
def licenses(font):
    """Get a list of paths for every license
    file found in a font project."""
    found = []
    family_directory = font.family_directory
    search_paths = [family_directory]
    gitroot = git_rootdir(family_directory)
    if gitroot and gitroot not in search_paths:
        search_paths.append(gitroot)

    for directory in search_paths:
        if directory:
            for license_filename in ["OFL.txt", "LICENSE.txt"]:
                license_path = os.path.join(directory, license_filename)
                if os.path.exists(license_path):
                    found.append(license_path)
    return found


@condition(Font)
def license_contents(font):
    if font.license_path:
        return open(font.license_path, encoding="utf-8").read().replace(" \n", "\n")


@condition(Font)
def license_path(font):
    """Get license path."""
    # This assumes that a repo can have multiple license files
    # and they're all the same.
    # FIXME: We should have a fontbakery check for that, though!
    if font.licenses and len(font.licenses) > 0:
        return font.licenses[0]


@condition(Font)
def license_filename(font):
    """Get license filename."""
    if font.license_path:
        return os.path.basename(font.license_path)


@condition(Font)
def is_ofl(font):
    return font.license_filename and "OFL" in font.license_filename


@check(
    id="com.google.fonts/check/family/has_license",
    conditions=["gfonts_repo_structure"],
    proposal="legacy:check/028",
    rationale="""
        A license file is required for all fonts in the Google Fonts collection.
        This checks that the font's directory contains a file named OFL.txt or
        LICENSE.txt.
    """,
)
def com_google_fonts_check_family_has_license(licenses, config):
    """Check font has a license."""
    from fontbakery.utils import pretty_print_list

    if len(licenses) > 1:
        filenames = [os.path.basename(f) for f in licenses]
        yield FAIL, Message(
            "multiple",
            f"More than a single license file found:"
            f" {pretty_print_list(config, filenames)}",
        )
    elif not licenses:
        yield FAIL, Message(
            "no-license",
            "No license file was found."
            " Please add an OFL.txt or a LICENSE.txt file."
            " If you are running fontbakery on a Google Fonts"
            " upstream repo, which is fine, just make sure"
            " there is a temporary license file in the same folder.",
        )


@check(
    id="com.google.fonts/check/license/OFL_copyright",
    conditions=["license_contents"],
    rationale="""
        An OFL.txt file's first line should be the font copyright.

    """
    + DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    severity=10,  # max severity because licensing mistakes can cause legal problems.
    proposal="https://github.com/fonttools/fontbakery/issues/2764",
)
def com_google_fonts_check_license_OFL_copyright(license_contents):
    """Check license file has good copyright string."""
    import re

    string = license_contents.strip().split("\n")[0].lower()
    if not re.search(EXPECTED_COPYRIGHT_PATTERN, string):
        yield FAIL, Message(
            "bad-format",
            f"First line in license file is:\n\n"
            f'"{string}"\n\n'
            f"which does not match the expected format, similar to:\n\n"
            f'"Copyright 2022 The Familyname Project Authors (git url)"',
        )


@check(
    id="com.google.fonts/check/license/OFL_body_text",
    conditions=["is_ofl", "license_contents"],
    rationale="""
        Check OFL body text is correct.
        Often users will accidently delete parts of the body text.
    """,
    severity=10,  # max severity because licensing mistakes can cause legal problems.
    proposal="https://github.com/fonttools/fontbakery/issues/3352",
)
def com_google_fonts_check_license_OFL_body_text(license_contents):
    """Check OFL body text is correct."""
    from fontbakery.constants import OFL_BODY_TEXT

    # apply replacements so we get ideal license contents as of 2024.
    # We want https and openfontslicense.org as the url. We also don't
    # seem to care if the last line is an empty line.
    # Not having these will raise warns in other checks.
    if license_contents[-1] == "\n":
        license_contents = license_contents[:-1]
    license_contents = (
        license_contents.replace("http://", "https://")
        .replace(
            "https://scripts.sil.org/OFL",
            "https://openfontlicense.org",
        )
        .replace("<", "\\<")
        .splitlines(keepends=True)[1:]
    )

    diff = Differ()
    res = diff.compare(OFL_BODY_TEXT.splitlines(keepends=True), license_contents)

    changed_lines = [
        f"\\{line}".replace("\n", "\\n") for line in res if line.startswith(("-", "+"))
    ]

    if changed_lines:
        output = "\n\n".join(changed_lines)
        yield WARN, Message(
            "incorrect-ofl-body-text",
            "The OFL.txt body text is incorrect. Please use "
            "https://github.com/googlefonts/Unified-Font-Repository"
            "/blob/main/OFL.txt as a template. "
            "You should only modify the first line.\n\n"
            "Lines changed:\n\n"
            f"{output}\n\n",
        )


@check(
    id="com.google.fonts/check/name/license",
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
    proposal="legacy:check/029",
)
def com_google_fonts_check_name_license(ttFont, license_filename):
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


@check(
    id="com.google.fonts/check/name/license_url",
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
        "legacy:check/030",
        "https://github.com/fonttools/fontbakery/issues/4358",
    ],
)
def com_google_fonts_check_name_license_url(ttFont, familyname):
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


@check(
    id="com.google.fonts/check/metadata/license",
    conditions=["family_metadata"],
    proposal="legacy:check/085",
    rationale="""
        The license field in METADATA.pb must contain one of the
        three values "APACHE2", "UFL" or "OFL". (New fonts should
        generally be OFL unless there are special circumstances.)
    """,
)
def com_google_fonts_check_metadata_license(family_metadata):
    """METADATA.pb license is "APACHE2", "UFL" or "OFL"?"""
    expected_licenses = ["APACHE2", "OFL", "UFL"]
    if not family_metadata.license in expected_licenses:
        yield FAIL, Message(
            "bad-license",
            f'METADATA.pb license field ("{family_metadata.license}")'
            f" must be one of the following: {expected_licenses}",
        )


@check(
    id="com.google.fonts/check/epar",
    rationale="""
        The EPAR table is/was a way of expressing common licensing permissions and
        restrictions in metadata; while almost nothing supported it, Dave Crossland
        wonders that adding it to everything in Google Fonts could help make it
        more popular.

        More info is available at:
        https://davelab6.github.io/epar/
    """,
    severity=1,
    proposal="https://github.com/fonttools/fontbakery/issues/226",
)
def com_google_fonts_check_epar(ttFont):
    """EPAR table present in font?"""

    if "EPAR" not in ttFont:
        yield INFO, Message(
            "lacks-EPAR",
            "EPAR table not present in font. To learn more see"
            " https://github.com/fonttools/fontbakery/issues/818",
        )


# Although this is a /name/ check, it's really about licensing
@check(
    id="com.google.fonts/check/name/rfn",
    rationale="""
        Some designers adopt the "Reserved Font Name" clause of the OFL license. This
        means that the original author reserves the rights to the family name and other
        people can only distribute modified versions using a different family name.

        Google Fonts published updates to the fonts in the collection in order to fix
        issues and/or implement further improvements to the fonts. It is important to
        keep the family name so that users of the webfonts can benefit from the updates.
        Since it would forbid such usage scenario, all families in the GFonts collection
        are required to not adopt the RFN clause.

        This check ensures "Reserved Font Name" is not mentioned in the name table.
    """,
    conditions=["not rfn_exception"],
    proposal="https://github.com/fonttools/fontbakery/issues/1380",
)
def com_google_fonts_check_name_rfn(ttFont, familyname):
    """Name table strings must not contain the string 'Reserved Font Name'."""
    for entry in ttFont["name"].names:
        string = entry.toUnicode()
        if "This license is copied below, and is also available with a FAQ" in string:
            # This is the OFL text in a name table entry.
            # It contains the term 'Reserved Font Name' in one of its clauses,
            # so we will ignore this here.
            continue

        import re

        matches = re.search(r"with [Rr]eserved [Ff]ont [Nn]ame (.*)\.", string)

        if matches:
            reserved_font_name = matches.group(1)
            if reserved_font_name in familyname:
                yield FAIL, Message(
                    "rfn",
                    f'Name table entry contains "Reserved Font Name":\n'
                    f'\t"{string}"\n'
                    f"\n"
                    f"This is an error except in a few specific rare cases.",
                )
            else:
                yield WARN, Message(
                    "legacy-familyname",
                    f'Name table entry contains "Reserved Font Name" for a'
                    f" family name ({reserved_font_name}) that differs"
                    f" from the currently used family name ({familyname}),"
                    f" which is fine.",
                )
