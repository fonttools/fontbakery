from fontbakery.callable import check
from fontbakery.status import PASS, FAIL
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import


from opentypespec.tags import FEATURE_TAGS, SCRIPT_TAGS, LANGUAGE_TAGS


def feature_tags(ttFont):
    in_this_font = set()
    for table in ["GSUB", "GPOS"]:
        if ttFont.get(table) and ttFont[table].table.FeatureList:
            for fr in ttFont[table].table.FeatureList.FeatureRecord:
                in_this_font.add(fr.FeatureTag)
    return in_this_font


DEPRECATED_TAGS = ["hngl", "opbd", "size"]


@check(
    id = "com.google.fonts/check/layout_valid_feature_tags",
    rationale = """
        Incorrect tags can be indications of typos, leftover debugging code or
        questionable approaches, or user error in the font editor. Such typos can
        cause features and language support to fail to work as intended.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/3355',
    severity = 8
)
def com_google_fonts_check_layout_valid_feature_tags(ttFont):
    """Does the font have any invalid feature tags?"""

    # We'll accept any of the OpenType specified feature tags:
    acceptable_tags = list(FEATURE_TAGS.keys())

    # And whoever is using these clearly know what they're doing:
    acceptable_tags += ['HARF', 'BUZZ']

    bad_tags = set()
    for tag in feature_tags(ttFont):
        if tag not in acceptable_tags:
            bad_tags.add(tag)
    if bad_tags:
        yield FAIL, \
              Message("bad-feature-tags",
                      "The following invalid feature tags were found in the font: "
                      + ", ".join(sorted(bad_tags)))
    else:
        yield PASS, "No invalid feature tags were found"


def script_tags(ttFont):
    in_this_font = set()
    for table in ["GSUB", "GPOS"]:
        if ttFont.get(table) and ttFont[table].table.ScriptList:
            for fr in ttFont[table].table.ScriptList.ScriptRecord:
                in_this_font.add(fr.ScriptTag)
    return in_this_font


@check(
    id = "com.google.fonts/check/layout_valid_script_tags",
    rationale = """
        Incorrect script tags can be indications of typos, leftover debugging code
        or questionable approaches, or user error in the font editor. Such typos can
        cause features and language support to fail to work as intended.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/3355',
    severity = 8
)
def com_google_fonts_check_layout_valid_script_tags(ttFont):
    """Does the font have any invalid script tags?"""
    bad_tags = set()
    for tag in script_tags(ttFont):
        if tag not in SCRIPT_TAGS.keys():
            bad_tags.add(tag)
    if bad_tags:
        yield FAIL, \
              Message("bad-script-tags",
                      "The following invalid script tags were found in the font: "
                      + ", ".join(sorted(bad_tags)))
    else:
        yield PASS, "No invalid script tags were found"


def language_tags(ttFont):
    in_this_font = set()
    for table in ["GSUB", "GPOS"]:
        if ttFont.get(table) and ttFont[table].table.ScriptList:
            for fr in ttFont[table].table.ScriptList.ScriptRecord:
                for lsr in fr.Script.LangSysRecord:
                    in_this_font.add(lsr.LangSysTag)
    return in_this_font


@check(
    id = "com.google.fonts/check/layout_valid_language_tags",
    rationale = """
        Incorrect language tags can be indications of typos, leftover debugging code
        or questionable approaches, or user error in the font editor. Such typos can
        cause features and language support to fail to work as intended.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/3355',
    severity = 8
)
def com_google_fonts_check_layout_valid_language_tags(ttFont):
    """Does the font have any invalid language tags?"""
    bad_tags = set()
    for tag in language_tags(ttFont):
        if tag not in LANGUAGE_TAGS.keys():
            bad_tags.add(tag)
    if bad_tags:
        yield FAIL, \
              Message("bad-language-tags",
                      "The following invalid language tags were found in the font: "
                      + ", ".join(sorted(bad_tags)))
    else:
        yield PASS, "No invalid language tags were found"
