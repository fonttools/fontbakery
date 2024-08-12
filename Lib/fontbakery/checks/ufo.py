import re

from fontbakery.testable import Designspace, Ufo
from fontbakery.prelude import (
    check,
    condition,
    exit_with_install_instructions,
    ERROR,
    FAIL,
    PASS,
    SKIP,
    WARN,
    Message,
)
from fontbakery import utils


@condition(Ufo)
def ufo_font(ufo):
    try:
        from fontTools.ufoLib.errors import UFOLibError
        import defcon
    except ImportError:
        exit_with_install_instructions("ufo")

    try:
        return defcon.Font(ufo.file)
    except UFOLibError:
        return None


@condition(Designspace)
def designSpace(designspace):
    """
    Given a filepath for a designspace file, parse it
    and return a DesignSpaceDocument, which is
    'an object to read, write and edit
    interpolation systems for typefaces'.
    """
    try:
        from fontTools.designspaceLib import DesignSpaceDocument
        import defcon
    except ImportError:
        exit_with_install_instructions("ufo")

    if designspace:
        DS = DesignSpaceDocument.fromfile(designspace.file)
        DS.loadSourceFonts(defcon.Font)
        return DS


@condition(Designspace)
def designspace_sources(designspace):
    """
    Given a DesignSpaceDocument object,
    return a set of UFO font sources.
    """
    try:
        import defcon
    except ImportError:
        exit_with_install_instructions("ufo")

    if designspace.designSpace:
        return designspace.designSpace.loadSourceFonts(defcon.Font)


@check(
    id="com.daltonmaag/check/ufolint",
    rationale="""
        ufolint is a tool that checks UFO source files for common issues.
        It is a good idea to run it before building a font to catch potential
        problems early in the process.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/1736",
    experimental="Since 2024/Aug/09",
)
def com_daltonmaag_check_ufolint(ufo):
    """Run ufolint on UFO source directory."""

    # IMPORTANT: This check cannot use the 'ufo_font' condition because it makes it
    # skip malformed UFOs (e.g. if metainfo.plist file is missing).

    import subprocess

    ufolint_cmd = ["ufolint", ufo.file]

    try:
        subprocess.check_output(ufolint_cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        yield FAIL, Message(
            "ufolint-fail",
            ("ufolint failed the UFO source. Output follows :" "\n\n{}\n").format(
                e.output.decode()
            ),
        )
    except OSError:
        yield ERROR, Message("ufolint-unavailable", "ufolint is not available!")
    else:
        yield PASS, "ufolint passed the UFO source."


@check(
    id="com.daltonmaag/check/ufo_required_fields",
    conditions=["ufo_font"],
    rationale="""
        ufo2ft requires these info fields to compile a font binary:
        unitsPerEm, ascender, descender, xHeight, capHeight and familyName.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/1736",
    experimental="Since 2024/Aug/09",
)
def com_daltonmaag_check_required_fields(ufo_font):
    """Check that required fields are present in the UFO fontinfo."""
    required_fields = []

    for field in [
        "unitsPerEm",
        "ascender",
        "descender",
        "xHeight",
        "capHeight",
        "familyName",
    ]:
        if ufo_font.info.__dict__.get("_" + field) is None:
            required_fields.append(field)

    if required_fields:
        yield FAIL, Message(
            "missing-required-fields", f"Required field(s) missing: {required_fields}"
        )
    else:
        yield PASS, "Required fields present."


@check(
    id="com.daltonmaag/check/ufo_recommended_fields",
    conditions=["ufo_font"],
    rationale="""
        This includes fields that should be in any production font.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/1736",
    experimental="Since 2024/Aug/09",
)
def com_daltonmaag_check_recommended_fields(ufo_font):
    """Check that recommended fields are present in the UFO fontinfo."""
    recommended_fields = []

    for field in [
        "postscriptUnderlineThickness",
        "postscriptUnderlinePosition",
        "versionMajor",
        "versionMinor",
        "styleName",
        "copyright",
        "openTypeOS2Panose",
    ]:
        if ufo_font.info.__dict__.get("_" + field) is None:
            recommended_fields.append(field)

    if recommended_fields:
        yield WARN, Message(
            "missing-recommended-fields",
            f"Recommended field(s) missing: {recommended_fields}",
        )
    else:
        yield PASS, "Recommended fields present."


@check(
    id="com.daltonmaag/check/ufo_unnecessary_fields",
    conditions=["ufo_font"],
    rationale="""
        ufo2ft will generate these.

        openTypeOS2UnicodeRanges and openTypeOS2CodePageRanges are exempted
        because it is useful to toggle a range when not _all_ the glyphs in that
        region are present.

        year is deprecated since UFO v2.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/1736",
    experimental="Since 2024/Aug/09",
)
def com_daltonmaag_check_unnecessary_fields(ufo_font):
    """Check that no unnecessary fields are present in the UFO fontinfo."""
    unnecessary_fields = []

    for field in [
        "openTypeNameUniqueID",
        "openTypeNameVersion",
        "postscriptUniqueID",
        "year",
    ]:
        if ufo_font.info.__dict__.get("_" + field) is not None:
            unnecessary_fields.append(field)

    if unnecessary_fields:
        yield WARN, Message(
            "unnecessary-fields", f"Unnecessary field(s) present: {unnecessary_fields}"
        )
    else:
        yield PASS, "Unnecessary fields omitted."


# The following fields are always generated empty by defcon:
# guidelines, postscriptBlueValues, postscriptOtherBlues,
# postscriptFamilyBlues, postscriptFamilyOtherBlues,
# postscriptStemSnapH, postscriptStemSnapV -- not sure if checking for that
# is useful.


@check(
    id="com.google.fonts/check/designspace_has_sources",
    rationale="""
        This check parses a designspace file and tries to load the
        source files specified.

        This is meant to ensure that the file is not malformed,
        can be properly parsed and does include valid source file references.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3168",
    experimental="Since 2024/Aug/09",
)
def com_google_fonts_check_designspace_has_sources(designspace_sources):
    """See if we can actually load the source files."""
    if not designspace_sources:
        yield FAIL, Message("no-sources", "Unable to load source files.")
    else:
        yield PASS, "OK"


@check(
    id="com.google.fonts/check/designspace_has_default_master",
    rationale="""
        We expect that designspace files declare on of the masters as default.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3168",
    experimental="Since 2024/Aug/09",
)
def com_google_fonts_check_designspace_has_default_master(designSpace):
    """Ensure a default master is defined."""
    if not designSpace.findDefault():
        yield FAIL, Message("not-found", "Unable to find a default master.")
    else:
        yield PASS, "We located a default master."


@check(
    id="com.google.fonts/check/designspace_has_consistent_glyphset",
    rationale="""
        This check ensures that non-default masters don't have glyphs
        not present in the default one.
    """,
    conditions=["designspace_sources"],
    proposal="https://github.com/fonttools/fontbakery/pull/3168",
    experimental="Since 2024/Aug/09",
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
            failures.append(
                f"Source {source.filename} has glyphs not present"
                f" in the default master: {outliers}"
            )
    if failures:
        yield FAIL, Message(
            "inconsistent-glyphset",
            f"Glyphsets were not consistent:\n\n" f"{bullet_list(config, failures)}",
        )
    else:
        yield PASS, "Glyphsets were consistent."


@check(
    id="com.google.fonts/check/designspace_has_consistent_codepoints",
    rationale="""
        This check ensures that Unicode assignments are consistent
        across all sources specified in a designspace file.
    """,
    conditions=["designspace_sources"],
    proposal="https://github.com/fonttools/fontbakery/pull/3168",
    experimental="Since 2024/Aug/09",
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
                failures.append(
                    f"Source {source.filename} has"
                    f" {g.name}={g.unicode};"
                    f" default master has"
                    f" {g.name}={default_unicodes[g.name]}"
                )
    if failures:
        yield FAIL, Message(
            "inconsistent-codepoints",
            f"Unicode assignments were not consistent:\n\n"
            f"{bullet_list(config, failures)}",
        )
    else:
        yield PASS, "Unicode assignments were consistent."


@check(
    id="com.thetypefounders/check/features_default_languagesystem",
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
    experimental="Since 2024/Aug/09",
)
def com_thetypefounders_check_features_default_languagesystem(ufo_font):
    """Check that languagesystem DFLT dflt is present in the features.fea file."""

    if ufo_font.features.text is None:
        yield SKIP, "No features.fea file in font."
    elif not ufo_font.features.text.strip():
        yield PASS, "Default languagesystem inserted by compiler."
    else:
        tags = re.findall(
            # pylint: disable-next=line-too-long
            r"languagesystem\s+([A-Za-z0-9\._!$%&*+:?^'|~]{1,4})\s+([A-Za-z0-9\._!$%&*+:?^'|~]{1,4})",  # noqa E501
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


@check(
    id="com.daltonmaag/check/consistent_curve_type",
    rationale="""
        This is normally an accident, and may be handled incorrectly by the
        build pipeline unless specifically configured to account for this.
    """,
    conditions=["ufo_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/4795",
    experimental="Since 2024/Jul/17",
)
def check_consistent_curve_type(config, ufo: Ufo):
    """Check that all glyphs across the source use the same curve type"""

    cubic_glyphs = []
    quadratic_glyphs = []
    mixed_glyphs = []
    for layer in ufo.ufo_font.layers:  # type: ignore
        for glyph in layer:
            point_types = set(
                point.segmentType for contour in glyph for point in contour
            )
            if "curve" in point_types and "qcurve" in point_types:
                mixed_glyphs.append(glyph.name)
            elif "curve" in point_types:
                cubic_glyphs.append(glyph.name)
            elif "qcurve" in point_types:
                quadratic_glyphs.append(glyph.name)

    if mixed_glyphs:
        yield (
            WARN,
            Message(
                "mixed-glyphs",
                f"UFO contains glyphs with mixed curves:\n\n"
                f"{utils.bullet_list(config, mixed_glyphs)}\n",
            ),
        )
    if cubic_glyphs and quadratic_glyphs:
        yield (
            WARN,
            Message(
                "both-cubic-and-quadratic",
                f"UFO contains a mix of cubic-curve glyphs"
                " and quadratic-curve glyphs\n\n"
                "Cubics:\n\n"
                f"{utils.bullet_list(config, cubic_glyphs)}\n\n"
                "Quadratics:\n\n"
                f"{utils.bullet_list(config, quadratic_glyphs)}\n",
            ),
        )
    elif not mixed_glyphs:
        yield (
            PASS,
            "All curves of all glyphs use a consistent curve type",
        )


@check(
    id="com.daltonmaag/check/no_open_corners",
    rationale="""
        This may be a requirement when creating a font that supports a roundness
        axis.
    """,
    conditions=["ufo_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/4808",
    experimental="Since 2024/Aug/09",
)
def check_no_open_corners(config, ufo):
    """Check the sources have no corners"""
    from glyphsLib.filters.eraseOpenCorners import EraseOpenCornersPen
    from fontTools.pens.basePen import NullPen

    font = ufo.ufo_font
    for layer in font.layers:
        offending_glyphs = []
        for glyph in layer:
            erase_open_corners = EraseOpenCornersPen(NullPen())
            for contour in glyph:
                contour.draw(erase_open_corners)
            if erase_open_corners.affected:
                offending_glyphs.append(glyph.name)

        if offending_glyphs:
            location_str = (
                "Default layer"
                if layer.name == font.layers.defaultLayer.name
                else layer.name
            )
            yield (
                FAIL,
                Message(
                    "open-corners-found",
                    f"{location_str} contains glyphs with open corners:\n\n"
                    f"{utils.bullet_list(config, offending_glyphs)}\n",
                ),
            )


@check(
    id="com.daltonmaag/check/designspace_has_consistent_groups",
    rationale="""
        Often designers will want kerning groups to be consistent across their
        whole Designspace, so this check helps flag if this isn't the case.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4814",
    experimental="Since 2024/Aug/12",
)
def check_designspace_has_consistent_groups(config, designSpace):
    """Confirms that all sources have the same kerning groups per Designspace."""

    default_source = designSpace.findDefault()
    reference = default_source.font.groups
    for source in designSpace.sources:
        if source is default_source:
            continue
        if source.font.groups != reference:
            yield (
                WARN,
                Message(
                    "mismatched-kerning-groups",
                    f"{source.filename} does not have the same kerning groups as default source.",
                ),
            )
