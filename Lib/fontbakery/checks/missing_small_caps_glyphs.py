from fontbakery.prelude import check, Message, FAIL


@check(
    id="missing_small_caps_glyphs",
    rationale="""
        Ensure small caps glyphs are available if
        a font declares smcp or c2sc OT features.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3154",
)
def check_missing_small_caps_glyphs(ttFont):
    """Ensure small caps glyphs are available."""

    if "GSUB" in ttFont and ttFont["GSUB"].table.FeatureList is not None:
        llist = ttFont["GSUB"].table.LookupList
        for record in range(ttFont["GSUB"].table.FeatureList.FeatureCount):
            feature = ttFont["GSUB"].table.FeatureList.FeatureRecord[record]
            tag = feature.FeatureTag
            if tag in ["smcp", "c2sc"]:
                for index in feature.Feature.LookupListIndex:
                    subtable = llist.Lookup[index].SubTable[0]
                    if subtable.LookupType == 7:
                        # This is an Extension lookup
                        # used for reaching 32-bit offsets
                        # within the GSUB table.
                        subtable = subtable.ExtSubTable
                    if not hasattr(subtable, "mapping"):
                        continue
                    smcp_glyphs = set()
                    for value in subtable.mapping.values():
                        if isinstance(value, list):
                            for v in value:
                                smcp_glyphs.add(v)
                        else:
                            smcp_glyphs.add(value)
                    missing = smcp_glyphs - set(ttFont.getGlyphNames())
                    if missing:
                        missing = "\n\t - " + "\n\t - ".join(missing)
                        yield FAIL, Message(
                            "missing-glyphs",
                            f"These '{tag}' glyphs are missing:\n\n{missing}",
                        )
                break
