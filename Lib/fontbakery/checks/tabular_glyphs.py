from fontbakery.prelude import check, Message, FAIL, SKIP, PASS


def parse_unicode_escape(s):
    import ast

    s = s.replace('"', r"\"")
    return ast.literal_eval(f'"{s}"')


def verify_widths(ttFont, hbFont, check_text):
    """Shape text and verify all shaped glyphs are the same width"""
    import uharfbuzz as hb

    buffer = hb.Buffer()
    buffer.add_str(check_text)
    buffer.guess_segment_properties()
    hb.shape(hbFont, buffer, features={"tnum": True})

    assert buffer.content_type == hb.BufferContentType.GLYPHS

    glyphs_by_width = {}
    glyphOrder = ttFont.getGlyphOrder()
    for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
        width = pos.x_advance
        # width to glyph name mapping
        glyph_name = glyphOrder[info.codepoint]
        if width in glyphs_by_width:
            glyphs_by_width[width].append(glyph_name)
        else:
            glyphs_by_width[width] = [glyph_name]

    return glyphs_by_width


def format_glyphs_by_width(glyphs_by_width):
    """
    Format glyphs_by_width as a string for output. Lists glyph groups sorted
    by the number of glyphs in each group.
    """
    output = ""
    lengths = {w: len(g) for w, g in glyphs_by_width.items()}
    output = "\n".join([f"{w}: {glyphs_by_width[w]}" for w in sorted(lengths.keys())])
    return output


# TODO: Compare this to googlefonts/family/tnum_horizontal_metrics as it seems that
#       it may be possible to merge the checks.
#
#       And see also typenetwork/family/tnum_horizontal_metrics
@check(
    id="tnum_glyphs_equal_widths",
    configs={"TEST_STR"},
    rationale="""
        Check to make sure all the tnum glyphs are the same width.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_tnum_glyphs_equal_widths(ttFont):
    """Widths of tabular number glyphs."""
    import uharfbuzz as hb

    filename = ttFont.reader.file.name
    hbBlob = hb.Blob.from_file_path(filename)
    hbFace = hb.Face(hbBlob)
    hbFont = hb.Font(hbFace)

    check_text = "0123456789"
    if TEST_STR is not None:  # type: ignore # noqa:F821 pylint:disable=E0602
        check_text = TEST_STR  # type: ignore # noqa:F821 pylint:disable=E0602

    # Evaluate any unicode escape sequences, e.g. \N{PLUS SIGN}
    check_text = "".join([parse_unicode_escape(l) for l in check_text.splitlines()])

    # Check for existence of tnum opentype feature
    if "GSUB" not in ttFont:
        yield PASS, "Font does not contain GSUB table"
        return

    gsub = ttFont["GSUB"].table
    if not any(
        feature.FeatureTag == "tnum" for feature in gsub.FeatureList.FeatureRecord
    ):
        yield PASS, "Font does not contain tnum opentype feature"
        return

    # variable or static font
    if "fvar" in ttFont:
        fvar_table = ttFont["fvar"]

        # for each named instance in fvar
        for fvar_instance in fvar_table.instances:
            instance_coord_dict = fvar_instance.coordinates
            hbFont.set_variations(instance_coord_dict)

            # Shape set of characters and verify glyphs have same width
            glyphs_with_widths = verify_widths(ttFont, hbFont, check_text)
            if len(glyphs_with_widths) > 1:
                yield FAIL, (
                    f"tnum glyphs in instance {instance_coord_dict} "
                    f"do not align:\n{format_glyphs_by_width(glyphs_with_widths)}"
                )
            else:
                yield PASS, (
                    f"tnum glyphs in instance {instance_coord_dict} "
                    f"are all the same width: {next(iter(glyphs_with_widths.values()))}"  # pylint:disable=R1708
                )

    else:
        # Shape set of characters and verify glyphs have same width
        glyphs_with_widths = verify_widths(ttFont, hbFont, check_text)
        if len(glyphs_with_widths) > 1:
            yield FAIL, (
                f"tnum glyphs appear not to align:\n{format_glyphs_by_width(glyphs_with_widths)}"
            )
        else:
            yield PASS, (
                f"tnum glyphs are all the same width: {next(iter(glyphs_with_widths.values()))}"  # pylint:disable=R1708
            )


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
    experimental="Since 2024/Jun/04",
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

    def mark_glyphs(ttFont):
        marks = []
        if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
            class_def = ttFont["GDEF"].table.GlyphClassDef.classDefs
            glyphOrder = ttFont.getGlyphOrder()
            for name in glyphOrder:
                if name in class_def and class_def[name] == 3:
                    marks.append(name)
        return marks

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
