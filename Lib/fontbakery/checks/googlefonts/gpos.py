from fontbakery.prelude import check, condition, Message, FAIL, WARN
from fontbakery.testable import Font
from fontbakery.utils import bullet_list


@condition(Font)
def ligatures(font):
    from fontTools.ttLib.tables.otTables import LigatureSubst

    ttFont = font.ttFont
    all_ligatures = {}
    try:
        if "GSUB" in ttFont and ttFont["GSUB"].table.LookupList:
            for record in ttFont["GSUB"].table.FeatureList.FeatureRecord:
                if record.FeatureTag == "liga":
                    for index in record.Feature.LookupListIndex:
                        lookup = ttFont["GSUB"].table.LookupList.Lookup[index]
                        for subtable in lookup.SubTable:
                            if isinstance(subtable, LigatureSubst):
                                for firstGlyph in subtable.ligatures.keys():
                                    all_ligatures[firstGlyph] = []
                                    for lig in subtable.ligatures[firstGlyph]:
                                        if (
                                            lig.Component
                                            not in all_ligatures[firstGlyph]
                                        ):
                                            all_ligatures[firstGlyph].append(
                                                lig.Component
                                            )
        return all_ligatures
    except (AttributeError, IndexError):
        return -1  # Indicate fontTools-related crash...


@check(
    id="com.google.fonts/check/kerning_for_non_ligated_sequences",
    conditions=["ligatures", "has_kerning_info"],
    rationale="""
        Fonts with ligatures should have kerning on the corresponding non-ligated
        sequences for text where ligatures aren't used
        (eg https://github.com/impallari/Raleway/issues/14).
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1145",
)
def com_google_fonts_check_kerning_for_non_ligated_sequences(ttFont, config, ligatures):
    """Is there kerning info for non-ligated sequences?"""

    def look_for_nonligated_kern_info(table):
        for pairpos in table.SubTable:
            for i, glyph in enumerate(pairpos.Coverage.glyphs):
                if not hasattr(pairpos, "PairSet"):
                    continue
                for pairvalue in pairpos.PairSet[i].PairValueRecord:
                    kern_pair = (glyph, pairvalue.SecondGlyph)
                    if kern_pair in ligature_pairs:
                        ligature_pairs.remove(kern_pair)

    def ligatures_sequences(pairs):
        return [f"{first} + {second}" for first, second in pairs]

    def make_pairs(first, components):
        pairs = []
        while components:
            pairs.append((first, components[0]))
            first = components.pop(0)
        return pairs

    if ligatures == -1:
        yield FAIL, Message(
            "malformed",
            "Failed to lookup ligatures."
            " This font file seems to be malformed."
            " For more info, read:"
            " https://github.com/fonttools/fontbakery/issues/1596",
        )
    else:
        ligature_pairs = set()
        for first, comp in ligatures.items():
            for components in comp:
                pairs = make_pairs(first, components)
                ligature_pairs.update(pairs)

        ligature_pairs = sorted(ligature_pairs)

        for record in ttFont["GSUB"].table.FeatureList.FeatureRecord:
            if record.FeatureTag == "kern":
                for index in record.Feature.LookupListIndex:
                    lookup = ttFont["GSUB"].table.LookupList.Lookup[index]
                    look_for_nonligated_kern_info(lookup)

        if ligature_pairs:
            yield WARN, Message(
                "lacks-kern-info",
                f"GPOS table lacks kerning info for the following"
                f" non-ligated sequences:\n\n"
                f"{bullet_list(config, ligatures_sequences(ligature_pairs))}",
            )
