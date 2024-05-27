import re

from fontbakery.prelude import FAIL, PASS, SKIP, WARN, Message, check
from fontbakery.utils import get_glyph_name, pretty_print_list


@check(
    id="com.google.fonts/check/valid_glyphnames",
    rationale="""
        Microsoft's recommendations for OpenType Fonts states the following:

        'NOTE: The PostScript glyph name must be no longer than 31 characters,
        include only uppercase or lowercase English letters, European digits,
        the period or the underscore, i.e. from the set `[A-Za-z0-9_.]` and
        should start with a letter, except the special glyph name `.notdef`
        which starts with a period.'

        https://learn.microsoft.com/en-us/typography/opentype/otspec181/recom#-post--table


        In practice, though, particularly in modern environments, glyph names
        can be as long as 63 characters.

        According to the "Adobe Glyph List Specification" available at:

        https://github.com/adobe-type-tools/agl-specification
    """,
    proposal=[
        "legacy:check/058",
        # issue #2832 increased the limit to 63 chars
        "https://github.com/fonttools/fontbakery/issues/2832",
    ],
)
def com_google_fonts_check_valid_glyphnames(ttFont, config):
    """Glyph names are all valid?"""
    if (
        ttFont.sfntVersion == "\x00\x01\x00\x00"
        and ttFont.get("post")
        and ttFont["post"].formatType == 3
    ):
        yield SKIP, (
            "TrueType fonts with a format 3 post table contain no glyph names."
        )
    elif (
        ttFont.sfntVersion == "OTTO"
        and ttFont.get("CFF2")
        and ttFont.get("post")
        and ttFont["post"].formatType == 3
    ):
        yield SKIP, (
            "OpenType-CFF2 fonts with a format 3 post table contain no glyph names."
        )
    else:
        bad_names = set()
        warn_names = set()
        for glyphName in ttFont.getGlyphOrder():
            # The first two names are explicit exceptions in the glyph naming rules.
            # The third was added in https://github.com/fonttools/fontbakery/pull/2003
            if glyphName.startswith((".null", ".notdef", ".ttfautohint")):
                continue
            if not re.match(r"^(?![.0-9])[a-zA-Z._0-9]{1,63}$", glyphName):
                bad_names.add(glyphName)
            if len(glyphName) > 31 and len(glyphName) <= 63:
                warn_names.add(glyphName)

        if not bad_names:
            if not warn_names:
                yield PASS, "Glyph names are all valid."
            else:
                yield WARN, Message(
                    "legacy-long-names",
                    "The following glyph names may be too long for some legacy systems"
                    " which may expect a maximum 31-characters length limit:\n"
                    f"{pretty_print_list(config, sorted(warn_names))}",
                )
        else:
            bad_names_list = pretty_print_list(config, sorted(bad_names))
            yield FAIL, Message(
                "found-invalid-names",
                "The following glyph names do not comply"
                f" with naming conventions: {bad_names_list}\n\n"
                " A glyph name must be entirely comprised of characters"
                " from the following set: A-Z a-z 0-9 .(period) _(underscore)."
                " A glyph name must not start with a digit or period."
                ' There are a few exceptions such as the special glyph ".notdef".'
                ' The glyph names "twocents", "a1", and "_" are all valid,'
                ' while "2cents" and ".twocents" are not.',
            )


@check(
    id="com.google.fonts/check/unique_glyphnames",
    rationale="""
        Duplicate glyph names prevent font installation on Mac OS X.
    """,
    proposal="legacy:check/059",
    misc_metadata={"affects": [("Mac", "unspecified")]},
)
def com_google_fonts_check_unique_glyphnames(ttFont):
    """Font contains unique glyph names?"""
    if (
        ttFont.sfntVersion == "\x00\x01\x00\x00"
        and ttFont.get("post")
        and ttFont["post"].formatType == 3
    ):
        yield SKIP, (
            "TrueType fonts with a format 3 post table contain no glyph names."
        )
    elif (
        ttFont.sfntVersion == "OTTO"
        and ttFont.get("CFF2")
        and ttFont.get("post")
        and ttFont["post"].formatType == 3
    ):
        yield SKIP, (
            "OpenType-CFF2 fonts with a format 3 post table contain no glyph names."
        )
    else:
        glyph_names = set()
        dup_glyph_names = set()
        for gname in ttFont.getGlyphOrder():
            # On font load, Fonttools adds #1, #2, ... suffixes to duplicate glyph names
            glyph_name = re.sub(r"#\w+", "", gname)
            if glyph_name in glyph_names:
                dup_glyph_names.add(glyph_name)
            else:
                glyph_names.add(glyph_name)

        if not dup_glyph_names:
            yield PASS, "Glyph names are all unique."
        else:
            yield FAIL, Message(
                "duplicated-glyph-names",
                f"These glyph names occur more than once: {sorted(dup_glyph_names)}",
            )


@check(
    id="com.google.fonts/check/whitespace_glyphnames",
    conditions=["not missing_whitespace_chars"],
    rationale="""
        This check enforces adherence to recommended whitespace
        (codepoints 0020 and 00A0) glyph names according to the Adobe Glyph List.
    """,
    proposal="legacy:check/048",
)
def com_google_fonts_check_whitespace_glyphnames(ttFont):
    """Font has **proper** whitespace glyph names?"""
    # AGL recommended names, according to Adobe Glyph List for new fonts:
    AGL_RECOMMENDED_0020 = {"space"}
    AGL_RECOMMENDED_00A0 = {"uni00A0", "space"}
    # "space" is in this set because some fonts use the same glyph for
    # U+0020 and U+00A0. Including it here also removes a warning
    # when U+0020 is wrong, but U+00A0 is okay.

    # AGL compliant names, but not recommended for new fonts:
    AGL_COMPLIANT_BUT_NOT_RECOMMENDED_0020 = {"uni0020", "u0020", "u00020", "u000020"}
    AGL_COMPLIANT_BUT_NOT_RECOMMENDED_00A0 = {
        "nonbreakingspace",
        "nbspace",
        "u00A0",
        "u000A0",
        "u0000A0",
    }

    if ttFont["post"].formatType == 3.0:
        yield SKIP, "Font has version 3 post table."
    else:
        passed = True

        space = get_glyph_name(ttFont, 0x0020)
        if space in AGL_RECOMMENDED_0020:
            pass

        elif space in AGL_COMPLIANT_BUT_NOT_RECOMMENDED_0020:
            passed = False
            yield WARN, Message(
                "not-recommended-0020",
                f'Glyph 0x0020 is called "{space}": Change to "space"',
            )
        else:
            passed = False
            yield FAIL, Message(
                "non-compliant-0020",
                f'Glyph 0x0020 is called "{space}": Change to "space"',
            )

        nbsp = get_glyph_name(ttFont, 0x00A0)
        if nbsp == space:
            # This is OK.
            # Some fonts use the same glyph for both space and nbsp.
            pass

        elif nbsp in AGL_RECOMMENDED_00A0:
            pass

        elif nbsp in AGL_COMPLIANT_BUT_NOT_RECOMMENDED_00A0:
            passed = False
            yield WARN, Message(
                "not-recommended-00a0",
                f'Glyph 0x00A0 is called "{nbsp}": Change to "uni00A0"',
            )
        else:
            passed = False
            yield FAIL, Message(
                "non-compliant-00a0",
                f'Glyph 0x00A0 is called "{nbsp}": Change to "uni00A0"',
            )

        if passed:
            yield PASS, "Font has **AGL recommended** names for whitespace glyphs."
