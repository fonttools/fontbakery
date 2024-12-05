import re

from fontbakery.prelude import check, PASS, SKIP, WARN, Message


@check(
    id="ufo_features_default_languagesystem",
    conditions=["ufo_font"],
    rationale="""
        The feature file specification strongly recommends to use a
        `languagesystem DFLT dflt` statement in your feature file. This
        statement is automatically inserted when no `languagesystem`
        statements are present in the feature file, *unless* there is
        another `languagesystem` statement already present. If this is
        the case, this behaviour could lead to unintended side effects.

        This check only WARNs when this happen as there are cases where
        not having a `languagesystem DFLT dflt` statement in your feature
        file is technically correct.

        http://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html#4b-language-system
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/4011",
)
def check_ufo_features_default_languagesystem(ufo_font):
    """Check that languagesystem DFLT dflt is present in the features.fea file."""

    if ufo_font.features.text is None:
        yield SKIP, "No features.fea file in font."
    elif not ufo_font.features.text.strip():
        yield PASS, "Default languagesystem inserted by compiler."
    else:
        tags = re.findall(
            r"languagesystem\s+"
            r"([A-Za-z0-9\._!$%&*+:?^'|~]{1,4})\s+"
            r"([A-Za-z0-9\._!$%&*+:?^'|~]{1,4})",
            ufo_font.features.text,
        )

        if len(tags) > 0 and ("DFLT", "dflt") != tags[0]:
            tags_str = ", ".join([" ".join(t) for t in tags])
            yield WARN, Message(
                "default-languagesystem",
                f"Default languagesystem not found in: {tags_str}.",
            )
        else:
            yield PASS, "Default languagesystem present or automatically inserted."
