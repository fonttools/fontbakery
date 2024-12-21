from fontbakery.prelude import PASS, FAIL, SKIP, Message, check


@check(
    id="smallcaps_before_ligatures",
    rationale="""
        OpenType small caps should be defined before ligature lookups to ensure
        proper functionality.

        Rainer Erich Scheichelbauer (a.k.a. MekkaBlue) pointed out in a tweet
        (https://twitter.com/mekkablue/status/1297486769668132865) that the ordering
        of small caps and ligature lookups can lead to bad results such as the example
        he provided of the word "WAFFLES" in small caps, but with an unfortunate
        lowercase ffl ligature substitution.
	
        This check attempts to detect this kind of mistake.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3020",
)
def check_smallcaps_before_ligatures(ttFont):
    """
    Ensure 'smcp' (small caps) lookups are defined before ligature lookups in the 'GSUB' table.
    """
    if "GSUB" not in ttFont:
        return SKIP, "Font lacks a 'GSUB' table."

    gsub_table = ttFont["GSUB"].table

    smcp_indices = [
        index
        for feature in gsub_table.FeatureList.FeatureRecord
        if feature.FeatureTag == "smcp"
        for index in feature.Feature.LookupListIndex
    ]
    liga_indices = [
        index
        for feature in gsub_table.FeatureList.FeatureRecord
        if feature.FeatureTag == "liga"
        for index in feature.Feature.LookupListIndex
    ]

    if not smcp_indices or not liga_indices:
        return SKIP, "Font lacks 'smcp' or 'liga' features."

    first_smcp_index = min(smcp_indices)
    first_liga_index = min(liga_indices)

    if first_smcp_index < first_liga_index:
        return PASS, "'smcp' lookups are defined before 'liga' lookups."
    else:
        return FAIL, Message(
            "feature-ordering", "'smcp' lookups are not defined before 'liga' lookups."
        )
