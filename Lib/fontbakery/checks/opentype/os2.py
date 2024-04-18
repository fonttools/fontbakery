from collections import defaultdict
from typing import Iterable
from fontbakery.callable import check
from fontbakery.message import Message
from fontbakery.status import FAIL, INFO, PASS, SKIP, WARN, FATAL
from fontbakery.testable import Font
from fontbakery.utils import show_inconsistencies, bullet_list


@check(
    id="com.google.fonts/check/family/panose_familytype",
    proposal="legacy:check/010",
    rationale="""
    The [PANOSE value](https://monotype.github.io/panose/) in the OS/2 table is a
    way of classifying a font based on its visual appearance and characteristics.

    The first field in the PANOSE classification is the family type: 2 means Latin
    Text, 3 means Latin Script, 4 means Latin Decorative, 5 means Latin Symbol.
    This check ensures that within a family, all fonts have the same family type.
""",
)
def com_google_fonts_check_family_panose_familytype(fonts: Iterable[Font], config):
    """Fonts have consistent PANOSE family type?"""
    missing = []
    familytypes = defaultdict(list)

    for font in fonts:
        if "OS/2" not in font.ttFont:
            missing.append(font.file_displayname)
            continue
        familytype = font.ttFont["OS/2"].panose.bFamilyType
        familytypes[familytype].append(font.file_displayname)

    if missing:
        yield FAIL, Message(
            "lacks-OS/2",
            "One or more fonts lack the required OS/2 table:\n"
            + bullet_list(config, missing),
        )

    if len(familytypes) > 1:
        yield WARN, Message(
            "inconsistency",
            "PANOSE family type is not the same across this family."
            " In order to fix this, please make sure that"
            " the panose.bFamilyType value is the same"
            " in the OS/2 table of all of this family font files.\n\n"
            "The following PANOSE family types were found:\n\n"
            + show_inconsistencies(familytypes, config),
        )


@check(
    id="com.google.fonts/check/xavgcharwidth",
    proposal="legacy:check/034",
    rationale="""
    The OS/2.xAvgCharWidth field is used to calculate the width of a string of characters.
    It is the average width of all non-zero width glyphs in the font.

    This check ensures that the value is correct. A failure here may indicate
    a bug in the font compiler, rather than something that the designer can
    do anything about.""",
)
def com_google_fonts_check_xavgcharwidth(ttFont):
    """Check if OS/2 xAvgCharWidth is correct."""

    if "OS/2" not in ttFont:
        yield FAIL, Message("lacks-OS/2", "Required OS/2 table is missing.")
        return

    current_value = ttFont["OS/2"].xAvgCharWidth
    ACCEPTABLE_ERROR = 10  # Width deviation tolerance in font units

    # Since version 3, the average is computed using _all_ glyphs in a font.
    if ttFont["OS/2"].version >= 3:
        calculation_rule = "the average of the widths of all glyphs in the font"
        if not ttFont["hmtx"].metrics:  # May contain just '.notdef', which is valid.
            yield FATAL, Message(
                "missing-glyphs",
                "Found no glyph width data in the hmtx table!",
            )
            return

        width_sum = 0
        count = 0
        for width, _ in ttFont[
            "hmtx"
        ].metrics.values():  # At least .notdef must be present.
            # The OpenType spec excludes negative widths (the
            # relevant field in `hmtx` tables is unsigned);
            # other formats (UFO) may allow signed, and
            # therefore negative, widths.
            # For extra reassurance, here we only count strictly
            # positive widths.
            if width > 0:
                count += 1
                width_sum += width

        expected_value = int(round(width_sum / count))
    else:  # Version 2 and below only consider lowercase latin glyphs and space.
        calculation_rule = (
            "the weighted average of the widths of the latin"
            " lowercase glyphs in the font"
        )
        weightFactors = {
            "a": 64,
            "b": 14,
            "c": 27,
            "d": 35,
            "e": 100,
            "f": 20,
            "g": 14,
            "h": 42,
            "i": 63,
            "j": 3,
            "k": 6,
            "l": 35,
            "m": 20,
            "n": 56,
            "o": 56,
            "p": 17,
            "q": 4,
            "r": 49,
            "s": 56,
            "t": 71,
            "u": 31,
            "v": 10,
            "w": 18,
            "x": 3,
            "y": 18,
            "z": 2,
            "space": 166,
        }
        glyph_order = ttFont.getGlyphOrder()
        if not all(character in glyph_order for character in weightFactors):
            yield FATAL, Message(
                "missing-glyphs",
                "Font is missing the required latin lowercase letters and/or space.",
            )
            return

        width_sum = 0
        for glyph_id in weightFactors:
            width = ttFont["hmtx"].metrics[glyph_id][0]
            width_sum += width * weightFactors[glyph_id]

        expected_value = int(width_sum / 1000.0 + 0.5)  # round to closest int

    difference = abs(current_value - expected_value)

    # We accept matches and off-by-ones due to rounding as correct.
    if current_value == expected_value or difference == 1:
        yield PASS, "OS/2 xAvgCharWidth value is correct."
    elif difference < ACCEPTABLE_ERROR:
        yield INFO, Message(
            "xAvgCharWidth-close",
            f"OS/2 xAvgCharWidth is {current_value} but it should be"
            f" {expected_value} which corresponds to {calculation_rule}."
            f" These are similar values, which"
            f" may be a symptom of the slightly different"
            f" calculation of the xAvgCharWidth value in"
            f" font editors. There's further discussion on"
            f" this at https://github.com/fonttools/fontbakery"
            f"/issues/1622",
        )
    else:
        yield WARN, Message(
            "xAvgCharWidth-wrong",
            f"OS/2 xAvgCharWidth is {current_value} but it should be"
            f" {expected_value} which corresponds to {calculation_rule}.",
        )


@check(
    id="com.adobe.fonts/check/fsselection_matches_macstyle",
    rationale="""
        The bold and italic bits in OS/2.fsSelection must match the bold and italic
        bits in head.macStyle per the OpenType spec.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2382",
)
def com_adobe_fonts_check_fsselection_matches_macstyle(ttFont):
    """Check if OS/2 fsSelection matches head macStyle bold and italic bits."""

    # Check both OS/2 and head are present.
    missing_tables = False

    required = ["OS/2", "head"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL, Message(f"lacks-{key}", f"The '{key}' table is missing.")
    if missing_tables:
        return

    from fontbakery.constants import FsSelection, MacStyle

    head_bold = (ttFont["head"].macStyle & MacStyle.BOLD) != 0
    os2_bold = (ttFont["OS/2"].fsSelection & FsSelection.BOLD) != 0
    if head_bold != os2_bold:
        yield FAIL, Message(
            "fsselection-macstyle-bold",
            "The OS/2.fsSelection and head.macStyle bold settings do not match:\n\n"
            f"* OS/2.fsSelection: BOLD is {'not ' if not os2_bold else ''}set\n"
            f"* head.macStyle: BOLD is {'not ' if not head_bold else ''}set",
        )
    head_italic = (ttFont["head"].macStyle & MacStyle.ITALIC) != 0
    os2_italic = (ttFont["OS/2"].fsSelection & FsSelection.ITALIC) != 0
    if head_italic != os2_italic:
        yield FAIL, Message(
            "fsselection-macstyle-italic",
            "The OS/2.fsSelection and head.macStyle italic settings do not match.\n\n"
            f"* OS/2.fsSelection: ITALIC is {'not ' if not os2_italic else ''}set\n"
            f"* head.macStyle: ITALIC is {'not ' if not head_italic else ''}set",
        )


@check(
    id="com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",
    conditions=["RIBBI_ttFonts"],
    rationale="""
        Per the OpenType spec: name ID 1 'is used in combination with Font Subfamily
        name (name ID 2), and should be shared among at most four fonts that differ
        only in weight or style.

        This four-way distinction should also be reflected in the OS/2.fsSelection
        field, using bits 0 and 5.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2388",
)
def com_adobe_fonts_check_family_bold_italic_unique_for_nameid1(RIBBI_ttFonts):
    """Check that OS/2.fsSelection bold & italic settings are unique
    for each NameID1"""
    from collections import Counter

    from fontbakery.constants import FsSelection, NameID
    from fontbakery.utils import get_name_entry_strings

    family_name_and_bold_italic = []
    for ttFont in RIBBI_ttFonts:
        names_list = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
        # names_list will likely contain multiple entries, e.g. multiple copies
        # of the same name in the same language for different platforms, but
        # also different names in different languages, we use set() below
        # to remove the duplicates and only store the unique family name(s)
        # used for a given font
        names_set = set(names_list)

        bold = (ttFont["OS/2"].fsSelection & FsSelection.BOLD) != 0
        italic = (ttFont["OS/2"].fsSelection & FsSelection.ITALIC) != 0
        bold_italic = "Bold=%r, Italic=%r" % (bold, italic)

        for name in names_set:
            family_name_and_bold_italic.append(
                (
                    name,
                    bold_italic,
                )
            )

    counter = Counter(family_name_and_bold_italic)
    for (family_name, bold_italic), count in counter.items():
        if count > 1:
            yield FAIL, Message(
                "unique-fsselection",
                f"Family '{family_name}' has {count} fonts"
                f" (should be no more than 1) with the"
                f" same OS/2.fsSelection bold & italic settings:"
                f" {bold_italic}",
            )


@check(
    id="com.google.fonts/check/code_pages",
    rationale="""
        At least some programs (such as Word and Sublime Text) under Windows 7
        do not recognize fonts unless code page bits are properly set on the
        ulCodePageRange1 (and/or ulCodePageRange2) fields of the OS/2 table.

        More specifically, the fonts are selectable in the font menu, but whichever
        Windows API these applications use considers them unsuitable for any
        character set, so anything set in these fonts is rendered with Arial as a
        fallback font.

        This check currently does not identify which code pages should be set.
        Auto-detecting coverage is not trivial since the OpenType specification
        leaves the interpretation of whether a given code page is "functional"
        or not open to the font developer to decide.

        So here we simply detect as a FAIL when a given font has no code page
        declared at all.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2474",
)
def com_google_fonts_check_code_pages(ttFont):
    """Check code page character ranges"""

    if "OS/2" not in ttFont:
        yield FAIL, Message("lacks-OS/2", "The required OS/2 table is missing.")
        return

    if (
        not hasattr(ttFont["OS/2"], "ulCodePageRange1")
        or not hasattr(ttFont["OS/2"], "ulCodePageRange2")
        or (
            ttFont["OS/2"].ulCodePageRange1 == 0
            and ttFont["OS/2"].ulCodePageRange2 == 0
        )
    ):
        yield FAIL, Message(
            "no-code-pages",
            "No code pages defined in the OS/2 table"
            " ulCodePageRange1 and CodePageRange2 fields.",
        )


@check(
    id="com.thetypefounders/check/vendor_id",
    rationale="""
        When a font project's Vendor ID is specified explicitly on FontBakery's
        configuration file, all binaries must have a matching vendor identifier
        value in the OS/2 table.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3941",
)
def com_thetypefounders_check_vendor_id(config, ttFont):
    """Checking OS/2 achVendID against configuration."""

    if "vendor_id" not in config:
        yield SKIP, (
            "Add the `vendor_id` key to a `fontbakery.yaml` file"
            " on your font project directory to enable this check.\n"
            "You'll also need to use the `--configuration` flag when"
            " invoking fontbakery."
        )
        return

    if "OS/2" not in ttFont:
        yield FAIL, Message("lacks-OS/2", "The required OS/2 table is missing.")
        return

    config_vendor_id = config["vendor_id"]
    font_vendor_id = ttFont["OS/2"].achVendID

    if config_vendor_id != font_vendor_id:
        yield FAIL, Message(
            "bad-vendor-id",
            f"OS/2 VendorID is '{font_vendor_id}',"
            f" but should be '{config_vendor_id}'.",
        )


@check(
    id="com.google.fonts/check/fsselection",
    conditions=["style"],
    proposal="legacy:check/129",
    rationale="""
    The OS/2.fsSelection field is a bit field used to specify the stylistic
    qualities of the font - in particular, it specifies to some operating
    systems whether the font is italic (bit 0), bold (bit 5) or regular
    (bit 6).

    This check verifies that the fsSelection field is set correctly for the
    font style. For a family of static fonts created in GlyphsApp, this is
    set by using the style linking checkboxes in the exports settings.
    """,
)
def com_google_fonts_check_fsselection(ttFont, style):
    """Checking OS/2 fsSelection value."""
    from fontbakery.constants import RIBBI_STYLE_NAMES, STATIC_STYLE_NAMES, FsSelection
    from fontbakery.utils import check_bit_entry

    # Checking fsSelection REGULAR bit:
    expected = "Regular" in style or (
        style in STATIC_STYLE_NAMES
        and style not in RIBBI_STYLE_NAMES
        and "Italic" not in style
    )
    yield check_bit_entry(
        ttFont,
        "OS/2",
        "fsSelection",
        expected,
        bitmask=FsSelection.REGULAR,
        bitname="REGULAR",
    )

    # Checking fsSelection ITALIC bit:
    expected = "Italic" in style
    yield check_bit_entry(
        ttFont,
        "OS/2",
        "fsSelection",
        expected,
        bitmask=FsSelection.ITALIC,
        bitname="ITALIC",
    )

    # Checking fsSelection BOLD bit:
    expected = style in ["Bold", "BoldItalic"]
    yield check_bit_entry(
        ttFont,
        "OS/2",
        "fsSelection",
        expected,
        bitmask=FsSelection.BOLD,
        bitname="BOLD",
    )
