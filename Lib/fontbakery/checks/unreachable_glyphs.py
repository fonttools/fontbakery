from copy import deepcopy

from fontbakery.prelude import check, Message, WARN, PASS
from fontbakery.utils import bullet_list


@check(
    id="unreachable_glyphs",
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
def unreachable_glyphs(ttFont, config):
    """Check font contains no unreachable glyphs"""

    # remove_lookup_outputs() mutates the TTF; deep copy to avoid this, and so
    # avoid issues with concurrent tests that also use ttFont.
    # See https://github.com/fonttools/fontbakery/issues/4834
    ttFont = deepcopy(ttFont)

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

            if ttFont["COLR"].table.LayerList:
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
