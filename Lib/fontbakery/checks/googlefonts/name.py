from fontbakery.checks.googlefonts.conditions import expected_font_names
from fontbakery.prelude import check, disable, Message, PASS, FAIL, WARN
from fontbakery.constants import (
    RIBBI_STYLE_NAMES,
    NameID,
    PlatformID,
)
from fontbakery.utils import markdown_table


@check(id="com.google.fonts/check/name/unwanted_chars", proposal="legacy:check/019")
def com_google_fonts_check_name_unwanted_chars(ttFont):
    """Substitute copyright, registered and trademark
    symbols in name table entries."""
    passed = True
    replacement_map = [("\u00a9", "(c)"), ("\u00ae", "(r)"), ("\u2122", "(tm)")]
    for name in ttFont["name"].names:
        string = str(name.string, encoding=name.getEncoding())
        for mark, ascii_repl in replacement_map:
            new_string = string.replace(mark, ascii_repl)
            if string != new_string:
                yield FAIL, Message(
                    "unwanted-chars",
                    f"NAMEID #{name.nameID} contains symbols that"
                    f" should be replaced by '{ascii_repl}'.",
                )
                passed = False
    if passed:
        yield PASS, (
            "No need to substitute copyright, registered and"
            " trademark symbols in name table entries of this font."
        )


@check(
    id="com.google.fonts/check/name/description_max_length",
    rationale="""
        An old FontLab version had a bug which caused it to store copyright notices
        in nameID 10 entries.

        In order to detect those and distinguish them from actual legitimate usage of
        this name table entry, we expect that such strings do not exceed a reasonable
        length of 200 chars.

        Longer strings are likely instances of the FontLab bug.
    """,
    proposal="legacy:check/032",
)
def com_google_fonts_check_name_description_max_length(ttFont):
    """Description strings in the name table must not exceed 200 characters."""
    passed = True
    for name in ttFont["name"].names:
        if (
            name.nameID == NameID.DESCRIPTION
            and len(name.string.decode(name.getEncoding())) > 200
        ):
            passed = False
            break

    if passed:
        yield PASS, "All description name records have reasonably small lengths."
    else:
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


@check(id="com.google.fonts/check/name/version_format", proposal="legacy:check/055")
def com_google_fonts_check_name_version_format(ttFont):
    """Version format is correct in 'name' table?"""
    from fontbakery.utils import get_name_entry_strings
    import re

    def is_valid_version_format(value):
        return re.match(r"Version\s0*[1-9][0-9]*\.\d+", value)

    passed = True
    version_entries = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    if len(version_entries) == 0:
        passed = False
        yield FAIL, Message(
            "no-version-string",
            f"Font lacks a NameID.VERSION_STRING"
            f" (nameID={NameID.VERSION_STRING}) entry",
        )
    for ventry in version_entries:
        if not is_valid_version_format(ventry):
            passed = False
            yield FAIL, Message(
                "bad-version-strings",
                f"The NameID.VERSION_STRING"
                f" (nameID={NameID.VERSION_STRING}) value must"
                f' follow the pattern "Version X.Y" with X.Y'
                f" greater than or equal to 1.000."
                f' Current version string is: "{ventry}"',
            )
    if passed:
        yield PASS, "Version format in NAME table entries is correct."


@check(
    id="com.google.fonts/check/name/familyname_first_char",
    rationale="""
        Font family names which start with a numeral are often not discoverable
        in Windows applications.
    """,
    proposal="legacy:check/067",
)
def com_google_fonts_check_name_familyname_first_char(ttFont):
    """Make sure family name does not begin with a digit."""
    from fontbakery.utils import get_name_entry_strings

    passed = True
    for familyname in get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME):
        digits = map(str, range(0, 10))
        if familyname[0] in digits:
            yield FAIL, Message(
                "begins-with-digit",
                f"Font family name '{familyname}' begins with a digit!",
            )
            passed = False
    if passed:
        yield PASS, "Font family name first character is not a digit."


@check(
    id="com.google.fonts/check/name/ascii_only_entries",
    rationale="""
        The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).

        For COPYRIGHT_NOTICE (nameID 0) ASCII is required because that string should be
        the same in CFF fonts which also have this requirement in the OpenType spec.

        Note:
        A common place where we find non-ASCII strings is on name table entries
        with NameID > 18, which are expressly for localising the ASCII-only IDs
        into Hindi / Arabic / etc.
    """,
    proposal=[
        "legacy:check/074",
        "https://github.com/fonttools/fontbakery/issues/1663",
    ],
)
def com_google_fonts_check_name_ascii_only_entries(ttFont):
    """Are there non-ASCII characters in ASCII-only NAME table entries?"""
    bad_entries = []
    for name in ttFont["name"].names:
        if name.nameID in (NameID.COPYRIGHT_NOTICE, NameID.POSTSCRIPT_NAME):
            string = name.string.decode(name.getEncoding())
            try:
                string.encode("ascii")
            except UnicodeEncodeError:
                bad_entries.append(name)
                badstring = string.encode("ascii", errors="xmlcharrefreplace")
                yield FAIL, Message(
                    "bad-string",
                    (
                        f"Bad string at"
                        f" [nameID {name.nameID}, '{name.getEncoding()}']:"
                        f" '{badstring}'"
                    ),
                )
    if len(bad_entries) > 0:
        yield FAIL, Message(
            "non-ascii-strings",
            (
                f"There are {len(bad_entries)} strings containing"
                " non-ASCII characters in the ASCII-only"
                " NAME table entries."
            ),
        )
    else:
        yield PASS, (
            "None of the ASCII-only NAME table entries"
            " contain non-ASCII characteres."
        )


@check(
    id="com.google.fonts/check/font_names",
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
def com_google_fonts_check_font_names(ttFont, ttFonts):
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
    else:
        yield PASS, f"Font names are good:\n\n{md_table}"


@check(
    id="com.google.fonts/check/name/mandatory_entries",
    conditions=["style"],
    proposal="legacy:check/156",
)
def com_google_fonts_check_name_mandatory_entries(ttFont, style):
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
    passed = True
    # The font must have at least these name IDs:
    for nameId in required_nameIDs:
        if len(get_name_entry_strings(ttFont, nameId)) == 0:
            passed = False
            yield FAIL, Message(
                "missing-entry",
                f"Font lacks entry with nameId={nameId}" f" ({NameID(nameId).name})",
            )
    if passed:
        yield PASS, "Font contains values for all mandatory name table entries."


@check(
    id="com.google.fonts/check/name/family_and_style_max_length",
    rationale="""
        This check ensures that the length of name table entries is not
        too long, as this causes problems in some environments.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1488",
        "https://github.com/fonttools/fontbakery/issues/2179",
    ],
)
def com_google_fonts_check_name_family_and_style_max_length(ttFont):
    """Combined length of family and style must not exceed 32 characters."""
    from fontbakery.utils import get_name_entry_strings
    import re

    ribbi_re = " (" + "|".join(RIBBI_STYLE_NAMES) + ")$"

    passed = True

    def strip_ribbi(x):
        return re.sub(ribbi_re, "", x)

    checks = [
        [
            FAIL,
            NameID.FULL_FONT_NAME,
            32,
            (
                "with the dropdown menu in old versions of Microsoft Word"
                " as well as shaping issues for some accented letters in"
                " Microsoft Word on Windows 10 and 11"
            ),
            strip_ribbi,
        ],
        [
            WARN,
            NameID.POSTSCRIPT_NAME,
            27,
            "with PostScript printers, especially on Mac platforms",
            lambda x: x,
        ],
    ]
    for loglevel, nameid, maxlen, reason, transform in checks:
        for the_name in get_name_entry_strings(ttFont, nameid):
            the_name = transform(the_name)
            if len(the_name) > maxlen:
                passed = False
                yield loglevel, Message(
                    f"nameid{nameid}-too-long",
                    f"Name ID {nameid} '{the_name}' exceeds"
                    f" {maxlen} characters. This has been found to"
                    f" cause problems {reason}.",
                )

    # name ID 1 + fvar instance name > 32 : FAIL : problems with Windows
    if "fvar" in ttFont:
        for instance in ttFont["fvar"].instances:
            for instance_name in get_name_entry_strings(
                ttFont, instance.subfamilyNameID
            ):
                for family_name in get_name_entry_strings(
                    ttFont, NameID.FONT_FAMILY_NAME
                ):
                    full_instance_name = instance_name + " " + family_name
                    if len(full_instance_name) > 32:
                        yield FAIL, Message(
                            "instance-too-long",
                            f"Variable font instance name '{full_instance_name}'"
                            f" formed by space-separated concatenation of"
                            f" instance subfamily nameID {instance.subfamilyNameID}"
                            f" and font family name (nameID {NameID.FONT_FAMILY_NAME})"
                            f" exceeds 32 characters.\n\n"
                            f"This has been found to cause shaping issues for some"
                            f" accented letters in Microsoft Word on Windows 10 and 11.",
                        )

    if passed:
        yield PASS, "All name entries are good."


@disable
@check(
    id="com.google.fonts/check/glyphs_file/name/family_and_style_max_length",
)
def com_google_fonts_check_glyphs_file_name_family_and_style_max_length(glyphsFile):
    """Combined length of family and style must not exceed 27 characters."""

    too_long = []
    for instance in glyphsFile.instances:
        if len(instance.fullName) > 27:
            too_long.append(instance.fullName)

    if too_long:
        too_long_list = "\n  - " + "\n  - ".join(too_long)
        yield WARN, Message(
            "too-long",
            f"The fullName length exceeds 27 chars in the"
            f" following entries:\n"
            f"{too_long_list}\n"
            f"\n"
            f"Please take a look at the conversation at"
            f" https://github.com/fonttools/fontbakery/issues/2179"
            f" in order to understand the reasoning behind these"
            f" name table records max-length criteria.",
        )
    else:
        yield PASS, "ok"


@check(
    id="com.google.fonts/check/name/line_breaks",
    rationale="""
        There are some entries on the name table that may include more than one line
        of text. The Google Fonts team, though, prefers to keep the name table entries
        short and simple without line breaks.

        For instance, some designers like to include the full text of a font license in
        the "copyright notice" entry, but for the GFonts collection this entry should
        only mention year, author and other basic info in a manner enforced by
        com.google.fonts/check/font_copyright
    """,
    proposal="legacy:check/057",
)
def com_google_fonts_check_name_line_breaks(ttFont):
    """Name table entries should not contain line-breaks."""
    passed = True
    for name in ttFont["name"].names:
        string = name.string.decode(name.getEncoding())
        if "\n" in string:
            passed = False
            yield FAIL, Message(
                "line-break",
                f"Name entry {NameID(name.nameID).name}"
                f" on platform {PlatformID(name.platformID).name}"
                f" contains a line-break.",
            )
    if passed:
        yield PASS, "Name table entries are all single-line (no line-breaks found)."


@check(
    id="com.google.fonts/check/name/family_name_compliance",
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
def com_google_fonts_check_name_family_name_compliance(ttFont):
    """Check family name for GF Guide compliance."""
    import re
    from pkg_resources import resource_filename
    from fontbakery.utils import get_name_entries

    camelcase_exceptions_txt = "data/googlefonts/camelcased_familyname_exceptions.txt"
    abbreviations_exceptions_txt = (
        "data/googlefonts/abbreviations_familyname_exceptions.txt"
    )
    passed = True

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
            passed = False
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
                passed = False
                yield FAIL, Message(
                    "abbreviation", f'"{family_name}" contains an abbreviation.'
                )

    # Allowed characters
    forbidden_characters = re.findall(r"[^a-zA-Z0-9 ]", family_name)
    if forbidden_characters:
        forbidden_characters = "".join(sorted(list(set(forbidden_characters))))
        passed = False
        yield FAIL, Message(
            "forbidden-characters",
            f'"{family_name}" contains the following characters'
            f' which are not allowed: "{forbidden_characters}".',
        )

    # Starts with uppercase
    if not bool(re.match(r"^[A-Z]", family_name)):
        passed = False
        yield FAIL, Message(
            "starts-with-not-uppercase",
            f'"{family_name}" doesn\'t start with an uppercase letter.',
        )

    if passed:
        yield PASS, "Font name looks good."
