from opentypespec.tags import FEATURE_TAGS

from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import feature_tags


DEPRECATED_TAGS = ["hngl", "opbd", "size"]


@check(
    id="opentype/layout_valid_feature_tags",
    rationale="""
        Incorrect tags can be indications of typos, leftover debugging code or
        questionable approaches, or user error in the font editor. Such typos can
        cause features and language support to fail to work as intended.

        Font vendors may use private tags to identify private features. These tags
        must be four uppercase letters (A-Z) with no punctuation, spaces, or numbers.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3355",
    severity=8,
)
def check_layout_valid_feature_tags(ttFont):
    """Does the font have any invalid feature tags?"""

    # We'll accept any of the OpenType specified feature tags:
    acceptable_tags = list(FEATURE_TAGS.keys())

    # And whoever is using these clearly know what they're doing:
    acceptable_tags += ["HARF", "BUZZ"]

    bad_tags = set()
    for tag in feature_tags(ttFont):
        if tag not in acceptable_tags:
            if not tag.isupper() or len(tag) > 4:
                bad_tags.add(tag)
    if bad_tags:
        yield FAIL, Message(
            "bad-feature-tags",
            "The following invalid feature tags were found in the font: "
            + ", ".join(sorted(bad_tags)),
        )
