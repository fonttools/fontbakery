from collections import defaultdict

from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import show_inconsistencies


@check(
    id="googlefonts/metadata/familyname",
    conditions=["family_metadata"],
    rationale="""
        The METADATA.pb file includes a family name field for each font
        file in the family. The value of this field should be the same
        for all fonts in the family.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_familyname(family_metadata, config):
    """Check that METADATA.pb family values are all the same."""
    names = defaultdict(list)
    for font in family_metadata.fonts:
        names[font.name].append(font.filename)
    if len(names) > 1:
        yield FAIL, Message(
            "inconsistency",
            "METADATA.pb: family name value is inconsistent across the family.\n"
            "The following name values were found:\n\n"
            + show_inconsistencies(names, config),
        )
