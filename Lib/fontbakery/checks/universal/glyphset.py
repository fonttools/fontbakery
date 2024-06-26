from fontbakery.prelude import FAIL, PASS, WARN, Message, check
from fontbakery.utils import bullet_list, glyph_has_ink


@check(
    id="com.google.fonts/check/mandatory_glyphs",
    rationale="""
        The OpenType specification v1.8.2 recommends that the first glyph is the
        '.notdef' glyph without a codepoint assigned and with a drawing:

        The .notdef glyph is very important for providing the user feedback
        that a glyph is not found in the font. This glyph should not be left
        without an outline as the user will only see what looks like a space
        if a glyph is missing and not be aware of the active font’s limitation.

        https://docs.microsoft.com/en-us/typography/opentype/spec/recom#glyph-0-the-notdef-glyph

        Pre-v1.8, it was recommended that fonts should also contain 'space', 'CR'
        and '.null' glyphs. This might have been relevant for MacOS 9 applications.
    """,
    proposal="legacy:check/046",
)
def com_google_fonts_check_mandatory_glyphs(ttFont):
    """Font contains '.notdef' as its first glyph?"""
    passed = True
    NOTDEF = ".notdef"
    glyph_order = ttFont.getGlyphOrder()

    if NOTDEF not in glyph_order or len(glyph_order) == 0:
        yield WARN, Message(
            "notdef-not-found", f"Font should contain the {NOTDEF!r} glyph."
        )
        # The font doesn't even have the notdef. There's no point in testing further.
        return

    if glyph_order[0] != NOTDEF:
        passed = False
        yield WARN, Message(
            "notdef-not-first", f"The {NOTDEF!r} should be the font's first glyph."
        )

    cmap = ttFont.getBestCmap()  # e.g. {65: 'A', 66: 'B', 67: 'C'} or None
    if cmap and NOTDEF in cmap.values():
        passed = False
        rev_cmap = {name: val for val, name in reversed(sorted(cmap.items()))}
        yield WARN, Message(
            "notdef-has-codepoint",
            f"The {NOTDEF!r} glyph should not have a Unicode codepoint value assigned,"
            f" but has 0x{rev_cmap[NOTDEF]:04X}.",
        )

    if not glyph_has_ink(ttFont, NOTDEF):
        passed = False
        yield FAIL, Message(
            "notdef-is-blank",
            f"The {NOTDEF!r} glyph should contain a drawing, but it is blank.",
        )

    if passed:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/whitespace_glyphs",
    proposal="legacy:check/047",
    rationale="""
        The OpenType specification recommends that fonts should contain
        glyphs for the following whitespace characters:

        - U+0020 SPACE
        - U+00A0 NO-BREAK SPACE

        The space character is required for text processing, and the no-break
        space is useful to prevent line breaks at its position. It is also
        recommended to have a glyph for the tab character (U+0009) and the
        soft hyphen (U+00AD), but these are not mandatory.
    """,
)
def com_google_fonts_check_whitespace_glyphs(ttFont, missing_whitespace_chars):
    """Font contains glyphs for whitespace characters?"""
    failed = False
    for wsc in missing_whitespace_chars:
        failed = True
        yield FAIL, Message(
            f"missing-whitespace-glyph-{wsc}",
            f"Whitespace glyph missing for codepoint {wsc}.",
        )

    if not failed:
        yield PASS, "Font contains glyphs for whitespace characters."


@check(
    id="com.google.fonts/check/unreachable_glyphs",
    rationale="""
        Glyphs are either accessible directly through Unicode codepoints or through
        substitution rules.

        In Color Fonts, glyphs are also referenced by the COLR table. And mathematical
        fonts also reference glyphs via the MATH table.

        Any glyphs not accessible by these means are redundant and serve only
        to increase the font's file size.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3160",
)
def com_google_fonts_check_unreachable_glyphs(ttFont, config):
    """Check font contains no unreachable glyphs"""

    def remove_lookup_outputs(all_glyphs, lookup):
        if lookup.LookupType == 1:  # Single:
            # Replace one glyph with one glyph
            for sub in lookup.SubTable:
                all_glyphs -= set(sub.mapping.values())

        if lookup.LookupType == 2:  # Multiple:
            # Replace one glyph with more than one glyph
            for sub in lookup.SubTable:
                for slot in sub.mapping.values():
                    all_glyphs -= set(slot)

        if lookup.LookupType == 3:  # Alternate:
            # Replace one glyph with one of many glyphs
            for sub in lookup.SubTable:
                for slot in sub.alternates.values():
                    all_glyphs -= set(slot)

        if lookup.LookupType == 4:  # Ligature:
            # Replace multiple glyphs with one glyph
            for sub in lookup.SubTable:
                for ligatures in sub.ligatures.values():
                    all_glyphs -= set(lig.LigGlyph for lig in ligatures)

        if lookup.LookupType in [5, 6]:
            # We do nothing here, because these contextual lookup types don't
            # generate glyphs directly; they only dispatch to other lookups
            # stored elsewhere in the lookup list. As we are examining all
            # lookups in the lookup list, other calls to this function will
            # deal with the lookups that a contextual lookup references.
            pass

        if lookup.LookupType == 7:  # Extension Substitution:
            # Extension mechanism for other substitutions
            for xt in lookup.SubTable:
                xt.SubTable = [xt.ExtSubTable]
                xt.LookupType = xt.ExtSubTable.LookupType
                remove_lookup_outputs(all_glyphs, xt)

        if lookup.LookupType == 8:  # Reverse chaining context single:
            # Applied in reverse order,
            # replace single glyph in chaining context
            for sub in lookup.SubTable:
                all_glyphs -= set(sub.Substitute)

    all_glyphs = set(ttFont.getGlyphOrder())

    # Exclude cmapped glyphs
    all_glyphs -= set(ttFont.getBestCmap().values())

    # Exclude glyphs referenced by cmap format 14 variation sequences
    # (as discussed at https://github.com/fonttools/fontbakery/issues/3915):
    for table in ttFont["cmap"].tables:
        if table.format == 14:
            for values in table.uvsDict.values():
                for v in list(values):
                    if v[1] is not None:
                        all_glyphs.discard(v[1])

    # and ignore these:
    all_glyphs.discard(".null")
    all_glyphs.discard(".notdef")

    # Glyphs identified in the Extender Glyph Table within JSTF table,
    # such as kashidas, are not included in the check output:
    # https://github.com/fonttools/fontbakery/issues/4773
    if "JSTF" in ttFont:
        for subtable in ttFont["JSTF"].table.iterSubTables():
            for extender_glyph in subtable.value.JstfScript.ExtenderGlyph.ExtenderGlyph:
                all_glyphs.discard(extender_glyph)

    if "MATH" in ttFont:
        glyphinfo = ttFont["MATH"].table.MathGlyphInfo
        mathvariants = ttFont["MATH"].table.MathVariants

        for glyphname in glyphinfo.MathTopAccentAttachment.TopAccentCoverage.glyphs:
            all_glyphs.discard(glyphname)

        for glyphname in glyphinfo.ExtendedShapeCoverage.glyphs:
            all_glyphs.discard(glyphname)

        for glyphname in mathvariants.VertGlyphCoverage.glyphs:
            all_glyphs.discard(glyphname)

        for glyphname in mathvariants.HorizGlyphCoverage.glyphs:
            all_glyphs.discard(glyphname)

        for vgc in mathvariants.VertGlyphConstruction:
            if vgc.GlyphAssembly:
                for part in vgc.GlyphAssembly.PartRecords:
                    all_glyphs.discard(part.glyph)

            for rec in vgc.MathGlyphVariantRecord:
                all_glyphs.discard(rec.VariantGlyph)

        for hgc in mathvariants.HorizGlyphConstruction:
            if hgc.GlyphAssembly:
                for part in hgc.GlyphAssembly.PartRecords:
                    all_glyphs.discard(part.glyph)

            for rec in hgc.MathGlyphVariantRecord:
                all_glyphs.discard(rec.VariantGlyph)

    if "COLR" in ttFont:
        if ttFont["COLR"].version == 0:
            for glyphname, colorlayers in ttFont["COLR"].ColorLayers.items():
                for layer in colorlayers:
                    all_glyphs.discard(layer.name)

        elif ttFont["COLR"].version == 1:
            if (
                hasattr(ttFont["COLR"].table, "BaseGlyphRecordArray")
                and ttFont["COLR"].table.BaseGlyphRecordArray is not None
            ):
                for baseglyph_record in ttFont[
                    "COLR"
                ].table.BaseGlyphRecordArray.BaseGlyphRecord:
                    all_glyphs.discard(baseglyph_record.BaseGlyph)

            if (
                hasattr(ttFont["COLR"].table, "LayerRecordArray")
                and ttFont["COLR"].table.LayerRecordArray is not None
            ):
                for layer_record in ttFont["COLR"].table.LayerRecordArray.LayerRecord:
                    all_glyphs.discard(layer_record.LayerGlyph)

            for paint_record in ttFont["COLR"].table.BaseGlyphList.BaseGlyphPaintRecord:
                if hasattr(paint_record.Paint, "Glyph"):
                    all_glyphs.discard(paint_record.Paint.Glyph)

            for paint in ttFont["COLR"].table.LayerList.Paint:
                if hasattr(paint, "Glyph"):
                    all_glyphs.discard(paint.Glyph)

    if "GSUB" in ttFont and ttFont["GSUB"].table.LookupList:
        lookups = ttFont["GSUB"].table.LookupList.Lookup

        for lookup in lookups:
            remove_lookup_outputs(all_glyphs, lookup)

    # Remove components used in TrueType table
    if "glyf" in ttFont:
        for glyph_name in ttFont["glyf"].keys():
            base_glyph = ttFont["glyf"][glyph_name]
            if base_glyph.isComposite() and glyph_name not in all_glyphs:
                all_glyphs -= set(base_glyph.getComponentNames(ttFont["glyf"]))

    if all_glyphs:
        yield WARN, Message(
            "unreachable-glyphs",
            "The following glyphs could not be reached"
            " by codepoint or substitution rules:\n\n"
            f"{bullet_list(config, sorted(all_glyphs))}\n",
        )
    else:
        yield PASS, "Font did not contain any unreachable glyphs"


@check(
    id="com.google.fonts/check/soft_hyphen",
    rationale="""
        The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark
        a hyphenation possibility within a word in the absence of or
        overriding dictionary hyphenation.

        It is sometimes designed empty with no width (such as a control character),
        sometimes the same as the traditional hyphen, sometimes double encoded with
        the hyphen.

        That being said, it is recommended to not include it in the font at all,
        because discretionary hyphenation should be handled at the level of the
        shaping engine, not the font. Also, even if present, the software would
        not display that character.

        More discussion at:
        https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/4046",
        "https://github.com/fonttools/fontbakery/issues/3486",
    ],
)
def com_google_fonts_check_soft_hyphen(ttFont):
    """Does the font contain a soft hyphen?"""
    if 0x00AD in ttFont["cmap"].getBestCmap().keys():
        yield WARN, Message("softhyphen", "This font has a 'Soft Hyphen' character.")
    else:
        yield PASS, "Looks good!"


@check(
    id="com.google.fonts/check/rupee",
    rationale="""
        Per Bureau of Indian Standards every font supporting one of the
        official Indian languages needs to include Unicode Character
        “₹” (U+20B9) Indian Rupee Sign.
    """,
    conditions=["is_indic_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2967",
)
def com_google_fonts_check_rupee(ttFont):
    """Ensure indic fonts have the Indian Rupee Sign glyph."""
    if 0x20B9 not in ttFont["cmap"].getBestCmap().keys():
        yield FAIL, Message(
            "missing-rupee",
            "Please add a glyph for Indian Rupee Sign (₹) at codepoint U+20B9.",
        )
    else:
        yield PASS, "Looks good!"


@check(
    id="com.google.fonts/check/case_mapping",
    rationale="""
        Ensure that no glyph lacks its corresponding upper or lower counterpart
        (but only when unicode supports case-mapping).
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/3230",
    severity=10,  # if a font shows tofu in caps but not in lowercase
    #               then it can be considered broken.
)
def com_google_fonts_check_case_mapping(ttFont):
    """Ensure the font supports case swapping for all its glyphs."""
    import unicodedata
    from fontbakery.utils import markdown_table

    # These are a selection of codepoints for which the corresponding case-swap
    # glyphs are missing way too often on the Google Fonts library,
    # so we'll ignore for now:
    EXCEPTIONS = [
        0x0192,  # ƒ - Latin Small Letter F with Hook
        0x00B5,  # µ - Micro Sign
        0x03C0,  # π - Greek Small Letter Pi
        0x2126,  # Ω - Ohm Sign
        0x03BC,  # μ - Greek Small Letter Mu
        0x03A9,  # Ω - Greek Capital Letter Omega
        0x0394,  # Δ - Greek Capital Letter Delta
        0x0251,  # ɑ - Latin Small Letter Alpha
        0x0261,  # ɡ - Latin Small Letter Script G
        0x00FF,  # ÿ - Latin Small Letter Y with Diaeresis
        0x0250,  # ɐ - Latin Small Letter Turned A
        0x025C,  # ɜ - Latin Small Letter Reversed Open E
        0x0252,  # ɒ - Latin Small Letter Turned Alpha
        0x0271,  # ɱ - Latin Small Letter M with Hook
        0x0282,  # ʂ - Latin Small Letter S with Hook
        0x029E,  # ʞ - Latin Small Letter Turned K
        0x0287,  # ʇ - Latin Small Letter Turned T
        0x0127,  # ħ - Latin Small Letter H with Stroke
        0x0140,  # ŀ - Latin Small Letter L with Middle Dot
        0x023F,  # ȿ - Latin Small Letter S with Swash Tail
        0x0240,  # ɀ - Latin Small Letter Z with Swash Tail
        0x026B,  # ɫ - Latin Small Letter L with Middle Tilde
    ]

    missing_counterparts_table = []
    cmap = ttFont["cmap"].getBestCmap()
    for codepoint in cmap:
        if codepoint in EXCEPTIONS:
            continue

        # Only check letters
        if unicodedata.category(chr(codepoint))[0] != "L":
            continue

        the_char = chr(codepoint)
        swapped = the_char.swapcase()

        # skip cases like 'ß' => 'SS'
        if len(swapped) > 1:
            continue

        if the_char != swapped and ord(swapped) not in cmap:
            name = unicodedata.name(the_char)
            swapped_name = unicodedata.name(swapped)
            row = {
                "Glyph present in the font": f"U+{codepoint:04X}: {name}",
                "Missing case-swapping counterpart": (
                    f"U+{ord(swapped):04X}: {swapped_name}"
                ),
            }
            missing_counterparts_table.append(row)

    if missing_counterparts_table:
        yield FAIL, Message(
            "missing-case-counterparts",
            f"The following glyphs lack their case-swapping counterparts:\n\n"
            f"{markdown_table(missing_counterparts_table)}\n\n",
        )
    else:
        yield PASS, "Looks good!"
