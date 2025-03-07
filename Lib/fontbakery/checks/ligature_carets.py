from fontbakery.testable import Font
from fontbakery.prelude import check, condition, SKIP, WARN, Message
from fontbakery.utils import bullet_list


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
        return []  # fontTools bug perhaps? (issue #1596)


@check(
    id="ligature_carets",
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
def check_ligature_carets(config, ttFont, ligature_glyphs):
    """Are there caret positions declared for every ligature?"""
    if len(ligature_glyphs) == 0:
        yield SKIP, Message("no-ligatures", "No ligature glyphs found.")
    elif "GDEF" not in ttFont:
        yield WARN, Message(
            "lacks-caret-pos-gdef",
            "This font lacks caret position values"
            " for ligature glyphs because it doesn't have a GDEF table.",
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
            missing = bullet_list(config, sorted(missing))
            yield WARN, Message(
                "incomplete-caret-pos-data",
                f"This font lacks caret positioning values for these ligature glyphs:\n"
                f"{missing}\n\n",
            )
