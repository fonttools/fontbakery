from fontbakery.prelude import check, Message, WARN


@check(
    id="com.google.fonts/check/stylisticset_description",
    rationale="""
        Stylistic sets should provide description text. Programs such as InDesign,
        TextEdit and Inkscape use that info to display to the users so that they know
        what a given stylistic set offers.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3155",
)
def com_google_fonts_check_stylisticset_description(ttFont):
    """Ensure Stylistic Sets have description."""

    if "GSUB" in ttFont and ttFont["GSUB"].table.FeatureList is not None:
        for record in range(ttFont["GSUB"].table.FeatureList.FeatureCount):
            feature = ttFont["GSUB"].table.FeatureList.FeatureRecord[record]
            tag = feature.FeatureTag
            SSETS = [f"ss{n+1:02d}" for n in range(20)]
            assert "ss00" not in SSETS
            assert "ss01" in SSETS
            assert "ss20" in SSETS
            assert "ss21" not in SSETS
            if tag in SSETS:
                if feature.Feature.FeatureParams is None:
                    yield WARN, Message(
                        "missing-description",
                        f"The stylistic set {tag} lacks"
                        f" a description string on the 'name' table.",
                    )
                else:
                    # TODO: Maybe here we can add code to make sure
                    #       that the referenced nameid does exist
                    #       in the name table.
                    pass
