from opentypespec.tags import LANGUAGE_TAGS

from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import language_tags


@check(
    id="opentype/layout_valid_language_tags",
    rationale="""
        Incorrect language tags can be indications of typos, leftover debugging code
        or questionable approaches, or user error in the font editor. Such typos can
        cause features and language support to fail to work as intended.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3355",
    severity=8,
)
def check_layout_valid_language_tags(ttFont):
    """Does the font have any invalid language tags?"""
    bad_tags = set()
    for tag in language_tags(ttFont):
        if tag not in LANGUAGE_TAGS.keys():
            bad_tags.add(tag)
    if bad_tags:
        yield FAIL, Message(
            "bad-language-tags",
            "The following invalid language tags were found in the font: "
            + ", ".join(sorted(bad_tags)),
        )
