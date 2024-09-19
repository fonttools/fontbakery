from fontbakery.constants import PANOSE_Family_Type
from fontbakery.prelude import check, condition, Message, FAIL, WARN, SKIP
from fontbakery.testable import Font
from fontbakery.utils import markdown_table, bullet_list


def is_icon_font(ttFont, config):
    return config.get("is_icon_font") or (
        "OS/2" in ttFont
        and ttFont["OS/2"].panose.bFamilyType == PANOSE_Family_Type.LATIN_SYMBOL
    )


@condition(Font)
def is_claiming_to_be_cjk_font(font):
    """Test font object to confirm that it meets our definition of a CJK font file.

    We do this in two ways: in some cases, we are testing the *metadata*,
    i.e. what the font claims about itself, in which case the definition is
    met if any of the following conditions are True:

      1. The font has a CJK code page bit set in the OS/2 table
      2. The font has a CJK Unicode range bit set in the OS/2 table

    See below for another way of testing this.
    """
    from fontbakery.constants import (
        CJK_CODEPAGE_BITS,
        CJK_UNICODE_RANGE_BITS,
    )

    if not font.has_os2_table:
        return

    os2 = font.ttFont["OS/2"]

    # OS/2 code page checks
    for _, bit in CJK_CODEPAGE_BITS.items():
        if os2.ulCodePageRange1 & (1 << bit):
            return True

    # OS/2 Unicode range checks
    for _, bit in CJK_UNICODE_RANGE_BITS.items():
        if bit in range(0, 32):
            if os2.ulUnicodeRange1 & (1 << bit):
                return True

        elif bit in range(32, 64):
            if os2.ulUnicodeRange2 & (1 << (bit - 32)):
                return True

        elif bit in range(64, 96):
            if os2.ulUnicodeRange3 & (1 << (bit - 64)):
                return True

    # default, return False if the above checks did not identify a CJK font
    return False


@check(
    id="googlefonts/glyph_coverage",
    rationale="""
        Google Fonts expects that fonts in its collection support at least the minimal
        set of characters defined in the `GF-latin-core` glyph-set.
    """,
    conditions=["font_codepoints"],
    proposal="https://github.com/fonttools/fontbakery/pull/2488",
)
def check_glyph_coverage(ttFont, family_metadata, config):
    """Check Google Fonts glyph coverage."""
    import unicodedata2
    from glyphsets import get_glyphsets_fulfilled

    if is_icon_font(ttFont, config):
        yield SKIP, "This is an icon font or a symbol font."
        return

    glyphsets_fulfilled = get_glyphsets_fulfilled(ttFont)

    # If we have a primary_script set, we only need care about Kernel
    if family_metadata and family_metadata.primary_script:
        required_glyphset = "GF_Latin_Kernel"
    else:
        required_glyphset = "GF_Latin_Core"

    if glyphsets_fulfilled[required_glyphset]["missing"]:
        missing = [
            "0x%04X (%s)\n" % (c, unicodedata2.name(chr(c)))
            for c in glyphsets_fulfilled[required_glyphset]["missing"]
        ]
        yield FAIL, Message(
            "missing-codepoints",
            f"Missing required codepoints:\n\n" f"{bullet_list(config, missing)}",
        )


@check(
    id="googlefonts/glyphsets/shape_languages",
    rationale="""
        This check uses a heuristic to determine which GF glyphsets a font supports.
        Then it checks the font for correct shaping behaviour for all languages in
        those glyphsets.
    """,
    conditions=[
        "network"
    ],  # use Shaperglot, which uses youseedee, which downloads Unicode files
    proposal=["https://github.com/googlefonts/fontbakery/issues/4147"],
)
def check_glyphsets_shape_languages(ttFont, config):
    """Shapes languages in all GF glyphsets."""
    from shaperglot.checker import Checker
    from shaperglot.languages import Languages
    from glyphsets import languages_per_glyphset, get_glyphsets_fulfilled

    def table_of_results(level, results):
        from fontbakery.utils import pretty_print_list

        results_table = []

        for message, languages in results.items():
            results_table.append(
                {
                    f"{level} messages": message,
                    "Languages": pretty_print_list(config, languages, quiet=True),
                }
            )
        return markdown_table(results_table)

    shaperglot_checker = Checker(ttFont.reader.file.name)
    shaperglot_languages = Languages()
    any_glyphset_supported = False

    warns = {}
    fails = {}
    glyphsets_fulfilled = get_glyphsets_fulfilled(ttFont)
    for glyphset in glyphsets_fulfilled:
        if glyphsets_fulfilled[glyphset]["percentage"] > 0.8:
            any_glyphset_supported = True
            for language_code in languages_per_glyphset(glyphset):
                reporter = shaperglot_checker.check(shaperglot_languages[language_code])
                name = shaperglot_languages[language_code]["name"]
                language_string = f"{language_code} ({name})"

                for w in reporter.warns:
                    if w.message not in warns.keys():
                        warns[w.message] = []
                    warns[w.message].append(language_string)

                for f in reporter.fails:
                    if f.message not in fails.keys():
                        fails[f.message] = []
                    fails[f.message].append(language_string)

    if fails:
        yield FAIL, Message(
            "failed-language-shaping",
            f"{glyphset} glyphset:\n{table_of_results('FAIL', fails)}\n",
        )

    if warns:
        yield WARN, Message(
            "warning-language-shaping",
            f"{glyphset} glyphset:\n{table_of_results('WARN', warns)}\n",
        )

    if not any_glyphset_supported:
        yield FAIL, Message(
            "no-glyphset-supported",
            (
                "No GF glyphset was found to be supported >80%,"
                " so language shaping support couldn't get checked."
            ),
        )
