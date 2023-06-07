from fontbakery.callable import check, condition
from fontbakery.status import ERROR, FAIL, PASS, WARN
from fontbakery.section import Section
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory


profile = profile_factory(default_section=Section("UFO Sources"))

UFO_PROFILE_CHECKS = [
    'com.daltonmaag/check/ufolint',
    'com.daltonmaag/check/ufo_required_fields',
    'com.daltonmaag/check/ufo_recommended_fields',
    'com.daltonmaag/check/ufo_unnecessary_fields',
    'com.google.fonts/check/designspace_has_sources',
    'com.google.fonts/check/designspace_has_default_master',
    'com.google.fonts/check/designspace_has_consistent_glyphset',
    'com.google.fonts/check/designspace_has_consistent_codepoints',
]


@condition
def ufo_font(ufo):
    try:
        import defcon
        return defcon.Font(ufo)
    except Exception:
        return None


@condition
def designSpace(designspace):
    """
    Given a filepath for a designspace file, parse it
    and return a DesignSpaceDocument, which is
    'an object to read, write and edit
    interpolation systems for typefaces'.
    """
    if designspace:
        from fontTools.designspaceLib import DesignSpaceDocument
        import defcon
        DS = DesignSpaceDocument.fromfile(designspace)
        DS.loadSourceFonts(defcon.Font)
        return DS


@condition
def designspace_sources(designSpace):
    """
    Given a DesignSpaceDocument object,
    return a set of UFO font sources.
    """
    if designSpace:
        import defcon
        return designSpace.loadSourceFonts(defcon.Font)


@check(
    id = 'com.daltonmaag/check/ufolint',
    proposal = 'https://github.com/googlefonts/fontbakery/pull/1736'
)
def com_daltonmaag_check_ufolint(ufo):
    """Run ufolint on UFO source directory."""

    # IMPORTANT: This check cannot use the 'ufo_font' condition because it makes it
    # skip malformed UFOs (e.g. if metainfo.plist file is missing).

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
    id = 'com.daltonmaag/check/ufo_required_fields',
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
    id = 'com.daltonmaag/check/ufo_recommended_fields',
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
    id = 'com.daltonmaag/check/ufo_unnecessary_fields',
    conditions = ['ufo_font'],
    rationale = """
        ufo2ft will generate these.

        openTypeOS2UnicodeRanges and openTypeOS2CodePageRanges are exempted
        because it is useful to toggle a range when not _all_ the glyphs in that
        region are present.

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


@check(
    id = "com.google.fonts/check/designspace_has_sources",
    rationale = """
        This check parses a designspace file and tries to load the
        source files specified.

        This is meant to ensure that the file is not malformed,
        can be properly parsed and does include valid source file references.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/3168'
)
def com_google_fonts_check_designspace_has_sources(designspace_sources):
    """See if we can actually load the source files."""
    if not designspace_sources:
        yield FAIL,\
              Message("no-sources",
                      "Unable to load source files.")
    else:
        yield PASS, "OK"


@check(
    id = "com.google.fonts/check/designspace_has_default_master",
    rationale = """
        We expect that designspace files declare on of the masters as default.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/3168'
)
def com_google_fonts_check_designspace_has_default_master(designSpace):
    """Ensure a default master is defined."""
    if not designSpace.findDefault():
        yield FAIL,\
              Message("not-found",
                      "Unable to find a default master.")
    else:
        yield PASS, "We located a default master."


@check(
    id = "com.google.fonts/check/designspace_has_consistent_glyphset",
    rationale = """
        This check ensures that non-default masters don't have glyphs
        not present in the default one.
    """,
    conditions = ["designspace_sources"],
    proposal = 'https://github.com/googlefonts/fontbakery/pull/3168'
)
def com_google_fonts_check_designspace_has_consistent_glyphset(designSpace, config):
    """Check consistency of glyphset in a designspace file."""
    from fontbakery.utils import bullet_list

    default_glyphset = set(designSpace.findDefault().font.keys())
    failures = []
    for source in designSpace.sources:
        master_glyphset = set(source.font.keys())
        outliers = master_glyphset - default_glyphset
        if outliers:
            outliers = ", ".join(list(outliers))
            failures.append(f"Source {source.filename} has glyphs not present"
                            f" in the default master: {outliers}")
    if failures:
        yield FAIL,\
              Message("inconsistent-glyphset",
                      f"Glyphsets were not consistent:\n\n"
                      f"{bullet_list(config, failures)}")
    else:
        yield PASS, "Glyphsets were consistent."


@check(
    id = "com.google.fonts/check/designspace_has_consistent_codepoints",
    rationale = """
        This check ensures that Unicode assignments are consistent
        across all sources specified in a designspace file.
    """,
    conditions = ["designspace_sources"],
    proposal = 'https://github.com/googlefonts/fontbakery/pull/3168'
)
def com_google_fonts_check_designspace_has_consistent_codepoints(designSpace, config):
    """Check codepoints consistency in a designspace file."""
    from fontbakery.utils import bullet_list

    default_source = designSpace.findDefault()
    default_unicodes = {g.name: g.unicode for g in default_source.font}
    failures = []
    for source in designSpace.sources:
        for g in source.font:
            if g.name not in default_unicodes:
                # Previous test will cover this
                continue

            if g.unicode != default_unicodes[g.name]:
                failures.append(f"Source {source.filename} has"
                                f" {g.name}={g.unicode};"
                                f" default master has"
                                f" {g.name}={default_unicodes[g.name]}")
    if failures:
        yield FAIL,\
              Message("inconsistent-codepoints",
                      f"Unicode assignments were not consistent:\n\n"
                      f"{bullet_list(config, failures)}")
    else:
        yield PASS, "Unicode assignments were consistent."


profile.auto_register(globals())
profile.test_expected_checks(UFO_PROFILE_CHECKS, exclusive=True)
