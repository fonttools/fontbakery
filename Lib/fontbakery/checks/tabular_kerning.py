from fontbakery.prelude import check, Message, FAIL, SKIP
from fontbakery.utils import mark_glyphs


@check(
    id="tabular_kerning",
    rationale="""
        Tabular glyphs should not have kerning, as they are meant to be used in tables.

        This check looks for kerning in:
        - all glyphs in a font in combination with tabular numerals;
        - tabular symbols in combination with tabular numerals.

        "Tabular symbols" is defined as:
        - for fonts with a "tnum" feature, all "tnum" substitution target glyphs;
        - for fonts without a "tnum" feature, all glyphs that have the same width
        as the tabular numerals, but limited to numbers, math and currency symbols.

        This check may produce false positives for fonts with no "tnum" feature
        and with equal-width numerals (and other same-width symbols) that are
        not intended to be used as tabular numerals.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4440",
)
def check_tabular_kerning(ttFont):
    """Check tabular widths don't have kerning."""
    from vharfbuzz import Vharfbuzz
    import uharfbuzz as hb
    import unicodedata

    EXCLUDE = [
        "\u0600",  # Arabic
        "\u0601",  # Arabic
        "\u0602",  # Arabic
        "\u0603",  # Arabic
        "\u0604",  # Arabic
        "\u06DD",  # Arabic
        "\u0890",  # Arabic
        "\u0891",  # Arabic
        "\u0605",  # Arabic
        "\u08E2",  # Arabic
        "\u2044",  # General Punctuation
        "\u2215",  # Mathematical Operators
    ]
    IGNORE_GLYPHS = [
        ".notdef",
        "NULL",
    ]
    GID_OFFSET = 0xF0000

    vhb = Vharfbuzz(ttFont.reader.file.name)
    best_cmap = ttFont.getBestCmap()
    unicode_for_glyphs = {v: k for k, v in best_cmap.items()}

    def nominal_glyph_func(font, code_point, data):
        if code_point > GID_OFFSET:
            return code_point - GID_OFFSET
        return 0

    funcs = hb.FontFuncs.create()
    funcs.set_nominal_glyph_func(nominal_glyph_func)
    vhb.hbfont.funcs = funcs

    def glyph_width(ttFont, glyph_name):
        return ttFont["hmtx"].metrics[glyph_name][0]

    def glyph_name_for_character(_ttFont, character):
        return best_cmap.get(ord(character))

    def unique_combinations(list_1, list_2):
        unique_combinations = []

        for i in range(len(list_1)):
            for j in range(len(list_2)):
                unique_combinations.append((list_1[i], list_2[j]))

        return unique_combinations

    def has_feature(ttFont, featureTag):
        if "GSUB" in ttFont and ttFont["GSUB"].table.FeatureList:
            for FeatureRecord in ttFont["GSUB"].table.FeatureList.FeatureRecord:
                if FeatureRecord.FeatureTag == featureTag:
                    return True
        if "GPOS" in ttFont and ttFont["GPOS"].table.FeatureList:
            for FeatureRecord in ttFont["GPOS"].table.FeatureList.FeatureRecord:
                if FeatureRecord.FeatureTag == featureTag:
                    return True
        return False

    def buf_to_width(buf):
        x_cursor = 0

        for _info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            x_cursor += pos.x_advance

        return x_cursor

    def glyph_name_to_gid(ttFont, glyph_name):
        if glyph_name.startswith("gid"):
            gid = int(glyph_name[3:])
            return gid
        return ttFont.getGlyphID(glyph_name)

    def get_substitutions(
        ttFont,
        featureTag,
        lookupType=1,
    ):
        substitutions = {}
        if "GSUB" in ttFont:
            for FeatureRecord in ttFont["GSUB"].table.FeatureList.FeatureRecord:
                if FeatureRecord.FeatureTag == featureTag:
                    for LookupIndex in FeatureRecord.Feature.LookupListIndex:
                        for SubTable in (
                            ttFont["GSUB"].table.LookupList.Lookup[LookupIndex].SubTable
                        ):
                            if SubTable.LookupType == lookupType:
                                substitutions.update(SubTable.mapping)
        return substitutions

    def get_kerning(glyph_list):
        # Either glyph is in EXCLUDED
        # Also stripping .ss01, .ss02, etc
        unicodes = [
            chr(unicode_for_glyphs[x])
            for x in [y.split(".")[0] for y in glyph_list]
            if x in unicode_for_glyphs
        ]
        excluded = set(EXCLUDE) & set(unicodes)
        if excluded:
            return 0

        glyph_list = [
            chr(GID_OFFSET + glyph_name_to_gid(ttFont, glyph_name))
            for glyph_name in glyph_list
        ]

        # Either glyph is .notdef
        if chr(GID_OFFSET) in glyph_list:
            return 0

        text = "".join(glyph_list)
        width1 = buf_to_width(vhb.shape(text, {"features": {"kern": True}}))
        width2 = buf_to_width(vhb.shape(text, {"features": {"kern": False}}))
        return width1 - width2

    def get_str_buffer(glyph_list):
        glyph_list = [
            chr(GID_OFFSET + glyph_name_to_gid(ttFont, glyph_name))
            for glyph_name in glyph_list
        ]
        text = "".join(glyph_list)
        buffer = vhb.shape(text)
        string = vhb.serialize_buf(buffer)
        return string

    def digraph_kerning(ttFont, glyph_list, expected_kerning):
        return (
            len(get_str_buffer(glyph_list).split("|")) > 1
            and get_kerning(glyph_list) == expected_kerning
        )

    # Font has no numerals at all
    if not all([glyph_name_for_character(ttFont, c) for c in "0123456789"]):
        yield SKIP, "Font has no numerals at all"
        return

    all_glyphs = list(
        set(ttFont.getGlyphOrder()) - set(IGNORE_GLYPHS) - set(mark_glyphs(ttFont))
    )
    tabular_glyphs = []
    tabular_numerals = []

    # Fonts with tnum feautre
    if has_feature(ttFont, "tnum"):
        tabular_glyphs = list(get_substitutions(ttFont, "tnum").values())
        buf = vhb.shape("0123456789", {"features": {"tnum": True}})
        tabular_numerals = vhb.serialize_buf(buf, glyphsonly=True).split("|")

    # Without tnum feature
    else:
        # Find out if font maybe has tabular numerals by default
        glyph_widths = [
            glyph_width(ttFont, glyph_name_for_character(ttFont, c))
            for c in "0123456789"
        ]
        if len(set(glyph_widths)) == 1:
            tabular_width = glyph_width(ttFont, glyph_name_for_character(ttFont, "0"))
            tabular_numerals = [
                glyph_name_for_character(ttFont, c) for c in "0123456789"
            ]
            # Collect all glyphs with the same width as the tabular numerals
            for glyph in all_glyphs:
                unicode = unicode_for_glyphs.get(glyph)
                if (
                    unicode
                    and glyph_width(ttFont, glyph) == tabular_width
                    and unicodedata.category(chr(unicode))
                    in (
                        "Nd",  # Decimal number
                        "No",  # Other number
                        "Nl",  # Letter-like number
                        "Sm",  # Math symbol
                        "Sc",  # Currency symbol
                    )
                ):
                    tabular_glyphs.append(glyph)

    # Font has no tabular numerals
    if not tabular_numerals:
        yield SKIP, "Font has no tabular numerals"
        return

    # Actually check for kerning
    if has_feature(ttFont, "kern"):
        for sets in (
            (all_glyphs, tabular_numerals),
            (tabular_numerals, tabular_glyphs),
        ):
            combinations = unique_combinations(sets[0], sets[1])
            for x, y in combinations:
                for a, b in ((x, y), (y, x)):
                    kerning = get_kerning([a, b])
                    if kerning != 0:
                        # Check if either a or b are digraphs that themselves
                        # have kerning when decomposed in ccmp
                        # that would throw off the reading, skip if it's identical
                        # to the kerning of the whole sequence
                        if digraph_kerning(ttFont, [a], kerning) or digraph_kerning(
                            ttFont, [b], kerning
                        ):
                            pass
                        else:
                            yield FAIL, Message(
                                "has-tabular-kerning",
                                f"Kerning between {a} and {b} is {kerning}, should be 0",
                            )
