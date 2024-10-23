from fontbakery.checks.vendorspecific.googlefonts.conditions import expected_font_names
from fontbakery.prelude import check, Message, PASS, FAIL, WARN
from fontbakery.constants import (
    RIBBI_STYLE_NAMES,
    NameID,
    PlatformID,
)
from fontbakery.utils import markdown_table


@check(
    id="googlefonts/name/description_max_length",
    rationale="""
        An old FontLab version had a bug which caused it to store copyright notices
        in nameID 10 entries.

        In order to detect those and distinguish them from actual legitimate usage of
        this name table entry, we expect that such strings do not exceed a reasonable
        length of 200 chars.

        Longer strings are likely instances of the FontLab bug.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_description_max_length(ttFont):
    """Description strings in the name table must not exceed 200 characters."""
    for name in ttFont["name"].names:
        if (
            name.nameID == NameID.DESCRIPTION
            and len(name.string.decode(name.getEncoding())) > 200
        ):
            yield WARN, Message(
                "too-long",
                f"A few name table entries with ID={NameID.DESCRIPTION}"
                f" (NameID.DESCRIPTION) are longer than 200 characters."
                f" Please check whether those entries are copyright"
                f" notices mistakenly stored in the description"
                f" string entries by a bug in an old FontLab version."
                f" If that's the case, then such copyright notices"
                f" must be removed from these entries.",
            )
            return


@check(
    id="googlefonts/name/version_format",
    rationale="""
        For Google Fonts, the version string must be in the format "Version X.Y".
        The version number must be greater than or equal to 1.000. (Additional
        information following the numeric version number is acceptable.)
        The "Version " prefix is a recommendation given by the OpenType spec.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_version_format(ttFont):
    """Version format is correct in 'name' table?"""
    from fontbakery.utils import get_name_entry_strings
    import re

    def is_valid_version_format(value):
        return re.match(r"Version\s0*[1-9][0-9]*\.\d+", value)

    version_entries = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    if len(version_entries) == 0:
        yield FAIL, Message(
            "no-version-string",
            f"Font lacks a NameID.VERSION_STRING"
            f" (nameID={NameID.VERSION_STRING}) entry",
        )
    for ventry in version_entries:
        if not is_valid_version_format(ventry):
            yield FAIL, Message(
                "bad-version-strings",
                f"The NameID.VERSION_STRING"
                f" (nameID={NameID.VERSION_STRING}) value must"
                f' follow the pattern "Version X.Y" with X.Y'
                f" greater than or equal to 1.000."
                f' The "Version " prefix is a recommendation'
                f" given by the OpenType spec."
                f' Current version string is: "{ventry}"',
            )


@check(
    id="googlefonts/name/familyname_first_char",
    rationale="""
        Font family names which start with a numeral are often not discoverable
        in Windows applications.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_familyname_first_char(ttFont):
    """Make sure family name does not begin with a digit."""
    from fontbakery.utils import get_name_entry_strings

    for familyname in get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME):
        digits = map(str, range(0, 10))
        if familyname[0] in digits:
            yield FAIL, Message(
                "begins-with-digit",
                f"Font family name '{familyname}' begins with a digit!",
            )


@check(
    id="googlefonts/font_names",
    rationale="""
        Google Fonts has several rules which need to be adhered to when
        setting a font's name table. Please read:
        https://googlefonts.github.io/gf-guide/statics.html#supported-styles
        https://googlefonts.github.io/gf-guide/statics.html#style-linking
        https://googlefonts.github.io/gf-guide/statics.html#unsupported-styles
        https://googlefonts.github.io/gf-guide/statics.html#single-weight-families
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3800",
)
def check_font_names(ttFont, ttFonts):
    """Check font names are correct"""
    expected_names = expected_font_names(ttFont, ttFonts)

    def style_names(nametable):
        res = {}
        for nameID in (
            NameID.FONT_FAMILY_NAME,
            NameID.FONT_SUBFAMILY_NAME,
            NameID.FULL_FONT_NAME,
            NameID.POSTSCRIPT_NAME,
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
        ):
            rec = nametable.getName(nameID, 3, 1, 0x409)
            if rec:
                res[nameID] = rec.toUnicode()
        return res

    font_names = style_names(ttFont["name"])
    expected_names = style_names(expected_names["name"])

    name_ids = {
        NameID.FONT_FAMILY_NAME: "Family Name",
        NameID.FONT_SUBFAMILY_NAME: "Subfamily Name",
        NameID.FULL_FONT_NAME: "Full Name",
        NameID.POSTSCRIPT_NAME: "Postscript Name",
        NameID.TYPOGRAPHIC_FAMILY_NAME: "Typographic Family Name",
        NameID.TYPOGRAPHIC_SUBFAMILY_NAME: "Typographic Subfamily Name",
    }
    table = []
    for nameID in set(font_names.keys()) | set(expected_names.keys()):
        id_name = name_ids[nameID]
        row = {"nameID": id_name}
        if nameID in font_names:
            row["current"] = font_names[nameID]
        else:
            row["current"] = "N/A"
        if nameID in expected_names:
            row["expected"] = expected_names[nameID]
        else:
            row["expected"] = "N/A"
        if row["current"] != row["expected"]:
            row["current"] = "**" + row["current"] + "**"
            row["expected"] = "**" + row["expected"] + "**"
        table.append(row)

    new_names = set(font_names) - set(expected_names)
    missing_names = set(expected_names) - set(font_names)
    same_names = set(font_names) & set(expected_names)

    md_table = markdown_table(table)

    passed = True
    if new_names or missing_names:
        passed = False

    for nameID in same_names:
        if nameID == NameID.FULL_FONT_NAME and all(
            [
                " Regular" in expected_names[nameID],
                font_names[nameID] == expected_names[nameID].replace(" Regular", ""),
            ]
        ):
            yield WARN, Message("lacks-regular", "Regular missing from full name")
        elif font_names[nameID] != expected_names[nameID]:
            passed = False

    if not passed:
        yield FAIL, Message("bad-names", f"Font names are incorrect:\n\n{md_table}")


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
                f"Font lacks entry with nameId={nameId}" f" ({NameID(nameId).name})",
            )


@check(
    id="googlefonts/name/line_breaks",
    rationale="""
        There are some entries on the name table that may include more than one line
        of text. The Google Fonts team, though, prefers to keep the name table entries
        short and simple without line breaks.

        For instance, some designers like to include the full text of a font license in
        the "copyright notice" entry, but for the GFonts collection this entry should
        only mention year, author and other basic info in a manner enforced by
        `googlefonts/font_copyright`
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_line_breaks(ttFont):
    """Name table entries should not contain line-breaks."""
    for name in ttFont["name"].names:
        string = name.string.decode(name.getEncoding())
        if "\n" in string:
            yield FAIL, Message(
                "line-break",
                f"Name entry {NameID(name.nameID).name}"
                f" on platform {PlatformID(name.platformID).name}"
                f" contains a line-break.",
            )


@check(
    id="googlefonts/name/family_name_compliance",
    rationale="""
        Checks the family name for compliance with the Google Fonts Guide.
        https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts

        If you want to have your family name added to the CamelCase
        exceptions list, please submit a pull request to the
        camelcased_familyname_exceptions.txt file.

        Similarly, abbreviations can be submitted to the
        abbreviations_familyname_exceptions.txt file.

        These are located in the Lib/fontbakery/data/googlefonts/ directory
        of the FontBakery source code currently hosted at
        https://github.com/fonttools/fontbakery/
    """,
    conditions=[],
    proposal="https://github.com/fonttools/fontbakery/issues/4049",
)
def check_name_family_name_compliance(ttFont):
    """Check family name for GF Guide compliance."""
    import re
    from pkg_resources import resource_filename
    from fontbakery.utils import get_name_entries

    camelcase_exceptions_txt = "data/googlefonts/camelcased_familyname_exceptions.txt"
    abbreviations_exceptions_txt = (
        "data/googlefonts/abbreviations_familyname_exceptions.txt"
    )

    if get_name_entries(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME):
        family_name = get_name_entries(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)[
            0
        ].toUnicode()
    else:
        family_name = get_name_entries(ttFont, NameID.FONT_FAMILY_NAME)[0].toUnicode()

    # CamelCase
    if bool(re.match(r"([A-Z][a-z]+){2,}", family_name)):
        known_exception = False

        # Process exceptions
        filename = resource_filename("fontbakery", camelcase_exceptions_txt)
        for exception in open(filename, "r", encoding="utf-8").readlines():
            exception = exception.split("#")[0].strip()
            if exception == "":
                continue
            if exception in family_name:
                known_exception = True
                yield PASS, Message(
                    "known-camelcase-exception",
                    "Family name is a known exception to the CamelCase rule.",
                )
                break

        if not known_exception:
            yield FAIL, Message(
                "camelcase",
                f'"{family_name}" is a CamelCased name.'
                f" To solve this, simply use spaces"
                f" instead in the font name.",
            )

    # Abbreviations
    if bool(re.match(r"([A-Z]){2,}", family_name)):
        known_exception = False

        # Process exceptions
        filename = resource_filename("fontbakery", abbreviations_exceptions_txt)
        for exception in open(filename, "r", encoding="utf-8").readlines():
            exception = exception.split("#")[0].strip()
            if exception == "":
                continue
            if exception in family_name:
                known_exception = True
                yield PASS, Message(
                    "known-abbreviation-exception",
                    "Family name is a known exception to the abbreviation rule.",
                )
                break

        if not known_exception:
            # Allow SC ending
            if not family_name.endswith("SC"):
                yield FAIL, Message(
                    "abbreviation", f'"{family_name}" contains an abbreviation.'
                )

    # Allowed characters
    forbidden_characters = re.findall(r"[^a-zA-Z0-9 ]", family_name)
    if forbidden_characters:
        forbidden_characters = "".join(sorted(list(set(forbidden_characters))))
        yield FAIL, Message(
            "forbidden-characters",
            f'"{family_name}" contains the following characters'
            f' which are not allowed: "{forbidden_characters}".',
        )

    # Starts with uppercase
    if not bool(re.match(r"^[A-Z]", family_name)):
        yield FAIL, Message(
            "starts-with-not-uppercase",
            f'"{family_name}" doesn\'t start with an uppercase letter.',
        )
