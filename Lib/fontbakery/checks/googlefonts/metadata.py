import os

from fontbakery.constants import NameID, RIBBI_STYLE_NAMES
from fontbakery.prelude import check, Message, PASS, FAIL, WARN, SKIP, FATAL
from fontbakery.utils import exit_with_install_instructions
from fontbakery.checks.googlefonts.glyphset import can_shape


@check(
    id="com.google.fonts/check/metadata/parses",
    conditions=["family_directory"],
    rationale="""
        The purpose of this check is to ensure that the METADATA.pb file is not
        malformed.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2248",
)
def com_google_fonts_check_metadata_parses(family_directory):
    """Check METADATA.pb parse correctly."""
    try:
        from google.protobuf import text_format
        from fontbakery.utils import get_FamilyProto_Message
    except ImportError:
        exit_with_install_instructions()

    try:
        pb_file = os.path.join(family_directory, "METADATA.pb")
        get_FamilyProto_Message(pb_file)
        yield PASS, "METADATA.pb parsed successfuly."
    except text_format.ParseError as e:
        yield FATAL, Message(
            "parsing-error",
            f"Family metadata at {family_directory} failed to parse.\n"
            f"TRACEBACK:\n{e}",
        )
    except FileNotFoundError:
        yield SKIP, Message(
            "file-not-found",
            f"Font family at '{family_directory}' lacks a METADATA.pb file.",
        )


@check(
    id="com.google.fonts/check/metadata/unknown_designer",
    conditions=["family_metadata"],
    proposal=[
        "legacy:check/007",
        "https://github.com/fonttools/fontbakery/issues/800",
    ],
)
def com_google_fonts_check_metadata_unknown_designer(family_metadata):
    """Font designer field in METADATA.pb must not be 'unknown'."""
    if family_metadata.designer.lower() == "unknown":
        yield FAIL, Message(
            "unknown-designer", f"Font designer field is '{family_metadata.designer}'."
        )
    else:
        yield PASS, "Font designer field is not 'unknown'."


@check(
    id="com.google.fonts/check/metadata/multiple_designers",
    conditions=["family_metadata"],
    rationale="""
        For a while the string "Multiple designers" was used as a placeholder on
        METADATA.pb files. We should replace all those instances with actual designer
        names so that proper credits are displayed on the Google Fonts family
        specimen pages.

        If there's more than a single designer, the designer names must be
        separated by commas.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2766",
)
def com_google_fonts_check_metadata_multiple_designers(family_metadata):
    """Font designer field in METADATA.pb must not contain 'Multiple designers'."""
    if "multiple designer" in family_metadata.designer.lower():
        yield FAIL, Message(
            "multiple-designers",
            f"Font designer field is '{family_metadata.designer}'."
            f" Please add an explicit comma-separated list of designer names.",
        )
    else:
        yield PASS, "Looks good."


@check(
    id="com.google.fonts/check/metadata/designer_values",
    conditions=["family_metadata"],
    rationale="""
        We must use commas instead of forward slashes because the server-side code
        at the fonts.google.com directory will segment the string on the commas into
        a list of names and display the first item in the list as the
        "principal designer" while the remaining names are identified as "contributors".

        See eg https://fonts.google.com/specimen/Rubik
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2479",
)
def com_google_fonts_check_metadata_designer_values(family_metadata):
    """Multiple values in font designer field in
    METADATA.pb must be separated by commas."""

    if "/" in family_metadata.designer:
        yield FAIL, Message(
            "slash",
            f"Font designer field contains a forward slash"
            f" '{family_metadata.designer}'."
            f" Please use commas to separate multiple names instead.",
        )
    else:
        yield PASS, "Looks good."


@check(
    id="com.google.fonts/check/metadata/broken_links",
    conditions=["network", "family_metadata"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/2550",
        "https://github.com/fonttools/fontbakery/issues/4110",
    ],
)
def com_google_fonts_check_metadata_broken_links(family_metadata):
    """Does METADATA.pb copyright field contain broken links?"""
    import requests

    passed = True
    broken_links = []
    unique_links = []
    for font_metadata in family_metadata.fonts:
        copyright_str = font_metadata.copyright
        if "mailto:" in copyright_str:
            # avoid reporting more then once
            if copyright_str in unique_links:
                continue

            unique_links.append(copyright_str)
            yield FAIL, Message("email", f"Found an email address: {copyright_str}")
            continue

        if "http" in copyright_str:
            link = "http" + copyright_str.split("http")[1]

            for endchar in [" ", ")"]:
                if endchar in link:
                    link = link.split(endchar)[0]

            # avoid requesting the same URL more then once
            if link in unique_links:
                continue

            unique_links.append(link)
            try:
                response = requests.head(link, allow_redirects=True, timeout=10)
                code = response.status_code
                # Status 429: "Too Many Requests" is acceptable
                # because it means the website is probably ok and
                # we're just perhaps being too agressive in probing the server!
                if code not in [requests.codes.ok, requests.codes.too_many_requests]:
                    # special case handling for github.com/$user/$repo/$something
                    chunks = link.split("/")
                    good = False
                    if len(chunks) == 6 and chunks[2].endswith("github.com"):
                        protocol, _, domain, user, repo, something = chunks
                        for branch in ["main", "master"]:
                            alternate_link = f"{protocol}//{domain}/{user}/{repo}/tree/{branch}/{something}"  # noqa:E501 pylint:disable=C0301
                            response = requests.head(
                                alternate_link, allow_redirects=True, timeout=10
                            )
                            code = response.status_code
                            if code in [
                                requests.codes.ok,
                                requests.codes.too_many_requests,
                            ]:
                                passed = False
                                yield WARN, Message(
                                    "bad-github-url",
                                    f"Could not fetch '{link}'.\n\n"
                                    f"But '{alternate_link}' seems to be good."
                                    f" Please consider using that instead.\n",
                                )
                                good = True
                    if not good:
                        passed = False
                        broken_links.append(("{} (status code: {})").format(link, code))
            except requests.exceptions.Timeout:
                passed = False
                yield WARN, Message(
                    "timeout",
                    f"Timed out while attempting to access: '{link}'."
                    f" Please verify if that's a broken link.",
                )
            except requests.exceptions.RequestException:
                broken_links.append("ouch! " + link)

    if len(broken_links) > 0:
        broken_links_list = "\n\t".join(broken_links)
        passed = False
        yield FAIL, Message(
            "broken-links",
            f"The following links are broken"
            f" in the METADATA.pb file:\n\t"
            f"{broken_links_list}",
        )

    if passed:
        yield PASS, "All links in the METADATA.pb file look good!"


@check(
    id="com.google.fonts/check/metadata/undeclared_fonts",
    conditions=["family_metadata"],
    rationale="""
        The set of font binaries available, except the ones on a "static" subdir,
        must match exactly those declared on the METADATA.pb file.

        Also, to avoid confusion, we expect that font files (other than statics)
        are not placed on subdirectories.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2575",
)
def com_google_fonts_check_metadata_undeclared_fonts(family_metadata, family_directory):
    """Ensure METADATA.pb lists all font binaries."""

    pb_binaries = []
    for font_metadata in family_metadata.fonts:
        pb_binaries.append(font_metadata.filename)

    passed = True
    binaries = []
    for entry in os.listdir(family_directory):
        if entry != "static" and os.path.isdir(os.path.join(family_directory, entry)):
            for filename in os.listdir(os.path.join(family_directory, entry)):
                if filename[-4:] in [".ttf", ".otf"]:
                    path = os.path.join(family_directory, entry, filename)
                    passed = False
                    yield WARN, Message(
                        "font-on-subdir",
                        f'The file "{path}" is a font binary'
                        f" in a subdirectory.\n"
                        f"Please keep all font files (except VF statics)"
                        f" directly on the root directory side-by-side"
                        f" with its corresponding METADATA.pb file.",
                    )
        else:
            # Note: This does not include any font binaries placed in a "static" subdir!
            if entry[-4:] in [".ttf", ".otf"]:
                binaries.append(entry)

    for filename in sorted(set(pb_binaries) - set(binaries)):
        passed = False
        yield FAIL, Message(
            "file-missing",
            f'The file "{filename}" declared on METADATA.pb'
            f" is not available in this directory.",
        )

    for filename in sorted(set(binaries) - set(pb_binaries)):
        passed = False
        yield FAIL, Message(
            "file-not-declared", f'The file "{filename}" is not declared on METADATA.pb'
        )

    if passed:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/metadata/category",
    conditions=["family_metadata"],
    rationale="""
        There are only five acceptable values for the category field in a METADATA.pb
        file:

        - MONOSPACE

        - SANS_SERIF

        - SERIF

        - DISPLAY

        - HANDWRITING

        This check is meant to avoid typos in this field.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2972",
)
def com_google_fonts_check_metadata_category(family_metadata):
    """Ensure METADATA.pb category field is valid."""
    ok = True
    for category in family_metadata.category:
        if category not in [
            "MONOSPACE",
            "SANS_SERIF",
            "SERIF",
            "DISPLAY",
            "HANDWRITING",
        ]:
            ok = False
            yield FAIL, Message(
                "bad-value",
                f'The field category has "{category}"' f" which is not valid.",
            )
    if ok:
        yield PASS, "OK!"


@check(
    id="com.google.fonts/check/metadata/menu_and_latin",
    conditions=["family_metadata"],
    proposal=[
        "legacy:check/086",
        "https://github.com/fonttools/fontbakery/issues/912#issuecomment-237935444",
    ],
)
def com_google_fonts_check_metadata_menu_and_latin(family_metadata):
    """METADATA.pb should contain at least "menu" and "latin" subsets."""
    missing = []
    for s in ["menu", "latin"]:
        if s not in list(family_metadata.subsets):
            missing.append(s)

    if missing:
        if len(missing) == 2:
            missing = "both"
        else:
            missing = f'"{missing[0]}"'

        yield FAIL, Message(
            "missing",
            f'Subsets "menu" and "latin" are mandatory,'
            f" but METADATA.pb is missing {missing}.",
        )
    else:
        yield PASS, 'METADATA.pb contains "menu" and "latin" subsets.'


@check(
    id="com.google.fonts/check/metadata/subsets_order",
    conditions=["family_metadata"],
    proposal="legacy:check/087",
)
def com_google_fonts_check_metadata_subsets_order(family_metadata):
    """METADATA.pb subsets should be alphabetically ordered."""
    expected = list(sorted(family_metadata.subsets))

    if list(family_metadata.subsets) != expected:
        yield FAIL, Message(
            "not-sorted",
            (
                "METADATA.pb subsets are not sorted "
                "in alphabetical order: Got ['{}']"
                " and expected ['{}']"
                ""
            ).format("', '".join(family_metadata.subsets), "', '".join(expected)),
        )
    else:
        yield PASS, "METADATA.pb subsets are sorted in alphabetical order."


@check(
    id="com.google.fonts/check/metadata/includes_production_subsets",
    conditions=["family_metadata", "production_metadata", "listed_on_gfonts_api"],
    rationale="""
        Check METADATA.pb file includes the same subsets as the family in production.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2989",
)
def com_google_fonts_check_metadata_includes_production_subsets(
    family_metadata, production_metadata
):
    """Check METADATA.pb includes production subsets."""
    prod_families_metadata = {
        i["family"]: i for i in production_metadata["familyMetadataList"]
    }
    prod_family_metadata = prod_families_metadata[family_metadata.name]

    prod_subsets = set(prod_family_metadata["subsets"])
    local_subsets = set(family_metadata.subsets)
    missing_subsets = prod_subsets - local_subsets
    if len(missing_subsets) > 0:
        yield FAIL, Message(
            "missing-subsets",
            f"The following subsets are missing [{', '.join(sorted(missing_subsets))}]",
        )
    else:
        yield PASS, "No missing subsets"


@check(
    id="com.google.fonts/check/metadata/copyright",
    conditions=["family_metadata"],
    proposal="legacy:check/088",
)
def com_google_fonts_check_metadata_copyright(family_metadata):
    """METADATA.pb: Copyright notice is the same in all fonts?"""
    copyright_str = None
    fail = False
    for f in family_metadata.fonts:
        if copyright_str and f.copyright != copyright_str:
            fail = True
        copyright_str = f.copyright
    if fail:
        yield FAIL, Message(
            "inconsistency",
            "METADATA.pb: Copyright field value is inconsistent across family",
        )
    else:
        yield PASS, "Copyright is consistent across family"


@check(
    id="com.google.fonts/check/metadata/familyname",
    conditions=["family_metadata"],
    proposal="legacy:check/089",
)
def com_google_fonts_check_metadata_familyname(family_metadata):
    """Check that METADATA.pb family values are all the same."""
    name = ""
    fail = False
    for f in family_metadata.fonts:
        if name and f.name != name:
            fail = True
        name = f.name
    if fail:
        yield FAIL, Message(
            "inconsistency",
            "METADATA.pb: Family name is not the same"
            ' in all metadata "fonts" items.',
        )
    else:
        yield PASS, (
            'METADATA.pb: Family name is the same in all metadata "fonts" items.'
        )


@check(
    id="com.google.fonts/check/metadata/has_regular",
    conditions=["family_metadata"],
    proposal="legacy:check/090",
)
def com_google_fonts_check_metadata_has_regular(font):
    """METADATA.pb: According to Google Fonts standards,
    families should have a Regular style.
    """
    if font.has_regular_style:
        yield PASS, "Family has a Regular style."
    else:
        yield FAIL, Message(
            "lacks-regular",
            "This family lacks a Regular"
            " (style: normal and weight: 400)"
            " as required by Google Fonts standards."
            " If family consists of a single-weight non-Regular style only,"
            " consider the Google Fonts specs for this case:"
            " https://github.com/googlefonts/gf-docs/tree/main/Spec#single-weight-families",  # noqa:E501 pylint:disable=C0301
        )


@check(
    id="com.google.fonts/check/metadata/regular_is_400",
    conditions=["family_metadata", "has_regular_style"],
    proposal="legacy:check/091",
)
def com_google_fonts_check_metadata_regular_is_400(family_metadata):
    """METADATA.pb: Regular should be 400."""
    badfonts = []
    for f in family_metadata.fonts:
        if f.full_name.endswith("Regular") and f.weight != 400:
            badfonts.append(f"{f.filename} (weight: {f.weight})")
    if len(badfonts) > 0:
        yield FAIL, Message(
            "not-400",
            f"METADATA.pb: Regular font weight must be 400."
            f' Please fix these: {", ".join(badfonts)}',
        )
    else:
        yield PASS, "Regular has weight = 400."


@check(
    id="com.google.fonts/check/metadata/nameid/family_name",
    conditions=["font_metadata"],
    proposal="legacy:check/092",
)
def com_google_fonts_check_metadata_nameid_family_name(ttFont, font_metadata):
    """Checks METADATA.pb font.name field matches
    family name declared on the name table.
    """
    from fontbakery.utils import get_name_entry_strings

    familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
    if not familynames:
        familynames = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
    if len(familynames) == 0:
        yield FAIL, Message(
            "missing",
            (
                f"This font lacks a FONT_FAMILY_NAME entry"
                f" (nameID = {NameID.FONT_FAMILY_NAME})"
                f" in the name table."
            ),
        )
    else:
        if font_metadata.name not in familynames:
            yield FAIL, Message(
                "mismatch",
                (
                    f"Unmatched family name in font:"
                    f' TTF has "{familynames[0]}" while METADATA.pb'
                    f' has "{font_metadata.name}"'
                ),
            )
        else:
            yield PASS, (
                f'Family name "{font_metadata.name}" is identical'
                f" in METADATA.pb and on the TTF file."
            )


@check(
    id="com.google.fonts/check/metadata/nameid/post_script_name",
    conditions=["font_metadata"],
    proposal="legacy:093",
)
def com_google_fonts_check_metadata_nameid_post_script_name(ttFont, font_metadata):
    """Checks METADATA.pb font.post_script_name matches
    postscript name declared on the name table.
    """
    passed = True
    from fontbakery.utils import get_name_entry_strings

    postscript_names = get_name_entry_strings(ttFont, NameID.POSTSCRIPT_NAME)
    if len(postscript_names) == 0:
        passed = False
        yield FAIL, Message(
            "missing",
            (
                f"This font lacks a POSTSCRIPT_NAME entry"
                f" (nameID = {NameID.POSTSCRIPT_NAME})"
                f" in the name table."
            ),
        )
    else:
        for psname in postscript_names:
            if psname != font_metadata.post_script_name:
                passed = False
                yield FAIL, Message(
                    "mismatch",
                    (
                        f"Unmatched postscript name in font:"
                        f' TTF has "{psname}" while METADATA.pb has'
                        f' "{font_metadata.post_script_name}".'
                    ),
                )
    if passed:
        yield PASS, (
            f'Postscript name "{font_metadata.post_script_name}"'
            f" is identical in METADATA.pb and on the TTF file."
        )


@check(
    id="com.google.fonts/check/metadata/nameid/full_name",
    conditions=["font_metadata"],
    proposal="legacy:check/094",
)
def com_google_fonts_check_metadata_nameid_full_name(ttFont, font_metadata):
    """METADATA.pb font.full_name value matches
    fullname declared on the name table?
    """
    from fontbakery.utils import get_name_entry_strings

    full_fontnames = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME, langID=0x409)
    # FIXME: only check English names
    #        https://github.com/fonttools/fontbakery/issues/4000

    if len(full_fontnames) == 0:
        yield FAIL, Message(
            "lacks-entry",
            (
                f"This font lacks a FULL_FONT_NAME entry"
                f" (nameID = {NameID.FULL_FONT_NAME})"
                f" in the name table."
            ),
        )
    else:
        for full_fontname in full_fontnames:
            if full_fontname != font_metadata.full_name:
                yield FAIL, Message(
                    "mismatch",
                    (
                        f"Unmatched fullname in font:"
                        f' TTF has "{full_fontname}" while METADATA.pb'
                        f' has "{font_metadata.full_name}".'
                    ),
                )
            else:
                yield PASS, (
                    f'Font fullname "{full_fontname}" is identical'
                    f" in METADATA.pb and on the TTF file."
                )


@check(
    id="com.google.fonts/check/metadata/nameid/font_name",
    rationale="""
        This check ensures consistency between the font name declared on the name table
        and the contents of the METADATA.pb file.
    """,
    conditions=["font_metadata", "style"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/4086",
        "legacy:check/095",
    ],
)
def com_google_fonts_check_metadata_nameid_font_name(ttFont, style, font_metadata):
    """METADATA.pb font.name value should be same as
    the family name declared on the name table.
    """
    from fontbakery.utils import get_name_entry_strings

    font_familynames = get_name_entry_strings(
        ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME, langID=0x409
    )
    if len(font_familynames) == 0:
        # We'll only use nameid 1 (FONT_FAMILY_NAME) when the font
        # does not have nameid 16 (TYPOGRAPHIC_FAMILY_NAME).
        # https://github.com/fonttools/fontbakery/issues/4086
        font_familynames = get_name_entry_strings(
            ttFont, NameID.FONT_FAMILY_NAME, langID=0x409
        )

    nameid = NameID.FONT_FAMILY_NAME
    if len(font_familynames) == 0:
        yield FAIL, Message(
            "lacks-entry",
            f"This font lacks a {NameID(nameid).name} entry"
            f" (nameID = {nameid}) in the name table.",
        )
    else:
        for font_familyname in font_familynames:
            if font_familyname != font_metadata.name:
                yield FAIL, Message(
                    "mismatch",
                    f"Unmatched familyname in font:"
                    f' TTF has familyname = "{font_familyname}" while'
                    f' METADATA.pb has font.name = "{font_metadata.name}".',
                )
            else:
                yield PASS, (
                    f'OK: Family name "{font_metadata.name}" is identical'
                    f" in METADATA.pb and on the TTF file."
                )


@check(
    id="com.google.fonts/check/metadata/match_fullname_postscript",
    conditions=["font_metadata"],
    proposal="legacy:check/096",
)
def com_google_fonts_check_metadata_match_fullname_postscript(font_metadata):
    """METADATA.pb font.full_name and font.post_script_name
    fields have equivalent values ?
    """
    import re

    regex = re.compile(r"\W")
    post_script_name = regex.sub("", font_metadata.post_script_name)
    fullname = regex.sub("", font_metadata.full_name)
    if fullname != post_script_name:
        yield FAIL, Message(
            "mismatch",
            f'METADATA.pb font full_name = "{font_metadata.full_name}"'
            f" does not match"
            f' post_script_name = "{font_metadata.post_script_name}"',
        )
    else:
        yield PASS, (
            'METADATA.pb font fields "full_name" and'
            ' "post_script_name" have equivalent values.'
        )


@check(
    id="com.google.fonts/check/metadata/match_filename_postscript",
    conditions=["font_metadata", "not is_variable_font"],
    # FIXME: We'll want to review this once
    #        naming rules for varfonts are settled.
    proposal="legacy:check/097",
)
def com_google_fonts_check_metadata_match_filename_postscript(font_metadata):
    """METADATA.pb font.filename and font.post_script_name
    fields have equivalent values?
    """
    post_script_name = font_metadata.post_script_name
    filename = os.path.splitext(font_metadata.filename)[0]

    if filename != post_script_name:
        yield FAIL, Message(
            "mismatch",
            f'METADATA.pb font filename = "{font_metadata.filename}"'
            f" does not match"
            f' post_script_name="{font_metadata.post_script_name}".',
        )
    else:
        yield PASS, (
            'METADATA.pb font fields "filename" and'
            ' "post_script_name" have equivalent values.'
        )


@check(
    id="com.google.fonts/check/metadata/valid_name_values",
    conditions=["ttFont", "font_metadata"],
    proposal="legacy:check/098",
)
def com_google_fonts_check_metadata_valid_name_values(ttFont, font_metadata):
    """METADATA.pb font.name field matches font"""
    family_name = ttFont["name"].getBestFamilyName()
    if family_name != font_metadata.name:
        yield FAIL, Message(
            "mismatch",
            (
                f"METADATA.pb font.name field is {font_metadata.name} "
                f"but font has {family_name}"
            ),
        )
    else:
        yield PASS, "METADATA.pb font.name is correct"


@check(
    id="com.google.fonts/check/metadata/valid_full_name_values",
    conditions=["style", "font_metadata"],
    proposal="legacy:check/099",
)
def com_google_fonts_check_metadata_valid_full_name_values(font):
    """METADATA.pb font.full_name field contains font name in right format?"""
    if font.style in RIBBI_STYLE_NAMES:
        familynames = font.font_familynames
        if familynames == []:
            yield SKIP, "No FONT_FAMILYNAME"
    else:
        familynames = font.typographic_familynames
        if familynames == []:
            yield SKIP, "No TYPOGRAPHIC_FAMILYNAME"

    if any((name in font.font_metadata.full_name) for name in familynames):
        yield PASS, (
            "METADATA.pb font.full_name field contains font name in right format."
        )
    else:
        yield FAIL, Message(
            "mismatch",
            f"METADATA.pb font.full_name field"
            f' ("{font.font_metadata.full_name}")'
            f" does not match correct font name format"
            f' ("{", ".join(familynames)}").',
        )


@check(
    id="com.google.fonts/check/metadata/valid_filename_values",
    conditions=[
        "style",  # This means the font filename
        # (source of truth here) is good
        "family_metadata",
    ],
    proposal="legacy:check/100",
)
def com_google_fonts_check_metadata_valid_filename_values(font, family_metadata):
    """METADATA.pb font.filename field contains font name in right format?"""
    expected = os.path.basename(font.file)
    passed = False
    for font_metadata in family_metadata.fonts:
        if font_metadata.filename == expected:
            passed = True
            yield PASS, (
                "METADATA.pb filename field contains font name in right format."
            )
            break

    if not passed:
        yield FAIL, Message(
            "bad-field",
            f"None of the METADATA.pb filename fields match"
            f' correct font name format ("{expected}").',
        )


@check(
    id="com.google.fonts/check/metadata/valid_post_script_name_values",
    conditions=["font_metadata", "font_familynames"],
    proposal="legacy:check/101",
)
def com_google_fonts_check_metadata_valid_post_script_name_values(
    font_metadata, font_familynames
):
    """METADATA.pb font.post_script_name field
    contains font name in right format?
    """
    possible_psnames = [
        "".join(str(font_familyname).split()) for font_familyname in font_familynames
    ]
    metadata_psname = "".join(font_metadata.post_script_name.split("-"))
    if any(psname in metadata_psname for psname in possible_psnames):
        yield PASS, (
            "METADATA.pb postScriptName field contains font name in right format."
        )
    else:
        yield FAIL, Message(
            "mismatch",
            f"METADATA.pb"
            f' postScriptName ("{font_metadata.post_script_name}")'
            f" does not match"
            f' correct font name format ("{", ".join(possible_psnames)}").',
        )


@check(
    id="com.google.fonts/check/metadata/valid_nameid25",
    conditions=["style"],
    rationale="""
        Due to a bug in (at least) Adobe Indesign, name ID 25
        needs to be different for Italic VFs than their Upright counterparts.
        Google Fonts chooses to append "Italic" here.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3024",
        "https://github.com/googlefonts/gftools/issues/297",
        "https://typo.social/@arrowtype/110430680157544757",
    ],
)
def com_google_fonts_check_metadata_valid_nameid25(font, style):
    'Check name ID 25 to end with "Italic" for Italic VFs.'
    ttFont = font.ttFont

    def get_name(font, ID):
        for entry in font["name"].names:
            if entry.nameID == 25:
                return entry.toUnicode()
        return ""

    if not ("Italic" in style and font.is_variable_font):
        yield PASS, ("Not an Italic VF.")
    else:
        passed = True
        if not get_name(ttFont, 25).endswith("Italic"):
            passed = False
            yield FAIL, Message(
                "nameid25-missing-italic",
                'Name ID 25 must end with "Italic" for Italic fonts.',
            )
        if " " in get_name(ttFont, 25):
            passed = False
            yield FAIL, Message(
                "nameid25-has-spaces", "Name ID 25 must not contain spaces."
            )

        if passed:
            yield PASS, ("Name ID 25 looks good.")


@check(
    id="com.google.fonts/check/metadata/filenames",
    rationale="""
        Note:
        This check only looks for files in the current directory.

        Font files in subdirectories are checked by these other two checks:
         - com.google.fonts/check/metadata/undeclared_fonts
         - com.google.fonts/check/repo/vf_has_static_fonts

        We may want to merge them all into a single check.
    """,
    conditions=["family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/2597",
)
def com_google_fonts_check_metadata_filenames(fonts, family_directory, family_metadata):
    """METADATA.pb: Font filenames match font.filename entries?"""

    passed = True
    metadata_filenames = []
    font_filenames = [
        f for f in os.listdir(family_directory) if f[-4:] in [".ttf", ".otf"]
    ]
    for font_metadata in family_metadata.fonts:
        if font_metadata.filename not in font_filenames:
            passed = False
            yield FAIL, Message(
                "file-not-found",
                f'Filename "{font_metadata.filename}" is listed on'
                f" METADATA.pb but an actual font file"
                f" with that name was not found.",
            )
        metadata_filenames.append(font_metadata.filename)

    for font in font_filenames:
        if font not in metadata_filenames:
            passed = False
            yield FAIL, Message(
                "file-not-declared",
                f'Filename "{font}" is not declared'
                f" on METADATA.pb as a font.filename entry.",
            )
    if passed:
        yield PASS, "Filenames in METADATA.pb look good."


@check(
    id="com.google.fonts/check/metadata/italic_style",
    conditions=["font_metadata"],
    proposal="legacy:check/106",
)
def com_google_fonts_check_metadata_italic_style(ttFont, font_metadata):
    """METADATA.pb font.style "italic" matches font internals?"""
    from fontbakery.utils import get_name_entry_strings
    from fontbakery.constants import MacStyle

    if font_metadata.style != "italic":
        yield SKIP, "This check only applies to italic fonts."
    else:
        font_fullname = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)
        if len(font_fullname) == 0:
            yield SKIP, "Font lacks fullname entries in name table."
            # this fail scenario was already checked above
            # (passing those previous checks is a prerequisite for this one)
            # FIXME: Could we pack this into a condition ?
        else:
            # FIXME: here we only check the first name entry.
            #        Should we iterate over them all ? Or should we check
            #        if they're all the same?
            font_fullname = font_fullname[0]

            if not bool(ttFont["head"].macStyle & MacStyle.ITALIC):
                yield FAIL, Message(
                    "bad-macstyle",
                    (
                        "METADATA.pb style has been set to italic"
                        " but font macStyle is improperly set."
                    ),
                )
            elif not font_fullname.split("-")[-1].endswith("Italic"):
                yield FAIL, Message(
                    "bad-fullfont-name",
                    (
                        f"Font macStyle Italic bit is set"
                        f" but nameID {NameID.FULL_FONT_NAME}"
                        f' ("{font_fullname}") is not'
                        f' ended with "Italic".'
                    ),
                )
            else:
                yield PASS, (
                    'OK: METADATA.pb font.style "italic" matches font internals.'
                )


@check(
    id="com.google.fonts/check/metadata/normal_style",
    conditions=["font_metadata"],
    proposal="legacy:check/107",
)
def com_google_fonts_check_metadata_normal_style(ttFont, font_metadata):
    """METADATA.pb font.style "normal" matches font internals?"""
    from fontbakery.utils import get_name_entry_strings
    from fontbakery.constants import MacStyle

    if font_metadata.style != "normal":
        yield SKIP, "This check only applies to normal fonts."
        # FIXME: declare a common condition called "normal_style"
    else:
        font_familyname = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
        font_fullname = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)
        if len(font_familyname) == 0 or len(font_fullname) == 0:
            # FIXME: This is the same SKIP condition as in check/metadata/italic_style
            #        so we definitely need to address them with a common condition!
            yield SKIP, "Font lacks familyname and/or fullname entries in name table."
        else:
            font_familyname = font_familyname[0]
            font_fullname = font_fullname[0]

            if bool(ttFont["head"].macStyle & MacStyle.ITALIC):
                yield FAIL, Message(
                    "bad-macstyle",
                    (
                        "METADATA.pb style has been set to normal"
                        " but font macStyle is improperly set."
                    ),
                )
            elif font_familyname.split("-")[-1].endswith("Italic"):
                yield FAIL, Message(
                    "familyname-italic",
                    (
                        "Font macStyle indicates a non-Italic font,"
                        f" but nameID {NameID.FONT_FAMILY_NAME}"
                        f' (FONT_FAMILY_NAME: "{font_familyname}")'
                        ' ends with "Italic".'
                    ),
                )
            elif font_fullname.split("-")[-1].endswith("Italic"):
                yield FAIL, Message(
                    "fullfont-italic",
                    (
                        "Font macStyle indicates a non-Italic font,"
                        f" but nameID {NameID.FULL_FONT_NAME}"
                        f' (FULL_FONT_NAME: "{font_fullname}")'
                        ' ends with "Italic".'
                    ),
                )
            else:
                yield PASS, 'METADATA.pb font.style "normal" matches font internals.'


@check(
    id="com.google.fonts/check/metadata/unique_full_name_values",
    conditions=["family_metadata"],
    proposal="legacy:check/083",
)
def com_google_fonts_check_metadata_unique_full_name_values(family_metadata):
    """METADATA.pb: check if fonts field only has
    unique "full_name" values.
    """
    fonts = {}
    for f in family_metadata.fonts:
        fonts[f.full_name] = f

    if len(set(fonts.keys())) != len(family_metadata.fonts):
        yield FAIL, Message(
            "duplicated",
            'Found duplicated "full_name" values in METADATA.pb fonts field.',
        )
    else:
        yield PASS, 'METADATA.pb "fonts" field only has unique "full_name" values.'


@check(
    id="com.google.fonts/check/metadata/unique_weight_style_pairs",
    conditions=["family_metadata"],
    proposal="legacy:check/084",
)
def com_google_fonts_check_metadata_unique_weight_style_pairs(family_metadata):
    """METADATA.pb: check if fonts field
    only contains unique style:weight pairs.
    """
    pairs = {}
    for f in family_metadata.fonts:
        styleweight = f"{f.style}:{f.weight}"
        pairs[styleweight] = 1
    if len(set(pairs.keys())) != len(family_metadata.fonts):
        yield FAIL, Message(
            "duplicated",
            "Found duplicated style:weight pair in METADATA.pb fonts field.",
        )
    else:
        yield PASS, 'METADATA.pb "fonts" field only has unique style:weight pairs.'


@check(
    id="com.google.fonts/check/metadata/reserved_font_name",
    conditions=["font_metadata", "not rfn_exception"],
    proposal="legacy:check/103",
)
def com_google_fonts_check_metadata_reserved_font_name(font_metadata):
    """Copyright notice on METADATA.pb should not contain 'Reserved Font Name'."""
    if "Reserved Font Name" in font_metadata.copyright:
        yield WARN, Message(
            "rfn",
            f"METADATA.pb:"
            f' copyright field ("{font_metadata.copyright}")'
            f' contains "Reserved Font Name".'
            f" This is an error except in a few specific rare cases.",
        )
    else:
        yield PASS, (
            'METADATA.pb copyright field does not contain "Reserved Font Name".'
        )


@check(
    id="com.google.fonts/check/metadata/nameid/family_and_full_names",
    conditions=["font_metadata"],
    proposal="legacy:check/108",
)
def com_google_fonts_check_metadata_nameid_family_and_full_names(ttFont, font_metadata):
    """METADATA.pb font.name and font.full_name fields match
    the values declared on the name table?
    """
    from fontbakery.utils import get_name_entry_strings

    font_familynames = get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)
    if font_familynames:
        font_familyname = font_familynames[0]
    else:
        font_familyname = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)[0]
    font_fullname = get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME)[0]
    # FIXME: common condition/name-id check as in the two previous checks.

    if font_fullname != font_metadata.full_name:
        yield FAIL, Message(
            "fullname-mismatch",
            (
                f'METADATA.pb: Fullname "{font_metadata.full_name}"'
                f' does not match name table entry "{font_fullname}"!'
            ),
        )

    elif font_familyname != font_metadata.name:
        yield FAIL, Message(
            "familyname-mismatch",
            (
                f'METADATA.pb Family name "{font_metadata.name}"'
                f' does not match name table entry "{font_familyname}"!'
            ),
        )
    else:
        yield PASS, (
            "METADATA.pb familyname and fullName fields"
            " match corresponding name table entries."
        )


@check(
    id="com.google.fonts/check/metadata/match_name_familyname",
    conditions=[
        "family_metadata",  # that's the family-wide metadata!
        "font_metadata",
    ],  # and this one's specific to a single file
    proposal="legacy:check/110",
)
def com_google_fonts_check_metadata_match_name_familyname(
    family_metadata, font_metadata
):
    """METADATA.pb: Check font name is the same as family name."""
    if font_metadata.name != family_metadata.name:
        yield FAIL, Message(
            "mismatch",
            f"METADATA.pb: {font_metadata.filename}:\n"
            f' Family name "{family_metadata.name}" does not match'
            f' font name: "{font_metadata.name}"',
        )
    else:
        yield PASS, "Font name is the same as family name."


@check(
    id="com.google.fonts/check/metadata/canonical_weight_value",
    conditions=["font_metadata"],
    proposal="legacy:check/111",
)
def com_google_fonts_check_metadata_canonical_weight_value(font_metadata):
    """METADATA.pb: Check that font weight has a canonical value."""
    first_digit = font_metadata.weight / 100
    if (font_metadata.weight % 100) != 0 or (first_digit < 1 or first_digit > 9):
        yield FAIL, Message(
            "bad-weight",
            f"METADATA.pb: The weight is declared"
            f" as {font_metadata.weight} which is not a"
            f" multiple of 100 between 100 and 900.",
        )
    else:
        yield PASS, "Font weight has a canonical value."


@check(
    id="com.google.fonts/check/metadata/os2_weightclass",
    rationale="""
        Check METADATA.pb font weights are correct.

        For static fonts, the metadata weight should be the same as the static font's
        OS/2 usWeightClass.

        For variable fonts, the weight value should be 400 if the font's wght axis range
        includes 400, otherwise it should be the value closest to 400.
    """,
    conditions=["font_metadata"],
    proposal=[
        "legacy:check/112",
        "https://github.com/fonttools/fontbakery/issues/2683",
    ],
)
def com_google_fonts_check_metadata_os2_weightclass(font, font_metadata):
    """Check METADATA.pb font weights are correct."""
    # Weight name to value mapping:
    GF_API_WEIGHT_NAMES = {
        100: "Thin",
        200: "ExtraLight",
        250: "Thin",  # Legacy. Pre-vf epoch
        275: "ExtraLight",  # Legacy. Pre-vf epoch
        300: "Light",
        400: "Regular",
        500: "Medium",
        600: "SemiBold",
        700: "Bold",
        800: "ExtraBold",
        900: "Black",
    }
    CSS_WEIGHT_NAMES = {
        100: "Thin",
        200: "ExtraLight",
        300: "Light",
        400: "Regular",
        500: "Medium",
        600: "SemiBold",
        700: "Bold",
        800: "ExtraBold",
        900: "Black",
    }
    ttFont = font.ttFont
    if font.is_variable_font:
        axes = {f.axisTag: f for f in ttFont["fvar"].axes}
        if "wght" not in axes:
            # if there isn't a wght axis, use the OS/2.usWeightClass
            font_weight = ttFont["OS/2"].usWeightClass
            should_be = "the same"
        else:
            # if the wght range includes 400, use 400
            wght_includes_400 = (
                axes["wght"].minValue <= 400 and axes["wght"].maxValue >= 400
            )
            if wght_includes_400:
                font_weight = 400
                should_be = (
                    "400 because it is a varfont which includes"
                    " this coordinate in its 'wght' axis"
                )
            else:
                # if 400 isn't in the wght axis range, use the value closest to 400
                if abs(axes["wght"].minValue - 400) < abs(axes["wght"].maxValue - 400):
                    font_weight = axes["wght"].minValue
                else:
                    font_weight = axes["wght"].maxValue
                should_be = (
                    f"{font_weight} because it is the closest value to 400"
                    f" on the 'wght' axis of this variable font"
                )
    else:
        font_weight = ttFont["OS/2"].usWeightClass
        if font_weight not in [250, 275]:
            should_be = "the same"
        else:
            if font_weight == 250:
                expected_value = 100  # "Thin"
            if font_weight == 275:
                expected_value = 200  # "ExtraLight"
            should_be = (
                f"{expected_value}, corresponding to"
                f' CSS weight name "{CSS_WEIGHT_NAMES[expected_value]}"'
            )

    gf_weight_name = GF_API_WEIGHT_NAMES.get(font_weight, "bad value")
    css_weight_name = CSS_WEIGHT_NAMES.get(font_metadata.weight)

    if gf_weight_name != css_weight_name:
        yield FAIL, Message(
            "mismatch",
            f'OS/2 table has usWeightClass={ttFont["OS/2"].usWeightClass},'
            f' meaning "{gf_weight_name}" on the Google Fonts API.\n\n'
            f"On METADATA.pb it should be {should_be},"
            f" but instead got {font_metadata.weight}.\n",
        )
    else:
        yield PASS, (
            "OS/2 usWeightClass or wght axis value matches"
            " weight specified at METADATA.pb"
        )


@check(
    id="com.google.fonts/check/metadata/match_weight_postscript",
    conditions=["font_metadata", "not is_variable_font"],
    proposal="legacy:check/113",
)
def com_google_fonts_check_metadata_match_weight_postscript(font_metadata):
    """METADATA.pb weight matches postScriptName for static fonts."""
    WEIGHTS = {
        "Thin": 100,
        "ThinItalic": 100,
        "ExtraLight": 200,
        "ExtraLightItalic": 200,
        "Light": 300,
        "LightItalic": 300,
        "Regular": 400,
        "Italic": 400,
        "Medium": 500,
        "MediumItalic": 500,
        "SemiBold": 600,
        "SemiBoldItalic": 600,
        "Bold": 700,
        "BoldItalic": 700,
        "ExtraBold": 800,
        "ExtraBoldItalic": 800,
        "Black": 900,
        "BlackItalic": 900,
    }
    pair = []
    for k, weight in WEIGHTS.items():
        if weight == font_metadata.weight:
            pair.append((k, weight))

    if not pair:
        yield FAIL, ("METADATA.pb: Font weight value ({}) is invalid.").format(
            font_metadata.weight
        )
    elif not (
        font_metadata.post_script_name.endswith("-" + pair[0][0])
        or font_metadata.post_script_name.endswith("-" + pair[1][0])
    ):
        yield FAIL, (
            'METADATA.pb: Mismatch between postScriptName ("{}")'
            " and weight value ({}). The name must be"
            ' ended with "{}" or "{}".'
            ""
        ).format(font_metadata.post_script_name, pair[0][1], pair[0][0], pair[1][0])
    else:
        yield PASS, "Weight value matches postScriptName."


@check(
    id="com.google.fonts/check/metadata/canonical_style_names",
    conditions=["font_metadata"],
    proposal="legacy:check/115",
)
def com_google_fonts_check_metadata_canonical_style_names(font, font_metadata):
    """METADATA.pb: Font styles are named canonically?"""
    if font_metadata.style not in ["italic", "normal"]:
        yield SKIP, (
            "This check only applies to font styles declared"
            ' as "italic" or "normal" on METADATA.pb.'
        )
    else:
        if font.is_italic and font_metadata.style != "italic":
            yield FAIL, Message(
                "italic",
                f'The font style is "{font_metadata.style}"'
                f' but it should be "italic".',
            )
        elif not font.is_italic and font_metadata.style != "normal":
            yield FAIL, Message(
                "normal",
                f'The font style is "{font_metadata.style}"'
                f' but it should be "normal".',
            )
        else:
            yield PASS, "Font styles are named canonically."


@check(
    id="com.google.fonts/check/metadata/consistent_repo_urls",
    conditions=["family_metadata"],
    rationale="""
        Sometimes, perhaps due to copy-pasting, projects may declare different URLs
        between the font.coyright and the family.sources.repository_url fields.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4056",
)
def com_google_fonts_check_metadata_consistent_repo_urls(
    config, family_metadata, license_contents, is_ofl, description
):
    """
    METADATA.pb: Check URL on copyright string is the same as in repository_url field.
    """
    repo_url = family_metadata.source.repository_url
    if not repo_url:
        yield FAIL, Message(
            "lacks-repo-url", "Please add a family.source.repository_url entry."
        )
        return

    import re

    A_GITHUB_URL = r"github.com/[\w-]+/[\w-]+"

    def clean_url(url):
        if ")" in url:
            url = url.split(")")[0].strip()
        if url.endswith("/"):
            url = url[:-1]
        if url.endswith(".git"):
            url = url[:-4]
        return url

    bad_urls = []
    repo_url = clean_url(family_metadata.source.repository_url)
    a_url = repo_url

    for font_md in family_metadata.fonts:
        if "http" in font_md.copyright:
            link = clean_url("http" + font_md.copyright.split("http")[1])
            if not a_url:
                a_url = link
            elif link != repo_url:
                bad_urls.append(("font copyright string", link))

    if is_ofl and license_contents:
        string = license_contents.strip().split("\n")[0]
        if "http" in string:
            link = clean_url("http" + string.split("http")[1])
            if not a_url:
                a_url = link
            elif clean_url(link) != a_url:
                bad_urls.append(("OFL text", link))

    if a_url and description:
        headless = re.sub(r"^https?://", "", a_url)
        for match in set(re.findall(A_GITHUB_URL, description)):
            if clean_url(match) != headless:
                bad_urls.append(("HTML description", match))

    if bad_urls:
        from fontbakery.utils import pretty_print_list

        bad_urls = pretty_print_list(
            config, [f"{location} has '{url}'" for location, url in bad_urls]
        )
        yield FAIL, Message(
            "mismatch",
            f"Repository URL is {a_url}\n\nBut: {bad_urls}\n",
        )
    else:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/metadata/primary_script",
    conditions=["family_metadata"],
    rationale="""
        Try to guess font's primary script and see if that's set in METADATA.pb.
        This is an educated guess based on the number of glyphs per script in the font
        and should be taken with caution.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4109",
)
def com_google_fonts_check_metadata_primary_script(ttFont, family_metadata):
    """METADATA.pb: Check for primary_script"""
    passed = True

    def get_primary_script(ttFont):
        from fontTools import unicodedata
        from collections import Counter

        script_count = Counter()
        for c in ttFont.getBestCmap().keys():
            for script in unicodedata.script_extension(chr(c)):
                if script not in ["Zinh", "Zyyy", "Zzzz"]:
                    # Zinh: "Inherited"
                    # Zyyy: "Common"
                    # Zzzz: "Unknown"
                    script_count[script] += 1
        most_common = script_count.most_common(1)
        if most_common:
            script = most_common[0][0]
            return script

    siblings = (
        ("Kore", "Hang"),
        ("Jpan", "Hani", "Hant", "Hans"),
        ("Hira", "Kana"),
    )

    def is_sibling_script(target, guessed):
        for family in siblings:
            if guessed in family and target in family:
                return True

    def get_sibling_scripts(target):
        for family in siblings:
            if target in family:
                return family

    guessed_primary_script = get_primary_script(ttFont)
    if guessed_primary_script != "Latn":
        # family_metadata.primary_script is empty but should be set
        if family_metadata.primary_script in (None, ""):
            passed = False
            message = (
                f"METADATA.pb: primary_script field"
                f" should be '{guessed_primary_script}' but is missing."
            )
            sibling_scripts = get_sibling_scripts(guessed_primary_script)
            if sibling_scripts:
                sibling_scripts = ", ".join(sibling_scripts)
                message += (
                    f"\nMake sure that '{guessed_primary_script}' is"
                    f" actually the correct one (out of {sibling_scripts})."
                )
            yield WARN, Message("missing-primary-script", message)

        # family_metadata.primary_script is set
        # but it's not the same as guessed_primary_script
        if (
            family_metadata.primary_script not in (None, "")
            and family_metadata.primary_script != guessed_primary_script
            and is_sibling_script(
                family_metadata.primary_script, guessed_primary_script
            )
            is None
        ):
            passed = False
            yield WARN, Message(
                "wrong-primary-script",
                (
                    f"METADATA.pb: primary_script is '{family_metadata.primary_script}'"
                    f"\nIt should instead be '{guessed_primary_script}'."
                ),
            )

    if passed:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/metadata/empty_designer",
    rationale="""
        Any font published on Google Fonts must credit one or several authors,
        foundry and/or individuals.

        Ideally, all authors listed in the upstream repository's AUTHORS.txt should
        be mentioned in the designer field.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3961",
)
def com_google_fonts_check_metadata_empty_designer(family_metadata):
    """At least one designer is declared in METADATA.pb"""

    if family_metadata.designer.strip() == "":
        yield FAIL, Message("empty-designer", "Font designer field is empty.")

    # TODO: Parse AUTHORS.txt and WARN if names do not match
    # (and then maybe rename the check-id)
    else:
        yield PASS, "Font designer field is not empty."


@check(
    id="com.google.fonts/check/metadata/has_tags",
    conditions=["network"],
    rationale="""
        Any font published on Google Fonts must be listed in the tags spreadsheet.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4465",
)
def com_google_fonts_check_metadata_has_tags(family_metadata):
    """The font has tags in the GF Tags spreadsheet"""
    from fontbakery.checks.googlefonts.conditions import gf_tags

    tags = gf_tags()
    tagged_families = set(row[0] for row in tags[6:])
    if family_metadata.name not in tagged_families:
        yield FATAL, Message("no-tags", "Family does not appear in tag spreadsheet.")
    else:
        yield PASS, "Family has tags"


@check(
    id="com.google.fonts/check/metadata/escaped_strings",
    rationale="""
        In some cases we've seen designer names and other fields with escaped strings
        in METADATA files (such as "Juli\\303\\241n").

        Nowadays the strings can be full unicode strings (such as "Julián") and do
        not need escaping.

        Escaping quotes or double-quotes is fine, though.
    """,
    conditions=["metadata_file"],
    proposal="https://github.com/fonttools/fontbakery/issues/2932",
)
def com_google_fonts_check_metadata_escaped_strings(metadata_file):
    """Ensure METADATA.pb does not use escaped strings."""
    passed = True
    for line in open(metadata_file, "r", encoding="utf-8").readlines():
        # Escaped quotes are fine!
        # What we're really interested in detecting things like
        # "Juli\303\241n" instead of "Julián"
        line = line.replace("\\'", "")
        line = line.replace('\\"', "")

        for quote_char in ["'", '"']:
            segments = line.split(quote_char)
            if len(segments) >= 3:
                a_string = segments[1]
                if "\\" in a_string:
                    passed = False
                    yield FAIL, Message(
                        "escaped-strings",
                        f"Found escaped chars at '{a_string}'."
                        f" Please use an unicode string instead.",
                    )
    if passed:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/metadata/designer_profiles",
    rationale="""
        Google Fonts has a catalog of designers.

        This check ensures that the online entries of the catalog can be found based
        on the designer names listed on the METADATA.pb file.

        It also validates the URLs and file formats are all correctly set.
    """,
    conditions=["network", "family_metadata", "not is_noto"],
    proposal="https://github.com/fonttools/fontbakery/issues/3083",
)
def com_google_fonts_check_metadata_designer_profiles(family_metadata, config):
    """METADATA.pb: Designers are listed correctly on the Google Fonts catalog?"""
    DESIGNER_INFO_RAW_URL = (
        "https://raw.githubusercontent.com/google/fonts/master/catalog/designers/{}/"
    )
    from fontbakery.utils import get_DesignerInfoProto_Message
    import requests

    # NOTE: See issue #3316
    TRANSLATE = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "à": "a",
        "è": "e",
        "ì": "i",
        "ò": "o",
        "ù": "u",
        "ń": "n",
        "ø": "o",
        "ř": "r",
        "ś": "s",
        "ß": "ss",
        "ł": "l",
        "ã": "a",
        "ı": "i",
        "ü": "ue",
    }

    def normalize(name):
        """Restrict the designer name to lowercase a-z and numbers"""
        import string

        normalized_name = ""
        for c in name.lower():
            if c in string.ascii_letters or c in "0123456789":
                normalized_name += c
            elif c in TRANSLATE.keys():
                normalized_name += TRANSLATE[c]
        return normalized_name

    passed = True
    for designer in family_metadata.designer.split(","):
        designer = designer.strip()
        normalized_name = normalize(designer)
        if normalized_name == "multipledesigners":
            yield FAIL, Message(
                "multiple-designers",
                f"Font family {family_metadata.name} does not explicitely"
                f" mention the names of its designers on its METADATA.pb file.",
            )
            continue

        url = DESIGNER_INFO_RAW_URL.format(normalized_name) + "info.pb"
        response = requests.get(url, timeout=config.get("timeout"))

        # https://github.com/fonttools/fontbakery/pull/3892#issuecomment-1248758859
        # For debugging purposes:
        # yield WARN,\
        #      Message("config",
        #              f"Config is '{config}'")

        if response.status_code != requests.codes.OK:
            passed = False
            yield WARN, Message(
                "profile-not-found",
                f"It seems that {designer} is still not listed on"
                f" the designers catalog. Please submit a photo and"
                f" a link to a webpage where people can learn more"
                f" about the work of this designer/typefoundry.",
            )
            continue

        info = get_DesignerInfoProto_Message(response.content)
        if info.designer != designer.strip():
            passed = False
            yield FAIL, Message(
                "mismatch",
                f"Designer name at METADATA.pb ({designer})"
                f" is not the same as listed on the designers"
                f" catalog ({info.designer}) available at {url}",
            )

        if info.link != "":
            passed = False
            yield FAIL, Message(
                "link-field",
                "Currently the link field is not used by the GFonts API."
                " Designer webpage links should, for now, be placed"
                " directly on the bio.html file.",
            )

        if not info.avatar.file_name and designer != "Google":
            passed = False
            yield FAIL, Message(
                "missing-avatar",
                f"Designer {designer} still does not have an avatar image. "
                f"Please provide one.",
            )
        else:
            avatar_url = (
                DESIGNER_INFO_RAW_URL.format(normalized_name) + info.avatar.file_name
            )
            response = requests.get(avatar_url, timeout=config.get("timeout"))
            if response.status_code != requests.codes.OK:
                passed = False
                yield FAIL, Message(
                    "bad-avatar-filename",
                    "The avatar filename provided seems to be incorrect:"
                    f" ({avatar_url})",
                )

    if passed:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/metadata/consistent_axis_enumeration",
    rationale="""
        All font variation axes present in the font files must be properly declared
        on METADATA.pb so that they can be served by the GFonts API.
    """,
    conditions=["is_variable_font", "family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3051",
)
def com_google_fonts_check_metadata_consistent_axis_enumeration(
    family_metadata, ttFont, config
):
    """Validate VF axes match the ones declared on METADATA.pb."""
    from fontbakery.utils import pretty_print_list

    passed = True
    md_axes = set(axis.tag for axis in family_metadata.axes)
    fvar_axes = set(axis.axisTag for axis in ttFont["fvar"].axes)
    missing = sorted(fvar_axes - md_axes)
    extra = sorted(md_axes - fvar_axes)

    if missing:
        passed = False
        yield FAIL, Message(
            "missing-axes",
            f"The font variation axes {pretty_print_list(config, missing)}"
            f" are present in the font's fvar table but are not"
            f" declared on the METADATA.pb file.",
        )
    if extra:
        passed = False
        yield FAIL, Message(
            "extra-axes",
            f"The METADATA.pb file lists font variation axes that"
            f" are not supported but this family: {pretty_print_list(config, extra)}",
        )
    if passed:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/metadata/family_directory_name",
    rationale="""
        We want the directory name of a font family to be predictable and directly
        derived from the family name, all lowercased and removing spaces.
    """,
    conditions=["family_metadata", "family_directory"],
    proposal="https://github.com/fonttools/fontbakery/issues/3421",
)
def com_google_fonts_check_metadata_family_directory_name(
    family_metadata, family_directory
):
    """Check font family directory name."""

    dir_name = os.path.basename(family_directory)
    expected = family_metadata.name.replace(" ", "").lower()
    if expected != dir_name:
        yield FAIL, Message(
            "bad-directory-name",
            f'Family name on METADATA.pb is "{family_metadata.name}"\n'
            f'Directory name is "{dir_name}"\n'
            f'Expected "{expected}"',
        )
    else:
        yield PASS, f'Directory name is "{dir_name}", as expected.'


@check(
    id="com.google.fonts/check/metadata/can_render_samples",
    rationale="""
        In order to prevent tofu from being seen on fonts.google.com, this check
        verifies that all samples specified by METADATA.pb can be properly
        rendered by the font.
    """,
    conditions=["family_metadata"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3419",
        "https://github.com/fonttools/fontbakery/issues/3605",
    ],
)
def com_google_fonts_check_metadata_can_render_samples(ttFont, family_metadata):
    """Check samples can be rendered."""
    try:
        from gflanguages import LoadLanguages
    except ImportError:
        exit_with_install_instructions()

    passed = True
    languages = LoadLanguages()
    for lang in family_metadata.languages:
        if lang not in languages:
            yield WARN, Message(
                "no-sample-string",
                f"Aparently there's no sample strings for"
                f" '{lang}' in the gflanguages package.",
            )
            passed = False
            continue

        # Note: checking agains all samples often results in
        #       a way too verbose output. That's why I only left
        #       the "tester" string for now.
        SAMPLES = {
            # 'styles': languages[lang].sample_text.styles,
            "tester": languages[lang].sample_text.tester,
            # 'specimen_16': languages[lang].sample_text.specimen_16,
            # 'specimen_21': languages[lang].sample_text.specimen_21,
            # 'specimen_32': languages[lang].sample_text.specimen_32,
            # 'specimen_36': languages[lang].sample_text.specimen_36,
            # 'specimen_48': languages[lang].sample_text.specimen_48
        }
        for sample_type, sample_text in SAMPLES.items():
            # Remove line-breaks and zero width space (U+200B) characteres.
            # For more info, see https://github.com/fonttools/fontbakery/issues/3990
            sample_text = sample_text.replace("\n", "").replace("\u200b", "")

            if not can_shape(ttFont, sample_text):
                passed = False
                yield FAIL, Message(
                    "sample-text",
                    f'Font can\'t render "{lang}" sample text:\n' f'"{sample_text}"\n',
                )

    if passed:
        yield PASS, "OK."


@check(
    id="com.google.fonts/check/metadata/category_hints",
    rationale="""
        Sometimes the font familyname contains words that hint at which is the most
        likely correct category to be declared on METADATA.pb
    """,
    conditions=["family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3624",
)
def com_google_fonts_check_metadata_category_hint(family_metadata):
    """
    Check if category on METADATA.pb matches what can be inferred from the family name.
    """

    HINTS = {
        "SANS_SERIF": ["Sans", "Grotesk", "Grotesque"],
        "SERIF": ["Old Style", "Transitional", "Garamond", "Serif", "Slab"],
        "DISPLAY": ["Display"],
        "HANDWRITING": ["Hand", "Script"],
    }

    inferred_category = None
    for category, hints in HINTS.items():
        for hint in hints:
            if hint in family_metadata.name:
                inferred_category = category
                break

    if (
        inferred_category is not None
        and inferred_category not in family_metadata.category
    ):
        yield WARN, Message(
            "inferred-category",
            f'Familyname seems to hint at "{inferred_category}" but'
            f' METADATA.pb declares it as "{family_metadata.category}".',
        )
    else:
        yield PASS, "OK."
