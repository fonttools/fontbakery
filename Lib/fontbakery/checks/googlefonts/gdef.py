from fontbakery.testable import Font
from fontbakery.prelude import check, condition, FAIL, WARN, Message


@condition(Font)
def ligature_glyphs(font):
    from fontTools.ttLib.tables.otTables import LigatureSubst

    ttFont = font.ttFont
    all_ligature_glyphs = []
    try:
        if "GSUB" in ttFont and ttFont["GSUB"].table.LookupList:
            for record in ttFont["GSUB"].table.FeatureList.FeatureRecord:
                if record.FeatureTag == "liga":
                    for index in record.Feature.LookupListIndex:
                        lookup = ttFont["GSUB"].table.LookupList.Lookup[index]
                        for subtable in lookup.SubTable:
                            if isinstance(subtable, LigatureSubst):
                                for firstGlyph in subtable.ligatures.keys():
                                    for lig in subtable.ligatures[firstGlyph]:
                                        if lig.LigGlyph not in all_ligature_glyphs:
                                            all_ligature_glyphs.append(lig.LigGlyph)
        return all_ligature_glyphs
    except (AttributeError, IndexError):
        return -1  # Indicate fontTools-related crash...


@check(
    id="com.google.fonts/check/ligature_carets",
    conditions=["ligature_glyphs"],
    rationale="""
        All ligatures in a font must have corresponding caret (text cursor) positions
        defined in the GDEF table, otherwhise, users may experience issues with
        caret rendering.

        If using GlyphsApp or UFOs, ligature carets can be defined as anchors with
        names starting with `caret_`. These can be compiled with fontmake as of
        version v2.4.0.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1225",
)
def com_google_fonts_check_ligature_carets(ttFont, ligature_glyphs):
    """Are there caret positions declared for every ligature?"""
    if ligature_glyphs == -1:
        yield FAIL, Message(
            "malformed",
            (
                "Failed to lookup ligatures."
                " This font file seems to be malformed."
                " For more info, read:"
                " https://github.com/fonttools/fontbakery/issues/1596"
            ),
        )
    elif "GDEF" not in ttFont:
        yield WARN, Message(
            "GDEF-missing",
            (
                "GDEF table is missing, but it is mandatory"
                " to declare it on fonts that provide ligature"
                " glyphs because the caret (text cursor)"
                " positioning for each ligature must be"
                " provided in this table."
            ),
        )
    else:
        lig_caret_list = ttFont["GDEF"].table.LigCaretList
        if lig_caret_list is None:
            missing = set(ligature_glyphs)
        else:
            missing = set(ligature_glyphs) - set(lig_caret_list.Coverage.glyphs)

        if lig_caret_list is None or lig_caret_list.LigGlyphCount == 0:
            yield WARN, Message(
                "lacks-caret-pos",
                "This font lacks caret position values"
                " for ligature glyphs on its GDEF table.",
            )
        elif missing:
            missing = "\n\t- ".join(sorted(missing))
            yield WARN, Message(
                "incomplete-caret-pos-data",
                f"This font lacks caret positioning"
                f" values for these ligature glyphs:"
                f"\n\t- {missing}\n\n  ",
            )
