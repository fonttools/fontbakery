import os

from fontbakery.callable import check, condition
from fontbakery.callable import FontBakeryExpectedValue as ExpectedValue
from fontbakery.status import ERROR, FAIL, PASS, WARN
from fontbakery.section import Section
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory


profile = profile_factory(default_section=Section("UFO Sources"))

UFO_PROFILE_CHECKS = [
    'com.daltonmaag/check/ufolint',
    'com.daltonmaag/check/ufo-required-fields',
    'com.daltonmaag/check/ufo-recommended-fields',
    'com.daltonmaag/check/ufo-unnecessary-fields'
]

@condition
def ufo_font(ufo):
    try:
        import defcon
        return defcon.Font(ufo)
    except:
        return None

@check(
    id = 'com.daltonmaag/check/ufolint',
    proposal = 'https://github.com/googlefonts/fontbakery/pull/1736'
)
def com_daltonmaag_check_ufolint(ufo):
    """Run ufolint on UFO source directory."""
    import subprocess
    ufolint_cmd = ["ufolint", ufo]

    try:
        subprocess.check_output(ufolint_cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        yield FAIL, \
              Message("ufolint-fail",
                      ("ufolint failed the UFO source. Output follows :"
                      "\n\n{}\n").format(e.output.decode()))
    except OSError:
        yield ERROR, \
              Message("ufolint-unavailable",
                      "ufolint is not available!")
    else:
        yield PASS, "ufolint passed the UFO source."


@check(
    id = 'com.daltonmaag/check/ufo-required-fields',
    conditions = ['ufo_font'],
    rationale = """
        ufo2ft requires these info fields to compile a font binary:
        unitsPerEm, ascender, descender, xHeight, capHeight and familyName.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/1736'
)
def com_daltonmaag_check_required_fields(ufo_font):
    """Check that required fields are present in the UFO fontinfo."""
    required_fields = []

    for field in ["unitsPerEm",
                  "ascender",
                  "descender",
                  "xHeight",
                  "capHeight",
                  "familyName"]:
        if ufo_font.info.__dict__.get("_" + field) is None:
            required_fields.append(field)

    if required_fields:
        yield FAIL, \
              Message("missing-required-fields",
                      f"Required field(s) missing: {required_fields}")
    else:
        yield PASS, "Required fields present."


@check(
    id = 'com.daltonmaag/check/ufo-recommended-fields',
    conditions = ['ufo_font'],
    rationale = """
        This includes fields that should be in any production font.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/1736'
)
def com_daltonmaag_check_recommended_fields(ufo_font):
    """Check that recommended fields are present in the UFO fontinfo."""
    recommended_fields = []

    for field in ["postscriptUnderlineThickness",
                  "postscriptUnderlinePosition",
                  "versionMajor",
                  "versionMinor",
                  "styleName",
                  "copyright",
                  "openTypeOS2Panose"]:
        if ufo_font.info.__dict__.get("_" + field) is None:
            recommended_fields.append(field)

    if recommended_fields:
        yield WARN, \
              Message("missing-recommended-fields",
                      f"Recommended field(s) missing: {recommended_fields}")
    else:
        yield PASS, "Recommended fields present."


@check(
    id = 'com.daltonmaag/check/ufo-unnecessary-fields',
    conditions = ['ufo_font'],
    rationale = """
        ufo2ft will generate these.

        openTypeOS2UnicodeRanges and openTypeOS2CodePageRanges are exempted because it is useful to toggle a range when not _all_ the glyphs in that region are present.

        year is deprecated since UFO v2.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/1736'
)
def com_daltonmaag_check_unnecessary_fields(ufo_font):
    """Check that no unnecessary fields are present in the UFO fontinfo."""
    unnecessary_fields = []

    for field in ["openTypeNameUniqueID",
                  "openTypeNameVersion",
                  "postscriptUniqueID",
                  "year"]:
        if ufo_font.info.__dict__.get("_" + field) is not None:
            unnecessary_fields.append(field)

    if unnecessary_fields:
        yield WARN, \
              Message("unnecessary-fields",
                      f"Unnecessary field(s) present: {unnecessary_fields}")
    else:
        yield PASS, "Unnecessary fields omitted."


# The following fields are always generated empty by defcon:
# guidelines, postscriptBlueValues, postscriptOtherBlues,
# postscriptFamilyBlues, postscriptFamilyOtherBlues,
# postscriptStemSnapH, postscriptStemSnapV -- not sure if checking for that
# is useful.

profile.auto_register(globals())

