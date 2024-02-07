from fontbakery.prelude import check, Message, PASS, FAIL, WARN
from fontbakery.shared_conditions import ligatures  # pylint: disable=unused-import
from fontbakery.utils import bullet_list


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
def com_google_fonts_check_kerning_for_non_ligated_sequences(
    ttFont, config, ligatures, has_kerning_info
):
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

    if ligatures == -1:
        yield FAIL, Message(
            "malformed",
            "Failed to lookup ligatures."
            " This font file seems to be malformed."
            " For more info, read:"
            " https://github.com/fonttools/fontbakery/issues/1596",
        )
    else:
        ligature_pairs = []
        for first, comp in ligatures.items():
            for components in comp:
                while components:
                    pair = (first, components[0])
                    if pair not in ligature_pairs:
                        ligature_pairs.append(pair)
                    first = components[0]
                    components.pop(0)

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
        else:
            yield PASS, (
                "GPOS table provides kerning info for all non-ligated sequences."
            )
