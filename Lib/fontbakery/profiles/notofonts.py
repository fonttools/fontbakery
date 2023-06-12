import re

from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.section import Section
from fontbakery.status import WARN, PASS, FAIL, SKIP  # , INFO, ERROR
from fontbakery.callable import check  # , disable
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.constants import (
    NameID,
    PlatformID,
    WindowsEncodingID,
    UnicodeEncodingID,
    MacintoshEncodingID,
)

profile_imports = (
    (".", ("shared_conditions", "googlefonts", "googlefonts_conditions")),
)
profile = profile_factory(default_section=Section("Noto Fonts"))

profile.configuration_defaults = {
    "com.google.fonts/check/file_size": {
        "WARN_SIZE": 1 * 1024 * 1024,
        "FAIL_SIZE": 16 * 1024 * 1024,
    }
}

NOTOFONTS_PROFILE_CHECKS = GOOGLEFONTS_PROFILE_CHECKS + [
    "com.google.fonts/check/cmap/unexpected_subtables",
    "com.google.fonts/check/unicode_range_bits",
    "com.google.fonts/check/name/noto_manufacturer",
    "com.google.fonts/check/name/noto_designer",
    "com.google.fonts/check/name/noto_trademark",
    "com.google.fonts/check/cmap/format_12",
    "com.google.fonts/check/os2/noto_vendor",
    "com.google.fonts/check/hmtx/encoded_latin_digits",
    "com.google.fonts/check/hmtx/comma_period",
    "com.google.fonts/check/hmtx/whitespace_advances",
    "com.google.fonts/check/cmap/alien_codepoints",
]


# For builds which target Google Fonts, we do want these checks, but as part of
# onboarding we will be running check-googlefonts on such builds.
# On other builds (e.g. targetting Android), we still want most of the Google
# strictures but size is a premium and we will be expecting to deliver a
# "minimal" font, so we accept the fact that there will be no Latin set and no
# hinting information at all.
SKIPPED_CHECKS = [
    "com.google.fonts/check/render_own_name",
    "com.google.fonts/check/glyph_coverage",
    "com.google.fonts/check/smart_dropout",
    "com.google.fonts/check/gasp",
]

NOTOFONTS_PROFILE_CHECKS = list(
    filter(lambda c: c not in SKIPPED_CHECKS, NOTOFONTS_PROFILE_CHECKS)
)

TRADEMARK = r"(Noto|Arimo|Tinos) is a trademark of Google (Inc|LLC)"
NOTO_URL = "http://www.google.com/get/noto/"  # Vendor URL

MANUFACTURERS_URLS = {
    "Adobe Systems Incorporated": "http://www.adobe.com/type/",
    "Ek Type": "http://www.ektype.in",
    "Monotype Imaging Inc.": "http://www.monotype.com/studio",
    "JamraPatel LLC": "http://www.jamra-patel.com",
    "Danh Hong": "http://www.khmertype.org",
    "Google LLC": "http://www.google.com/get/noto/",
    "Dalton Maag Ltd": "http://www.daltonmaag.com/",
    "Lisa Huang": "http://www.lisahuang.work",
    "Mangu Purty": "",
    "LiuZhao Studio": "",
}

NOTO_DESIGNERS = [
    "Nadine Chahine - Monotype Design Team",
    "Jelle Bosma - Monotype Design Team",
    "Danh Hong and the Monotype Design Team",
    "Indian Type Foundry and the Monotype Design Team",
    "Ben Mitchell and the Monotype Design Team",
    "Vaibhav Singh and the Monotype Design Team",
    "Universal Thirst, Indian Type Foundry and the Monotype Design Team",
    "Monotype Design Team",
    "Ek Type & Mukund Gokhale",
    "Ek Type",
    "JamraPatel",
    "Dalton Maag Ltd",
    "Amélie Bonet and Sol Matas",
    "Ben Nathan",
    "Indian type Foundry, Jelle Bosma, Monotype Design Team",
    "Indian Type Foundry, Tom Grace, and the Monotype Design Team",
    "Jelle Bosma - Monotype Design Team, Universal Thirst",
    "Juan Bruce, Universal Thirst, Indian Type Foundry and the Monotype Design Team.",
    "Lisa Huang",
    "Mangu Purty",
    "Mark Jamra, Neil Patel",
    "Monotype Design Team (Regular), Sérgio L. Martins (other weights)",
    "Monotype Design Team 2013. Revised by David WIlliams 2020",
    "Monotype Design Team and DaltonMaag",
    "Monotype Design Team and Neelakash Kshetrimayum",
    "Monotype Design Team, Akaki Razmadze",
    "Monotype Design Team, Lewis McGuffie",
    "Monotype Design Team, Nadine Chahine and Nizar Qandah",
    "Monotype Design Team, Sérgio Martins",
    "Monotype Design Team. David Williams.",
    "Patrick Giasson and the Monotype Design Team",
    "David Williams",
    "LIU Zhao",
    "Steve Matteson",
    "Juan Bruce",
    "Sérgio Martins",
    "Lewis McGuffie",
    "YANG Xicheng",
]


def _get_advance_width_for_char(ttFont, ch):
    cp = ord(ch)
    cmap = ttFont.getBestCmap()
    if cp not in cmap:
        return None
    return ttFont["hmtx"][cmap[cp]][0]


@check(
    id="com.google.fonts/check/cmap/unexpected_subtables",
    rationale="""
        There are just a few typical types of cmap subtables that are used in fonts.
        If anything different is declared in a font, it will be treated as a FAIL.
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/2676",
)
def com_google_fonts_check_cmap_unexpected_subtables(
    ttFont, has_os2_table, is_cjk_font
):
    """Ensure all cmap subtables are the typical types expected in a font."""

    if not has_os2_table:
        yield FAIL, Message("font-lacks-OS/2-table", "Font lacks 'OS/2' table.")
        return

    passed = True
    # Note:
    #   Format 0 = Byte encoding table
    #   Format 4 = Segment mapping to delta values
    #   Format 6 = Trimmed table mapping
    #   Format 12 = Segmented coverage
    #   Format 14 = Unicode Variation Sequences
    EXPECTED_SUBTABLES = [
        (
            0,
            PlatformID.MACINTOSH,
            MacintoshEncodingID.ROMAN,
        ),  # 13.7% of GFonts TTFs (389 files)
        # ( 4, PlatformID.MACINTOSH, MacintoshEncodingID.ROMAN),     # only the Sansation family has this on GFonts
        (
            6,
            PlatformID.MACINTOSH,
            MacintoshEncodingID.ROMAN,
        ),  # 38.1% of GFonts TTFs (1.082 files)
        # ( 4, PlatformID.UNICODE,   UnicodeEncodingID.UNICODE_1_0), # only the Gentium family has this on GFonts
        # (12, PlatformID.UNICODE, 10), # INVALID? - only the Overpass family and SawarabiGothic-Regular has this on GFonts
        # -----------------------------------------------------------------------
        (
            4,
            PlatformID.WINDOWS,
            WindowsEncodingID.UNICODE_BMP,
        ),  # Absolutely all GFonts TTFs have this table :-)
        (
            12,
            PlatformID.WINDOWS,
            WindowsEncodingID.UNICODE_FULL_REPERTOIRE,
        ),  #   5.7% of GFonts TTFs (162 files)
        (
            14,
            PlatformID.UNICODE,
            UnicodeEncodingID.UNICODE_VARIATION_SEQUENCES,
        ),  #   1.1% - Only 4 families (30 TTFs),
        #          including SourceCodePro, have this on GFonts
        (
            4,
            PlatformID.UNICODE,
            UnicodeEncodingID.UNICODE_2_0_BMP_ONLY,
        ),  #  97.0% of GFonts TTFs (only 84 files lack it)
        (
            12,
            PlatformID.UNICODE,
            UnicodeEncodingID.UNICODE_2_0_FULL,
        ),  #   2.9% of GFonts TTFs (82 files)
    ]
    if is_cjk_font:
        EXPECTED_SUBTABLES.extend(
            [
                # Adobe says historically some programs used these to identify
                # the script in the font.  The encodingID is the quickdraw
                # script manager code.  These are placeholder tables.
                (6, PlatformID.MACINTOSH, MacintoshEncodingID.JAPANESE),
                (6, PlatformID.MACINTOSH, MacintoshEncodingID.CHINESE_TRADITIONAL),
                (6, PlatformID.MACINTOSH, MacintoshEncodingID.KOREAN),
                (6, PlatformID.MACINTOSH, MacintoshEncodingID.CHINESE_SIMPLIFIED),
            ]
        )

    for subtable in ttFont["cmap"].tables:
        if (
            subtable.format,
            subtable.platformID,
            subtable.platEncID,
        ) not in EXPECTED_SUBTABLES:
            passed = False
            yield WARN, Message(
                "unexpected-subtable",
                f"'cmap' has a subtable of"
                f" (format={subtable.format}, platform={subtable.platformID},"
                f" encoding={subtable.platEncID}), which it shouldn't have.",
            )
    if passed:
        yield PASS, "All cmap subtables look good!"


@check(
    id="com.google.fonts/check/unicode_range_bits",
    rationale="""
        When the UnicodeRange bits on the OS/2 table are not properly set,
        some programs running on Windows may not recognize the font and use a
        system fallback font instead. For that reason, this check calculates the
        proper settings by inspecting the glyphs declared on the cmap table and
        then ensures that their corresponding ranges are enabled.
    """,
    conditions=["unicoderange", "preferred_cmap"],
    proposal="https://github.com/googlefonts/fontbakery/issues/2676",
)
def com_google_fonts_check_unicode_range_bits(ttFont, unicoderange, preferred_cmap):
    """Ensure UnicodeRange bits are properly set."""
    from fontbakery.constants import UNICODERANGE_DATA
    from fontbakery.utils import (
        compute_unicoderange_bits,
        unicoderange_bit_name,
        chars_in_range,
    )

    expected_unicoderange = compute_unicoderange_bits(ttFont)
    difference = unicoderange ^ expected_unicoderange
    if not difference:
        yield PASS, "Looks good!"
    else:
        for bit in range(128):
            if difference & (1 << bit):
                range_name = unicoderange_bit_name(bit)
                num_chars = len(chars_in_range(ttFont, bit))
                range_size = sum(
                    entry[3] - entry[2] + 1 for entry in UNICODERANGE_DATA[bit]
                )
                set_unset = "1"
                if num_chars == 0:
                    set_unset = "0"
                    num_chars = "none"
                yield WARN, Message(
                    "bad-range-bit",
                    f'UnicodeRange bit {bit} "{range_name}" should be'
                    f" {set_unset} because cmap has {num_chars} of"
                    f" the {range_size} codepoints in this range.",
                )


@check(
    id="com.google.fonts/check/name/noto_manufacturer",
    rationale="""
        Noto fonts must contain known manufacturer and manufacturer
        URL entries in the name table.
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/3681",
)
def com_google_fonts_check_noto_manufacturer(ttFont):
    """Ensure the manufacturer is a known Noto manufacturer and the URL is correct."""
    from fontbakery.utils import get_name_entry_strings

    bad = False
    manufacturers = get_name_entry_strings(ttFont, NameID.MANUFACTURER_NAME)
    good_manufacturer = None
    if not manufacturers:
        bad = True
        yield FAIL, Message(
            "no-manufacturer", "The font contained no manufacturer name"
        )

    manufacturer_re = "|".join(MANUFACTURERS_URLS.keys())
    for manufacturer in manufacturers:
        m = re.search(manufacturer_re, manufacturer)
        if m:
            good_manufacturer = m[0]
        else:
            bad = True
            yield WARN, Message(
                "unknown-manufacturer",
                f"The font's manufacturer name '{manufacturer}' was"
                f" not a known Noto font manufacturer",
            )

    designer_urls = get_name_entry_strings(ttFont, NameID.DESIGNER_URL)
    if not designer_urls:
        bad = True
        yield WARN, Message("no-designer-urls", "The font contained no designer URL")
    if good_manufacturer:
        expected_url = MANUFACTURERS_URLS[good_manufacturer]
        for designer_url in designer_urls:
            if designer_url != expected_url:
                yield WARN, Message(
                    "bad-designer-url",
                    f"The font's designer URL was '{designer_url}'"
                    f" but should have been '{expected_url}'",
                )
    if not bad:
        yield PASS, "The manufacturer name and designer URL entries were valid"


@check(
    id="com.google.fonts/check/name/noto_designer",
    rationale="""
        Noto fonts must contain known designer entries in the name table.
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/3681",
)
def com_google_fonts_check_noto_designer(ttFont):
    """Ensure the designer is a known Noto designer."""
    from fontbakery.utils import get_name_entry_strings

    bad = False
    designers = get_name_entry_strings(ttFont, NameID.DESIGNER)
    if not designers:
        bad = True
        yield FAIL, Message("no-designer", "The font contained no designer name")

    for designer in designers:
        if designer not in NOTO_DESIGNERS:
            bad = True
            yield WARN, Message(
                "unknown-designer",
                f"The font's designer name '{designer}' was "
                "not a known Noto font designer",
            )
    if not bad:
        yield PASS, "The designer name entry was valid"


@check(
    id="com.google.fonts/check/name/noto_trademark",
    rationale="""
        Noto fonts must contain the correct trademark entry in the name table.
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/3681",
)
def com_google_fonts_check_noto_trademark(ttFont):
    """Ensure the trademark matches the expected string."""
    from fontbakery.utils import get_name_entry_strings

    bad = False
    trademarks = get_name_entry_strings(ttFont, NameID.TRADEMARK)
    if not trademarks:
        bad = True
        yield FAIL, Message("no-trademark", "The font contained no trademark entry")
    for trademark in trademarks:
        if not re.match(TRADEMARK, trademark):
            bad = True
            yield FAIL, Message(
                "bad-trademark",
                f"The trademark entry should be '{TRADEMARK}' "
                f"but was actually '{trademark}'",
            )

    if not bad:
        yield PASS, "The trademark name entry was valid"


@check(
    id="com.google.fonts/check/cmap/format_12",
    rationale="""
        If a format 12 cmap table is used to address codepoints beyond the BMP,
        it should actually contain such codepoints. Additionally, it should also
        contain all characters mapped in the format 4 subtable.
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/3681",
)
def com_google_fonts_check_cmap_format_12(ttFont, config):
    """Check that format 12 cmap subtables are correctly constituted."""
    bad = False
    skipped = True
    # Find the format 4
    cmap4 = None
    for table in ttFont["cmap"].tables:
        if table.format == 4:
            cmap4 = table
            break

    if not cmap4:
        yield FAIL, Message(
            "no-cmap-4", "The font did not contain a format 4 cmap table"
        )
        return

    for subtable in ttFont["cmap"].tables:
        if subtable.format != 12:
            continue
        skipped = False
        codepoints = subtable.cmap.keys()
        if not any(cp > 0x0FFF for cp in codepoints):
            bad = True
            yield FAIL, Message(
                "pointless-format-12",
                "A format 12 subtable did not contain"
                " any codepoints beyond the Basic Multilingual Plane (BMP)",
            )
        unmapped_from_4 = set(cmap4.cmap.keys()) - set(codepoints)
        if unmapped_from_4:
            from fontbakery.utils import pretty_print_list

            yield WARN, Message(
                "unmapped-from-4",
                f"A format 12 subtable did not the following codepoints"
                f" mapped in the format 4 subtable:"
                f" {pretty_print_list(config, unmapped_from_4)}",
            )

    if skipped:
        yield SKIP, "No format 12 subtables found"
    elif not bad:
        yield PASS, "All format 12 subtables were correctly formed"


@check(
    id="com.google.fonts/check/os2/noto_vendor",
    rationale="""
        Vendor ID must be 'GOOG'
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/3681",
)
def com_google_fonts_check_os2_noto_vendor(ttFont):
    """Check OS/2 achVendID is set to GOOG."""

    vendor_id = ttFont["OS/2"].achVendID
    if vendor_id != "GOOG":
        yield FAIL, Message(
            "bad-vendor-id", f"OS/2 VendorID is '{vendor_id}', but should be 'GOOG'."
        )
    else:
        yield PASS, f"OS/2 VendorID '{vendor_id}' is correct."


@check(
    id="com.google.fonts/check/hmtx/encoded_latin_digits",
    rationale="""
        Encoded Latin digits in Noto fonts should have equal advance widths.
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/3681",
)
def com_google_fonts_check_htmx_encoded_latin_digits(ttFont):
    """Check all encoded Latin digits have the same advance width"""
    bad = False
    digits = "0123456789"
    zero_width = _get_advance_width_for_char(ttFont, "0")
    if zero_width is None:
        yield SKIP, "No encoded Latin digits"
        return
    for d in digits:
        actual_width = _get_advance_width_for_char(ttFont, d)
        if actual_width is None:
            bad = True
            yield FAIL, Message("missing-digit", f"Missing Latin digit {d}")
        elif actual_width != zero_width:
            bad = True
            yield FAIL, Message(
                "bad-digit-width",
                f"Width of {d} was expected to be "
                f"{zero_width} but was {actual_width}",
            )
    if not bad:
        yield PASS, "All Latin digits had same advance width"


@check(
    id="com.google.fonts/check/hmtx/comma_period",
    rationale="""
        If Latin comma and period are encoded in Noto fonts,
        they should have equal advance widths.
    """,
)
def com_google_fonts_check_htmx_comma_period(ttFont):
    """Check comma and period have the same advance width"""
    comma = _get_advance_width_for_char(ttFont, ",")
    period = _get_advance_width_for_char(ttFont, ".")
    if comma is None or period is None:
        yield SKIP, "No comma and/or period"
    elif comma != period:
        yield FAIL, Message(
            "comma-period",
            f"Advance width of comma ({comma}) != advance width" f" of period {period}",
        )
    else:
        yield PASS, "Comma and period had the same advance width"


@check(
    id="com.google.fonts/check/hmtx/whitespace_advances",
    rationale="""
        Encoded whitespace in Noto fonts should have well-defined advance widths.
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/3681",
)
def com_google_fonts_check_htmx_whitespace_advances(
    ttFont, config, glyph_metrics_stats
):
    """Check all whitespace glyphs have correct advances"""
    import math

    problems = []
    if glyph_metrics_stats["seems_monospaced"]:
        yield SKIP, "Monospace glyph widths handled in other checks"
        return

    space_width = _get_advance_width_for_char(ttFont, " ")
    period_width = _get_advance_width_for_char(ttFont, ".")
    digit_width = _get_advance_width_for_char(ttFont, "0")
    em_width = ttFont["head"].unitsPerEm
    expectations = {
        0x09: space_width,  # tab
        0xA0: space_width,  # nbsp
        0x2000: em_width / 2,
        0x2001: em_width,
        0x2002: em_width / 2,
        0x2003: em_width,
        0x2004: em_width / 3,
        0x2005: em_width / 4,
        0x2006: em_width / 6,
        0x2007: digit_width,
        0x2008: period_width,
        0x2009: (em_width / 6, em_width / 5),
        0x200A: (em_width / 16, em_width / 10),
        0x200B: 0,
    }
    for cp, expected_width in expectations.items():
        got_width = _get_advance_width_for_char(ttFont, chr(cp))
        if got_width is None:
            continue
        if isinstance(expected_width, tuple):
            if got_width < math.floor(expected_width[0]) or got_width > math.ceil(
                expected_width[1]
            ):
                problems.append(
                    f"0x{cp:02x} (got={got_width},"
                    f" expected={expected_width[0]}...{expected_width[1]}"
                )
        else:
            if got_width != round(expected_width):
                problems.append(
                    f"0x{cp:02x} (got={got_width}," f" expected={expected_width}"
                )

    if problems:
        from fontbakery.utils import pretty_print_list

        formatted_list = "\t* " + pretty_print_list(config, problems, sep="\n\t* ")
        yield FAIL, Message(
            "bad-whitespace-advances",
            f"The following glyphs had wrong advance widths:\n" f"{formatted_list}",
        )
    else:
        yield PASS, "Whitespace glyphs had correct advance widths"


@check(
    id="com.google.fonts/check/cmap/alien_codepoints",
    rationale="""
        Private Use Area codepoints and Surrogate Pairs should not be encoded.
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/3681",
)
def com_google_fonts_check_cmap_alien_codepoints(ttFont, config):
    """Check no PUA or Surrogate Pair codepoints encoded"""
    pua = []
    surrogate = []
    for cp in ttFont.getBestCmap().keys():
        if (
            (0xE000 <= cp <= 0xF8FF)
            or (0xF0000 <= cp <= 0xFFFFD)
            or (0x100000 <= cp <= 0x10FFFD)
        ):
            pua.append(f"0x{cp:02x}")
        if 0xD800 <= cp <= 0xDFFF:
            surrogate.append(f"0x{cp:02x}")
    if not pua and not surrogate:
        yield PASS, "No alien codepoints were encoded"
        return

    from fontbakery.utils import pretty_print_list

    if pua:
        yield FAIL, Message(
            "pua-encoded",
            "The following private use area codepoints were"
            " encoded in the font: " + pretty_print_list(config, pua),
        )
    if surrogate:
        yield FAIL, Message(
            "surrogate-encoded",
            "The following surrogate pair codepoints were"
            " encoded in the font: " + pretty_print_list(config, surrogate),
        )


profile.auto_register(
    globals(),
    filter_func=lambda type, id, _: not (
        type == "check" and id not in NOTOFONTS_PROFILE_CHECKS
    ),
)
profile.test_expected_checks(NOTOFONTS_PROFILE_CHECKS, exclusive=True)
