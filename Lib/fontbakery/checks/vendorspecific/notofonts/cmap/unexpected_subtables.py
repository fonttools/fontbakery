from fontbakery.prelude import check, WARN, FAIL, Message
from fontbakery.constants import (
    PlatformID,
    WindowsEncodingID,
    UnicodeEncodingID,
    MacintoshEncodingID,
)


@check(
    id="notofonts/cmap/unexpected_subtables",
    rationale="""
        There are just a few typical types of cmap subtables that are used in fonts.
        If anything different is declared in a font, it will be treated as a FAIL.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2676",
)
def check_cmap_unexpected_subtables(font):
    """Ensure all cmap subtables are the typical types expected in a font."""

    if not font.has_os2_table:
        yield FAIL, Message("font-lacks-OS/2-table", "Font lacks 'OS/2' table.")
        return

    # Note:
    #   Format 0 = Byte encoding table
    #   Format 4 = Segment mapping to delta values
    #   Format 6 = Trimmed table mapping
    #   Format 12 = Segmented coverage
    #   Format 14 = Unicode Variation Sequences
    EXPECTED_SUBTABLES = [
        # 13.7% of GFonts TTFs (389 files)
        (0, PlatformID.MACINTOSH, MacintoshEncodingID.ROMAN),
        #
        # only the Sansation family has this on GFonts
        # (4, PlatformID.MACINTOSH, MacintoshEncodingID.ROMAN),
        #
        # 38.1% of GFonts TTFs (1.082 files)
        (6, PlatformID.MACINTOSH, MacintoshEncodingID.ROMAN),
        #
        # only the Gentium family has this on GFonts
        # (4, PlatformID.UNICODE, UnicodeEncodingID.UNICODE_1_0),
        #
        # INVALID? - only the Overpass family and SawarabiGothic-Regular
        #            has this on GFonts
        # (12, PlatformID.UNICODE, 10),
        # -----------------------------------------------------------------------
        # Absolutely all GFonts TTFs have this table :-)
        (4, PlatformID.WINDOWS, WindowsEncodingID.UNICODE_BMP),
        #
        # 5.7% of GFonts TTFs (162 files)
        (12, PlatformID.WINDOWS, WindowsEncodingID.UNICODE_FULL_REPERTOIRE),
        #
        # 1.1% - Only 4 families (30 TTFs),
        # including SourceCodePro, have this on GFonts
        (14, PlatformID.UNICODE, UnicodeEncodingID.UNICODE_VARIATION_SEQUENCES),
        #
        # 97.0% of GFonts TTFs (only 84 files lack it)
        (4, PlatformID.UNICODE, UnicodeEncodingID.UNICODE_2_0_BMP_ONLY),
        #
        # 2.9% of GFonts TTFs (82 files)
        (12, PlatformID.UNICODE, UnicodeEncodingID.UNICODE_2_0_FULL),
    ]
    if font.is_cjk_font:
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

    for subtable in font.ttFont["cmap"].tables:
        if (
            subtable.format,
            subtable.platformID,
            subtable.platEncID,
        ) not in EXPECTED_SUBTABLES:
            yield WARN, Message(
                "unexpected-subtable",
                f"'cmap' has a subtable of"
                f" (format={subtable.format}, platform={subtable.platformID},"
                f" encoding={subtable.platEncID}), which it shouldn't have.",
            )
