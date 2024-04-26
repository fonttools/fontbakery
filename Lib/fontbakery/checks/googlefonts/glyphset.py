from fontbakery.constants import PANOSE_Family_Type
from fontbakery.prelude import check, condition, Message, FAIL, WARN, SKIP
from fontbakery.testable import Font
from fontbakery.constants import (
    NameID,
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)
from fontbakery.utils import markdown_table, bullet_list, exit_with_install_instructions


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
    id="com.google.fonts/check/glyph_coverage",
    rationale="""
        Google Fonts expects that fonts in its collection support at least the minimal
        set of characters defined in the `GF-latin-core` glyph-set.
    """,
    conditions=["font_codepoints"],
    proposal="https://github.com/fonttools/fontbakery/pull/2488",
)
def com_google_fonts_check_glyph_coverage(ttFont, family_metadata, config):
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
    id="com.google.fonts/check/glyphsets/shape_languages",
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
def com_google_fonts_check_glyphsets_shape_languages(ttFont, config):
    """Shapes languages in all GF glyphsets."""
    from shaperglot.checker import Checker
    from shaperglot.languages import Languages
    from glyphsets import languages_per_glyphset, get_glyphsets_fulfilled

    def table_of_results(level, results):
        results_table = []
        name = shaperglot_languages[language_code]["name"]
        language = f"{language_code} ({name})"
        messages = set()
        for result in results:
            if result.message not in messages:
                results_table.append(
                    {"Language": language, f"{level} messages": result.message}
                )
                messages.add(result.message)
                language = " ^ "
        return markdown_table(results_table)

    shaperglot_checker = Checker(ttFont.reader.file.name)
    shaperglot_languages = Languages()
    any_glyphset_supported = False

    glyphsets_fulfilled = get_glyphsets_fulfilled(ttFont)
    for glyphset in glyphsets_fulfilled:
        percentage_fulfilled = glyphsets_fulfilled[glyphset]["percentage"]
        if percentage_fulfilled > 0.8:
            any_glyphset_supported = True
            for language_code in languages_per_glyphset(glyphset):
                reporter = shaperglot_checker.check(shaperglot_languages[language_code])

                if reporter.fails:
                    yield FAIL, Message(
                        "failed-language-shaping",
                        f"{glyphset} glyphset:\n\n"
                        f"{table_of_results('FAIL', reporter.fails)}\n\n",
                    )

                if reporter.warns:
                    yield WARN, Message(
                        "warning-language-shaping",
                        f"{glyphset} glyphset:\n\n"
                        f"{table_of_results('WARN', reporter.warns)}\n\n",
                    )

    if not any_glyphset_supported:
        yield FAIL, Message(
            "no-glyphset-supported",
            (
                "No GF glyphset was found to be supported >80%,"
                " so language shaping support couldn't get checked."
            ),
        )


@check(
    id="com.google.fonts/check/family/control_chars",
    conditions=["are_ttf"],
    rationale="""
        Use of some unacceptable control characters in the U+0000 - U+001F range can
        lead to rendering issues on some platforms.

        Acceptable control characters are defined as .null (U+0000) and
        CR (U+000D) for this test.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2430",
)
def com_google_fonts_check_family_control_chars(ttFonts):
    """Does font file include unacceptable control character glyphs?"""
    # list of unacceptable control character glyph names
    # definition includes the entire control character Unicode block except:
    #    - .null (U+0000)
    #    - CR (U+000D)
    unacceptable_cc_list = [
        "uni0001",
        "uni0002",
        "uni0003",
        "uni0004",
        "uni0005",
        "uni0006",
        "uni0007",
        "uni0008",
        "uni0009",
        "uni000A",
        "uni000B",
        "uni000C",
        "uni000E",
        "uni000F",
        "uni0010",
        "uni0011",
        "uni0012",
        "uni0013",
        "uni0014",
        "uni0015",
        "uni0016",
        "uni0017",
        "uni0018",
        "uni0019",
        "uni001A",
        "uni001B",
        "uni001C",
        "uni001D",
        "uni001E",
        "uni001F",
    ]

    # A dict with 'key => value' pairs of
    # font path that did not pass the check => list of unacceptable glyph names
    bad_fonts = {}

    for ttFont in ttFonts:
        passed = True
        unacceptable_glyphs_in_set = []  # a list of unacceptable glyph names identified
        glyph_name_set = set(ttFont["glyf"].glyphs.keys())
        fontname = ttFont.reader.file.name

        for unacceptable_glyph_name in unacceptable_cc_list:
            if unacceptable_glyph_name in glyph_name_set:
                passed = False
                unacceptable_glyphs_in_set.append(unacceptable_glyph_name)

        if not passed:
            bad_fonts[fontname] = unacceptable_glyphs_in_set

    if len(bad_fonts) > 0:
        msg_unacceptable = (
            "The following unacceptable control characters were identified:\n"
        )
        for fnt in bad_fonts.keys():
            bad = ", ".join(bad_fonts[fnt])
            msg_unacceptable += f" {fnt}: {bad}\n"
        yield FAIL, Message("unacceptable", f"{msg_unacceptable}")


@check(
    id="com.google.fonts/check/cjk_not_enough_glyphs",
    conditions=["is_claiming_to_be_cjk_font"],
    rationale="""
        Kana has 150 characters and it's the smallest CJK writing system.

        If a font contains less CJK glyphs than this writing system, we inform the
        user that some glyphs may be encoded incorrectly.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3214",
)
def com_google_fonts_check_cjk_not_enough_glyphs(font):
    """Does the font contain less than 150 CJK characters?"""

    cjk_glyphs = font.get_cjk_glyphs
    cjk_glyph_count = len(cjk_glyphs)
    if cjk_glyph_count > 0 and cjk_glyph_count < 150:
        if cjk_glyph_count == 1:
            N_CJK_glyphs = "There is only one CJK glyph"
        else:
            N_CJK_glyphs = f"There are only {cjk_glyph_count} CJK glyphs"

        yield WARN, Message(
            "cjk-not-enough-glyphs",
            f"{N_CJK_glyphs} when there needs to be at least 150"
            f" in order to support the smallest CJK writing system, Kana.\n"
            f"The following CJK glyphs were found:\n"
            f"{cjk_glyphs}\n"
            f"Please check that these glyphs have the correct unicodes.",
        )


@check(
    id="com.google.fonts/check/missing_small_caps_glyphs",
    rationale="""
        Ensure small caps glyphs are available if
        a font declares smcp or c2sc OT features.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3154",
)
def com_google_fonts_check_missing_small_caps_glyphs(ttFont):
    """Check small caps glyphs are available."""

    if "GSUB" in ttFont and ttFont["GSUB"].table.FeatureList is not None:
        llist = ttFont["GSUB"].table.LookupList
        for record in range(ttFont["GSUB"].table.FeatureList.FeatureCount):
            feature = ttFont["GSUB"].table.FeatureList.FeatureRecord[record]
            tag = feature.FeatureTag
            if tag in ["smcp", "c2sc"]:
                for index in feature.Feature.LookupListIndex:
                    subtable = llist.Lookup[index].SubTable[0]
                    if subtable.LookupType == 7:
                        # This is an Extension lookup
                        # used for reaching 32-bit offsets
                        # within the GSUB table.
                        subtable = subtable.ExtSubTable
                    if not hasattr(subtable, "mapping"):
                        continue
                    smcp_glyphs = set()
                    for value in subtable.mapping.values():
                        if isinstance(value, list):
                            for v in value:
                                smcp_glyphs.add(v)
                        else:
                            smcp_glyphs.add(value)
                    missing = smcp_glyphs - set(ttFont.getGlyphNames())
                    if missing:
                        missing = "\n\t - " + "\n\t - ".join(missing)
                        yield FAIL, Message(
                            "missing-glyphs",
                            f"These '{tag}' glyphs are missing:\n\n{missing}",
                        )
                break


def can_shape(ttFont, text, parameters=None):
    """
    Returns true if the font can render a text string without any
    .notdef characters.
    """
    try:
        from vharfbuzz import Vharfbuzz
    except ImportError:
        exit_with_install_instructions("googlefonts")

    filename = ttFont.reader.file.name
    vharfbuzz = Vharfbuzz(filename)
    buf = vharfbuzz.shape(text, parameters)
    return all(g.codepoint != 0 for g in buf.glyph_infos)


@check(
    id="com.google.fonts/check/render_own_name",
    rationale="""
        A base expectation is that a font family's regular/default (400 roman) style
        can render its 'menu name' (nameID 1) in itself.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3159",
)
def com_google_fonts_check_render_own_name(ttFont):
    """Check font can render its own name."""
    menu_name = (
        ttFont["name"]
        .getName(
            NameID.FONT_FAMILY_NAME,
            PlatformID.WINDOWS,
            WindowsEncodingID.UNICODE_BMP,
            WindowsLanguageID.ENGLISH_USA,
        )
        .toUnicode()
    )
    if not can_shape(ttFont, menu_name):
        yield FAIL, Message(
            "render-own-name",
            f".notdef glyphs were found when attempting to render {menu_name}",
        )
