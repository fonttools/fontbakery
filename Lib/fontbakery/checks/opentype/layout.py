from opentypespec.tags import FEATURE_TAGS, SCRIPT_TAGS, LANGUAGE_TAGS

from fontbakery.callable import check
from fontbakery.status import FAIL
from fontbakery.message import Message


def feature_tags(ttFont):
    in_this_font = set()
    for table in ["GSUB", "GPOS"]:
        if ttFont.get(table) and ttFont[table].table.FeatureList:
            for fr in ttFont[table].table.FeatureList.FeatureRecord:
                in_this_font.add(fr.FeatureTag)
    return in_this_font


DEPRECATED_TAGS = ["hngl", "opbd", "size"]


@check(
    id="com.google.fonts/check/layout_valid_feature_tags",
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
def com_google_fonts_check_layout_valid_feature_tags(ttFont):
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


def script_tags(ttFont):
    in_this_font = set()
    for table in ["GSUB", "GPOS"]:
        if ttFont.get(table) and ttFont[table].table.ScriptList:
            for fr in ttFont[table].table.ScriptList.ScriptRecord:
                in_this_font.add(fr.ScriptTag)
    return in_this_font


@check(
    id="com.google.fonts/check/layout_valid_script_tags",
    rationale="""
        Incorrect script tags can be indications of typos, leftover debugging code
        or questionable approaches, or user error in the font editor. Such typos can
        cause features and language support to fail to work as intended.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3355",
    severity=8,
)
def com_google_fonts_check_layout_valid_script_tags(ttFont):
    """Does the font have any invalid script tags?"""
    bad_tags = set()
    for tag in script_tags(ttFont):
        if tag not in SCRIPT_TAGS.keys():
            bad_tags.add(tag)
    if bad_tags:
        yield FAIL, Message(
            "bad-script-tags",
            "The following invalid script tags were found in the font: "
            + ", ".join(sorted(bad_tags)),
        )


def language_tags(ttFont):
    in_this_font = set()
    for table in ["GSUB", "GPOS"]:
        if ttFont.get(table) and ttFont[table].table.ScriptList:
            for fr in ttFont[table].table.ScriptList.ScriptRecord:
                for lsr in fr.Script.LangSysRecord:
                    in_this_font.add(lsr.LangSysTag)
    return in_this_font


@check(
    id="com.google.fonts/check/layout_valid_language_tags",
    rationale="""
        Incorrect language tags can be indications of typos, leftover debugging code
        or questionable approaches, or user error in the font editor. Such typos can
        cause features and language support to fail to work as intended.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3355",
    severity=8,
)
def com_google_fonts_check_layout_valid_language_tags(ttFont):
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
