import re

from fontbakery.prelude import FAIL, PASS, SKIP, WARN, Message, check
from fontbakery.utils import pretty_print_list


@check(
    id="valid_glyphnames",
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
        "https://github.com/fonttools/fontbakery/issues/2832",  # increase to 63 chars
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_valid_glyphnames(ttFont, config):
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
