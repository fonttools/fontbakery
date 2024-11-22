from collections import defaultdict

from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import show_inconsistencies


@check(
    id="googlefonts/metadata/copyright",
    conditions=["family_metadata"],
    rationale="""
        The METADATA.pb file includes a copyright field for each font
        file in the family. The value of this field should be the same
        for all fonts in the family.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_copyright(family_metadata, config):
    """METADATA.pb: Copyright notice is the same in all fonts?"""
    copyrights = defaultdict(list)
    for font in family_metadata.fonts:
        copyrights[font.copyright].append(font.filename)
    if len(copyrights) > 1:
        yield FAIL, Message(
            "inconsistency",
            "METADATA.pb: Copyright field value is inconsistent across the family.\n"
            "The following copyright values were found:\n\n"
            + show_inconsistencies(copyrights, config),
        )
