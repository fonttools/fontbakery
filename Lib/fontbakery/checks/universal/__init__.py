import os
from typing import List


from fontbakery.prelude import (
    check,
    disable,
    Message,
    PASS,
    FAIL,
    WARN,
    INFO,
    SKIP,
)
from fontbakery.glyphdata import desired_glyph_data
from fontbakery.checks.opentype.layout import feature_tags
from fontbakery.utils import (
    bullet_list,
    get_font_glyph_data,
    get_glyph_name,
    glyph_has_ink,
    iterate_lookup_list_with_extensions,
    pretty_print_list,
)


@check(
    id="com.google.fonts/check/name/trailing_spaces",
    proposal="https://github.com/fonttools/fontbakery/issues/2417",
    rationale="""
        This check ensures that no entries in the name table end in
        spaces; trailing spaces, particularly in font names, can be
        confusing to users. In most cases this can be fixed by
        removing trailing spaces from the metadata fields in the font
        editor.
    """,
)
def com_google_fonts_check_name_trailing_spaces(ttFont):
    """Name table records must not have trailing spaces."""
    failed = False
    for name_record in ttFont["name"].names:
        name_string = name_record.toUnicode()
        if name_string != name_string.strip():
            failed = True
            name_key = tuple(
                [
                    name_record.platformID,
                    name_record.platEncID,
                    name_record.langID,
                    name_record.nameID,
                ]
            )
            shortened_str = name_record.toUnicode()
            if len(shortened_str) > 25:
                shortened_str = shortened_str[:10] + "[...]" + shortened_str[-10:]
            yield FAIL, Message(
                "trailing-space",
                f"Name table record with key = {name_key} has trailing spaces"
                f" that must be removed: '{shortened_str}'",
            )
    if not failed:
        yield PASS, ("No trailing spaces on name table entries.")


@check(
    id="com.google.fonts/check/family/single_directory",
    rationale="""
        If the set of font files passed in the command line is not all in the
        same directory, then we warn the user since the tool will interpret the
        set of files as belonging to a single family (and it is unlikely that
        the user would store the files from a single family spreaded
        in several separate directories).
    """,
    proposal="legacy:check/002",
)
def com_google_fonts_check_family_single_directory(fonts):
    """Checking all files are in the same directory."""

    directories = []
    for font in fonts:
        directory = os.path.dirname(font.file)
        if directory not in directories:
            directories.append(directory)

    if len(directories) == 1:
        yield PASS, "All files are in the same directory."
    else:
        yield FAIL, Message(
            "single-directory",
            "Not all fonts passed in the command line are in the"
            " same directory. This may lead to bad results as the tool"
            " will interpret all font files as belonging to a single"
            f" font family. The detected directories are: {directories}",
        )


@disable
@check(
    id="com.google.fonts/check/caps_vertically_centered",
    rationale="""
        This check suggests one possible approach to designing vertical metrics,
        but can be ingnored if you follow a different approach.
        In order to center text in buttons, lists, and grid systems
        with minimal additional CSS work, the uppercase glyphs should be
        vertically centered in the em box.
        This check mainly applies to Latin, Greek, Cyrillic, and other similar scripts.
        For non-latin scripts like Arabic, this check might not be applicable.
        There is a detailed description of this subject at:
        https://x.com/romanshamin_en/status/1562801657691672576
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4139",
)
def com_google_fonts_check_caps_vertically_centered(ttFont):
    """Check if uppercase glyphs are vertically centered."""
    from fontTools.pens.boundsPen import BoundsPen

    SOME_UPPERCASE_GLYPHS = ["A", "B", "C", "D", "E", "H", "I", "M", "O", "S", "T", "X"]
    glyphSet = ttFont.getGlyphSet()

    for glyphname in SOME_UPPERCASE_GLYPHS:
        if glyphname not in glyphSet.keys():
            yield SKIP, Message(
                "lacks-ascii",
                "The implementation of this check relies on a few samples"
                " of uppercase latin characteres that are not available in this font.",
            )
            return

    highest_point_list = []
    for glyphName in SOME_UPPERCASE_GLYPHS:
        pen = BoundsPen(glyphSet)
        glyphSet[glyphName].draw(pen)
        highest_point = pen.bounds[3]
        highest_point_list.append(highest_point)

    upm = ttFont["head"].unitsPerEm
    error_margin = upm * 0.05
    average_cap_height = sum(highest_point_list) / len(highest_point_list)
    descender = ttFont["hhea"].descent
    top_margin = upm - average_cap_height
    difference = abs(top_margin - abs(descender))
    vertically_centered = difference <= error_margin

    if not vertically_centered:
        yield WARN, Message(
            "vertical-metrics-not-centered",
            "Uppercase glyphs are not vertically centered in the em box.",
        )
    else:
        yield PASS, "Uppercase glyphs are vertically centered in the em box."


@check(
    id="com.google.fonts/check/whitespace_ink",
    proposal="legacy:check/049",
    rationale="""
           This check ensures that certain whitespace glyphs are empty.
           Certain text layout engines will assume that these glyphs are empty,
           and will not draw them; if they were in fact not designed to be
           empty, the result will be text layout that is not as expected.
       """,
)
def com_google_fonts_check_whitespace_ink(ttFont):
    """Whitespace glyphs have ink?"""
    # This checks that certain glyphs are empty.
    # Some, but not all, are Unicode whitespace.

    # code-points for all Unicode whitespace chars
    # (according to Unicode 11.0 property list):
    WHITESPACE_CHARACTERS = {
        0x0009,
        0x000A,
        0x000B,
        0x000C,
        0x000D,
        0x0020,
        0x0085,
        0x00A0,
        0x1680,
        0x2000,
        0x2001,
        0x2002,
        0x2003,
        0x2004,
        0x2005,
        0x2006,
        0x2007,
        0x2008,
        0x2009,
        0x200A,
        0x2028,
        0x2029,
        0x202F,
        0x205F,
        0x3000,
    }

    # Code-points that do not have whitespace property, but
    # should not have a drawing.
    EXTRA_NON_DRAWING = {0x180E, 0x200B, 0x2060, 0xFEFF}

    # Make the set of non drawing characters.
    # OGHAM SPACE MARK U+1680 is removed as it is
    # a whitespace that should have a drawing.
    NON_DRAWING = (WHITESPACE_CHARACTERS | EXTRA_NON_DRAWING) - {0x1680}

    passed = True
    for codepoint in sorted(NON_DRAWING):
        g = get_glyph_name(ttFont, codepoint)
        if g is not None and glyph_has_ink(ttFont, g):
            passed = False
            yield FAIL, Message(
                "has-ink",
                f"Glyph '{g}' has ink. It needs to be replaced by an empty glyph.",
            )
    if passed:
        yield PASS, "There is no whitespace glyph with ink."


@check(
    id="com.google.fonts/check/legacy_accents",
    proposal=[
        "https://github.com/googlefonts/fontbakery/issues/4310",
    ],
    rationale="""
        Legacy accents should not have anchors and should have positive width.
        They are often used independently of a letter, either as a placeholder
        for an expected combined mark+letter combination in MacOS, or separately.
        For instance, U+00B4 (ACUTE ACCENT) is often mistakenly used as an apostrophe,
        U+0060 (GRAVE ACCENT) is used in Markdown to notify code blocks,
        and ^ is used as an exponential operator in maths.
    """,
)
def com_google_fonts_check_legacy_accents(ttFont):
    """Check that legacy accents aren't used in composite glyphs."""

    # code-points for all legacy chars
    LEGACY_ACCENTS = {
        0x00A8,  # DIAERESIS
        0x02D9,  # DOT ABOVE
        0x0060,  # GRAVE ACCENT
        0x00B4,  # ACUTE ACCENT
        0x02DD,  # DOUBLE ACUTE ACCENT
        0x02C6,  # MODIFIER LETTER CIRCUMFLEX ACCENT
        0x02C7,  # CARON
        0x02D8,  # BREVE
        0x02DA,  # RING ABOVE
        0x02DC,  # SMALL TILDE
        0x00AF,  # MACRON
        0x00B8,  # CEDILLA
        0x02DB,  # OGONEK
    }

    passed = True

    reverseCmap = ttFont["cmap"].buildReversed()
    hmtx = ttFont["hmtx"]

    # Check whether legacy accents have positive width.
    for name in reverseCmap:
        if reverseCmap[name].intersection(LEGACY_ACCENTS):
            if hmtx[name][0] == 0:
                passed = False
                yield FAIL, Message(
                    "legacy-accents-width",
                    f'Width of legacy accent "{name}" is zero; should be positive.',
                )

    # Check whether legacy accents appear in GDEF as marks.
    # Not being marks in GDEF also typically means that they don't have anchors,
    # as font compilers would have otherwise classified them as marks in GDEF.
    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        class_def = ttFont["GDEF"].table.GlyphClassDef.classDefs
        for name in reverseCmap:
            if reverseCmap[name].intersection(LEGACY_ACCENTS):
                if name in class_def and class_def[name] == 3:
                    passed = False
                    yield FAIL, Message(
                        "legacy-accents-gdef",
                        f'Legacy accent "{name}" is defined in GDEF'
                        f" as a mark (class 3).",
                    )

    if passed:
        yield PASS, "Looks good!"


@check(
    id="com.google.fonts/check/contour_count",
    conditions=["is_ttf", "not is_variable_font"],
    rationale="""
        Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only
        be constructured in a handful of ways. This means a glyph's contour count
        will only differ slightly amongst different fonts, e.g a 'g' could either
        be 2 or 3 contours, depending on whether its double story or single story.

        However, a quotedbl should have 2 contours, unless the font belongs
        to a display family.

        This check currently does not cover variable fonts because there's plenty
        of alternative ways of constructing glyphs with multiple outlines for each
        feature in a VarFont. The expected contour count data for this check is
        currently optimized for the typical construction of glyphs in static fonts.
    """,
    proposal="legacy:check/153",
)
def com_google_fonts_check_contour_count(ttFont, config):
    """Check if each glyph has the recommended amount of contours.

    This check is useful to assure glyphs aren't incorrectly constructed.

    The desired_glyph_data module contains the 'recommended' countour count
    for encoded glyphs. The contour counts are derived from fonts which were
    chosen for their quality and unique design decisions for particular glyphs.

    In the future, additional glyph data can be included. A good addition would
    be the 'recommended' anchor counts for each glyph.
    """

    def in_PUA_range(codepoint):
        """
        In Unicode, a Private Use Area (PUA) is a range of code points that,
        by definition, will not be assigned characters by the Unicode Consortium.
        Three private use areas are defined:
          one in the Basic Multilingual Plane (U+E000–U+F8FF),
          and one each in, and nearly covering, planes 15 and 16
          (U+F0000–U+FFFFD, U+100000–U+10FFFD).
        """
        return (
            (codepoint >= 0xE000 and codepoint <= 0xF8FF)
            or (codepoint >= 0xF0000 and codepoint <= 0xFFFFD)
            or (codepoint >= 0x100000 and codepoint <= 0x10FFFD)
        )

    # rearrange data structure:
    desired_glyph_data_by_codepoint = {}
    desired_glyph_data_by_glyphname = {}
    for glyph in desired_glyph_data:
        desired_glyph_data_by_glyphname[glyph["name"]] = glyph
        # since the glyph in PUA ranges have unspecified meaning,
        # it doesnt make sense for us to have an expected contour cont for them
        if not in_PUA_range(glyph["unicode"]):
            desired_glyph_data_by_codepoint[glyph["unicode"]] = glyph

    bad_glyphs = []
    desired_glyph_contours_by_codepoint = {
        f: desired_glyph_data_by_codepoint[f]["contours"]
        for f in desired_glyph_data_by_codepoint
    }
    desired_glyph_contours_by_glyphname = {
        f: desired_glyph_data_by_glyphname[f]["contours"]
        for f in desired_glyph_data_by_glyphname
    }

    font_glyph_data = get_font_glyph_data(ttFont)

    if font_glyph_data is None:
        yield FAIL, Message("lacks-cmap", "This font lacks cmap data.")
    else:
        font_glyph_contours_by_codepoint = {
            f["unicode"]: list(f["contours"])[0] for f in font_glyph_data
        }
        font_glyph_contours_by_glyphname = {
            f["name"]: list(f["contours"])[0] for f in font_glyph_data
        }

        shared_glyphs_by_codepoint = set(desired_glyph_contours_by_codepoint) & set(
            font_glyph_contours_by_codepoint
        )
        for glyph in sorted(shared_glyphs_by_codepoint):
            if (
                font_glyph_contours_by_codepoint[glyph]
                not in desired_glyph_contours_by_codepoint[glyph]
            ):
                bad_glyphs.append(
                    [
                        glyph,
                        font_glyph_contours_by_codepoint[glyph],
                        desired_glyph_contours_by_codepoint[glyph],
                    ]
                )

        shared_glyphs_by_glyphname = set(desired_glyph_contours_by_glyphname) & set(
            font_glyph_contours_by_glyphname
        )
        for glyph in sorted(shared_glyphs_by_glyphname):
            if (
                font_glyph_contours_by_glyphname[glyph]
                not in desired_glyph_contours_by_glyphname[glyph]
            ):
                bad_glyphs.append(
                    [
                        glyph,
                        font_glyph_contours_by_glyphname[glyph],
                        desired_glyph_contours_by_glyphname[glyph],
                    ]
                )

        if len(bad_glyphs) > 0:
            cmap = ttFont.getBestCmap()

            def _glyph_name(cmap, name):
                if name in cmap:
                    return cmap[name]
                else:
                    return name

            bad_glyphs_message = []
            zero_contours_message = []

            for name, count, expected in bad_glyphs:
                if count == 0:
                    zero_contours_message.append(
                        f"Glyph name: {_glyph_name(cmap, name)}\t"
                        f"Expected: {pretty_print_list(config, expected, glue=' or ')}"
                    )
                else:
                    bad_glyphs_message.append(
                        f"Glyph name: {_glyph_name(cmap, name)}\t"
                        f"Contours detected: {count}\t"
                        f"Expected: {pretty_print_list(config, expected, glue=' or ')}"
                    )

            if bad_glyphs_message:
                bad_glyphs_message = bullet_list(config, bad_glyphs_message)
                yield WARN, Message(
                    "contour-count",
                    "This check inspects the glyph outlines and detects the total"
                    " number of contours in each of them. The expected values are"
                    " infered from the typical ammounts of contours observed in a"
                    " large collection of reference font families. The divergences"
                    " listed below may simply indicate a significantly different"
                    " design on some of your glyphs. On the other hand, some of these"
                    " may flag actual bugs in the font such as glyphs mapped to an"
                    " incorrect codepoint. Please consider reviewing the design and"
                    " codepoint assignment of these to make sure they are correct.\n\n"
                    "The following glyphs do not have the recommended number of"
                    f" contours:\n\n{bad_glyphs_message}\n",
                )

            if zero_contours_message:
                zero_contours_message = bullet_list(config, zero_contours_message)
                yield FAIL, Message(
                    "no-contour",
                    "The following glyphs have no contours even though they were"
                    f" expected to have some:\n\n{zero_contours_message}\n",
                )
        else:
            yield PASS, "All glyphs have the recommended amount of contours"


@check(
    id="com.google.fonts/check/cjk_chws_feature",
    conditions=["is_cjk_font"],
    rationale="""
        The W3C recommends the addition of chws and vchw features to CJK fonts
        to enhance the spacing of glyphs in environments which do not fully support
        JLREQ layout rules.

        The chws_tool utility (https://github.com/googlefonts/chws_tool) can be used
        to add these features automatically.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3363",
)
def com_google_fonts_check_cjk_chws_feature(ttFont):
    """Does the font contain chws and vchw features?"""
    passed = True
    tags = feature_tags(ttFont)
    FEATURE_NOT_FOUND = (
        "{} feature not found in font."
        " Use chws_tool (https://github.com/googlefonts/chws_tool)"
        " to add it."
    )
    if "chws" not in tags:
        passed = False
        yield WARN, Message("missing-chws-feature", FEATURE_NOT_FOUND.format("chws"))
    if "vchw" not in tags:
        passed = False
        yield WARN, Message("missing-vchw-feature", FEATURE_NOT_FOUND.format("vchw"))
    if passed:
        yield PASS, "Font contains chws and vchw features"


@check(
    id="com.google.fonts/check/transformed_components",
    conditions=["is_ttf"],
    rationale="""
        Some families have glyphs which have been constructed by using
        transformed components e.g the 'u' being constructed from a flipped 'n'.

        From a designers point of view, this sounds like a win (less work).
        However, such approaches can lead to rasterization issues, such as
        having the 'u' not sitting on the baseline at certain sizes after
        running the font through ttfautohint.

        Other issues are outlines that end up reversed when only one dimension
        is flipped while the other isn't.

        As of July 2019, Marc Foley observed that ttfautohint assigns cvt values
        to transformed glyphs as if they are not transformed and the result is
        they render very badly, and that vttLib does not support flipped components.

        When building the font with fontmake, the problem can be fixed by adding
        this to the command line:

        --filter DecomposeTransformedComponentsFilter
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2011",
)
def com_google_fonts_check_transformed_components(ttFont, is_hinted):
    """Ensure component transforms do not perform scaling or rotation."""
    failures = ""
    for glyph_name in ttFont.getGlyphOrder():
        glyf = ttFont["glyf"][glyph_name]
        if not glyf.isComposite():
            continue
        for component in glyf.components:
            comp_name, transform = component.getComponentInfo()

            # Font is hinted, complain about *any* transformations
            if is_hinted:
                if transform[0:4] != (1, 0, 0, 1):
                    failures += f"* {glyph_name} (component {comp_name})\n"
            # Font is unhinted, complain only about transformations where
            # only one dimension is flipped while the other isn't.
            # Otherwise the outline direction is intact and since the font is unhinted,
            # no rendering problems are to be expected
            else:
                if transform[0] * transform[3] < 0:
                    failures += f"* {glyph_name} (component {comp_name})\n"

    if failures:
        yield FAIL, Message(
            "transformed-components",
            "The following glyphs had components with scaling or rotation\n"
            f"or inverted outline direction:\n\n{failures}",
        )
    else:
        yield PASS, "No glyphs had components with scaling or rotation"


@check(
    id="com.google.fonts/check/gpos7",
    conditions=["ttFont"],
    severity=9,
    rationale="""
        Versions of fonttools >=4.14.0 (19 August 2020) perform an optimisation on
        chained contextual lookups, expressing GSUB6 as GSUB5 and GPOS8 and GPOS7
        where possible (when there are no suffixes/prefixes for all rules in
        the lookup).

        However, makeotf has never generated these lookup types and they are rare
        in practice. Perhaps because of this, Mac's CoreText shaper does not correctly
        interpret GPOS7, meaning that these lookups will be ignored by the shaper,
        and fonts containing these lookups will have unintended positioning errors.

        To fix this warning, rebuild the font with a recent version of fonttools.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3643",
)
def com_google_fonts_check_gpos7(ttFont):
    """Ensure no GPOS7 lookups are present."""
    has_gpos7 = False

    def find_gpos7(lookup):
        nonlocal has_gpos7
        if lookup.LookupType == 7:
            has_gpos7 = True

    iterate_lookup_list_with_extensions(ttFont, "GPOS", find_gpos7)

    if not has_gpos7:
        yield PASS, "Font has no GPOS7 lookups"
        return

    yield WARN, Message(
        "has-gpos7", "Font contains a GPOS7 lookup which is not processed by macOS"
    )


@check(
    id="com.adobe.fonts/check/freetype_rasterizer",
    conditions=["ttFont"],
    severity=10,
    rationale="""
        Malformed fonts can cause FreeType to crash.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3642",
)
def com_adobe_fonts_check_freetype_rasterizer(font):
    """Ensure that the font can be rasterized by FreeType."""
    import freetype
    from freetype.ft_errors import FT_Exception

    try:
        face = freetype.Face(font.file)
        face.set_char_size(48 * 64)
        face.load_char("✅")  # any character can be used here

    except FT_Exception as err:
        yield FAIL, Message(
            "freetype-crash", f"Font caused FreeType to crash with this error: {err}"
        )
    else:
        yield PASS, "Font can be rasterized by FreeType."


@check(
    id="com.adobe.fonts/check/sfnt_version",
    severity=10,
    rationale="""
        OpenType fonts that contain TrueType outlines should use the value of 0x00010000
        for the sfntVersion. OpenType fonts containing CFF data (version 1 or 2) should
        use 0x4F54544F ('OTTO', when re-interpreted as a Tag) for sfntVersion.

        Fonts with the wrong sfntVersion value are rejected by FreeType.

        https://docs.microsoft.com/en-us/typography/opentype/spec/otff#table-directory
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3388",
)
def com_adobe_fonts_check_sfnt_version(ttFont, is_ttf, is_cff, is_cff2):
    """Font has the proper sfntVersion value?"""
    sfnt_version = ttFont.sfntVersion

    if is_ttf and sfnt_version != "\x00\x01\x00\x00":
        yield FAIL, Message(
            "wrong-sfnt-version-ttf",
            "Font with TrueType outlines has incorrect sfntVersion value:"
            f" '{sfnt_version}'",
        )

    elif (is_cff or is_cff2) and sfnt_version != "OTTO":
        yield FAIL, Message(
            "wrong-sfnt-version-cff",
            f"Font with CFF data has incorrect sfntVersion value: '{sfnt_version}'",
        )

    else:
        yield PASS, "Font has the correct sfntVersion value."


@check(
    id="com.google.fonts/check/whitespace_widths",
    conditions=["not missing_whitespace_chars"],
    rationale="""
        If the space and nbspace glyphs have different widths, then Google Workspace
        has problems with the font.

        The nbspace is used to replace the space character in multiple situations in
        documents; such as the space before punctuation in languages that do that. It
        avoids the punctuation to be separated from the last word and go to next line.

        This is automatic substitution by the text editors, not by fonts. It's also used
        by designers in text composition practice to create nicely shaped paragraphs.
        If the space and the nbspace are not the same width, it breaks the text
        composition of documents.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/3843",
        "legacy:check/050",
    ],
)
def com_google_fonts_check_whitespace_widths(ttFont):
    """Space and non-breaking space have the same width?"""
    space_name = get_glyph_name(ttFont, 0x0020)
    nbsp_name = get_glyph_name(ttFont, 0x00A0)

    space_width = ttFont["hmtx"][space_name][0]
    nbsp_width = ttFont["hmtx"][nbsp_name][0]

    if space_width > 0 and space_width == nbsp_width:
        yield PASS, "Space and non-breaking space have the same width."
    else:
        yield FAIL, Message(
            "different-widths",
            "Space and non-breaking space have differing width:"
            f" The space glyph named {space_name} is {space_width} font units wide,"
            f" non-breaking space named ({nbsp_name}) is {nbsp_width} font units wide,"
            ' and both should be positive and the same. GlyphsApp has "Sidebearing'
            ' arithmetic" (https://glyphsapp.com/tutorials/spacing) which allows you to'
            " set the non-breaking space width to always equal the space width.",
        )


@check(
    id="com.google.fonts/check/interpolation_issues",
    conditions=["is_variable_font", "is_ttf"],
    severity=4,
    rationale="""
        When creating a variable font, the designer must make sure that corresponding
        paths have the same start points across masters, as well as that corresponding
        component shapes are placed in the same order within a glyph across masters.
        If this is not done, the glyph will not interpolate correctly.

        Here we check for the presence of potential interpolation errors using the
        fontTools.varLib.interpolatable module.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3930",
)
def com_google_fonts_check_interpolation_issues(ttFont, config):
    """Detect any interpolation issues in the font."""
    from fontTools.varLib.interpolatable import test as interpolation_test
    from fontTools.varLib.interpolatableHelpers import InterpolatableProblem
    from fontTools.varLib.models import piecewiseLinearMap

    gvar = ttFont["gvar"]
    # This code copied from fontTools.varLib.interpolatable
    locs = set()
    for variations in gvar.variations.values():
        for var in variations:
            loc = []
            for tag, val in sorted(var.axes.items()):
                loc.append((tag, val[1]))
            locs.add(tuple(loc))

    # Rebuild locs as dictionaries
    new_locs = [{}]
    for loc in sorted(locs, key=lambda v: (len(v), v)):
        location = {}
        for tag, val in loc:
            location[tag] = val
        new_locs.append(location)

    axis_maps = {
        ax.axisTag: {-1: ax.minValue, 0: ax.defaultValue, 1: ax.maxValue}
        for ax in ttFont["fvar"].axes
    }

    locs = new_locs
    glyphsets = [ttFont.getGlyphSet(location=loc, normalized=True) for loc in locs]

    # Name glyphsets by their full location. Different versions of fonttools
    # have differently-typed default names, and so this optional argument must
    # be provided to ensure that returned names are always strings.
    # See: https://github.com/fonttools/fontbakery/issues/4356
    names: List[str] = []
    for glyphset in glyphsets:
        full_location: List[str] = []
        for ax in ttFont["fvar"].axes:
            normalized = glyphset.location.get(ax.axisTag, 0)
            denormalized = int(piecewiseLinearMap(normalized, axis_maps[ax.axisTag]))
            full_location.append(f"{ax.axisTag}={denormalized}")
        names.append(",".join(full_location))

    # Inputs are ready; run the tests.
    results = interpolation_test(glyphsets, names=names)

    # Most of the potential problems varLib.interpolatable finds can't
    # exist in a built binary variable font. We focus on those which can.
    report = []
    for glyph, glyph_problems in results.items():
        for p in glyph_problems:
            if p["type"] == InterpolatableProblem.CONTOUR_ORDER:
                report.append(
                    f"Contour order differs in glyph '{glyph}':"
                    f" {p['value_1']} in {p['master_1']},"
                    f" {p['value_2']} in {p['master_2']}."
                )
            elif p["type"] == InterpolatableProblem.WRONG_START_POINT:
                report.append(
                    f"Contour {p['contour']} start point"
                    f" differs in glyph '{glyph}' between"
                    f" location {p['master_1']} and"
                    f" location {p['master_2']}"
                )
            elif p["type"] == InterpolatableProblem.KINK:
                report.append(
                    f"Contour {p['contour']} point {p['value']} in glyph '{glyph}' "
                    f"has a kink between location {p['master_1']} and"
                    f" location {p['master_2']}"
                )
            elif p["type"] == InterpolatableProblem.UNDERWEIGHT:
                report.append(
                    f"Contour {p['contour']} in glyph '{glyph}':"
                    f" becomes underweight between {p['master_1']}"
                    f" and {p['master_2']}."
                )
            elif p["type"] == InterpolatableProblem.OVERWEIGHT:
                report.append(
                    f"Contour {p['contour']} in glyph '{glyph}':"
                    f" becomes overweight between {p['master_1']}"
                    f" and {p['master_2']}."
                )

    if not report:
        yield PASS, "No interpolation issues found"
    else:
        yield WARN, Message(
            "interpolation-issues",
            f"Interpolation issues were found in the font:\n\n"
            f"{bullet_list(config, report)}",
        )


@check(
    id="com.google.fonts/check/math_signs_width",
    rationale="""
        It is a common practice to have math signs sharing the same width
        (preferably the same width as tabular figures accross the entire font family).

        This probably comes from the will to avoid additional tabular math signs
        knowing that their design can easily share the same width.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3832",
)
def com_google_fonts_check_math_signs_width(ttFont):
    """Check math signs have the same width."""
    # Ironically, the block of text below may not have
    # uniform widths for these glyphs depending on
    # which font your text editor is using while you
    # read the source code of this check:
    COMMON_WIDTH_MATH_GLYPHS = (
        "+ < = > ¬ ± × ÷ ∈ ∉ ∋ ∌ − ∓ ∔ ∝ ∟ ∠ ∡ ∢ ∷ ∸ ∹ ∺ ∻ "
        "∼ ∽ ∾ ∿ ≁ ≂ ≃ ≄ ≅ ≆ ≇ ≈ ≉ ≊ ≋ ≌ ≍ ≎ ≏ ≐ ≑ ≒ ≓ ≖ ≗ "
        "≘ ≙ ≚ ≛ ≜ ≝ ≞ ≟ ≠ ≡ ≢ ≣ ≤ ≥ ≦ ≧ ≨ ≩ ≭ ≮ ≯ ≰ ≱ ≲ ≳ "
        "≴ ≵ ≶ ≷ ≸ ≹ ≺ ≻ ≼ ≽ ≾ ≿ ⊀ ⊁ ⊂ ⊃ ⊄ ⊅ ⊆ ⊇ ⊈ ⊉ ⊊ ⊋ ⊏ "
        "⊐ ⊑ ⊒ ⊢ ⊣ ⊤ ⊥ ⊨ ⊰ ⊱ ⊲ ⊳ ⊴ ⊵ ⊹ ⊾ ⋇ ⋍ ⋐ ⋑ ⋕ ⋖ ⋗ ⋚ ⋛ "
        "⋜ ⋝ ⋞ ⋟ ⋠ ⋡ ⋢ ⋣ ⋤ ⋥ ⋦ ⋧ ⋨ ⋩ ⋳ ⋵ ⋶ ⋸ ⋹ ⋻ ⋽ ⟀ ⟃ ⟄ ⟓ "
        "⟔ ⥶ ⥸ ⥹ ⥻ ⥾ ⥿ ⦓ ⦔ ⦕ ⦖ ⦛ ⦜ ⦝ ⦞ ⦟ ⦠ ⦡ ⦢ ⦣ ⦤ ⦥ ⦨ ⦩ ⦪ "
        "⦫ ⧣ ⧤ ⧥ ⧺ ⧻ ⨢ ⨣ ⨤ ⨥ ⨦ ⨧ ⨨ ⨩ ⨪ ⨫ ⨬ ⨳ ⩦ ⩧ ⩨ ⩩ ⩪ ⩫ ⩬ "
        "⩭ ⩮ ⩯ ⩰ ⩱ ⩲ ⩳ ⩷ ⩸ ⩹ ⩺ ⩻ ⩼ ⩽ ⩾ ⩿ ⪀ ⪁ ⪂ ⪃ ⪄ ⪅ ⪆ ⪇ ⪈ "
        "⪉ ⪊ ⪋ ⪌ ⪍ ⪎ ⪏ ⪐ ⪑ ⪒ ⪓ ⪔ ⪕ ⪖ ⪗ ⪘ ⪙ ⪚ ⪛ ⪜ ⪝ ⪞ ⪟ ⪠ ⪡ "
        "⪢ ⪦ ⪧ ⪨ ⪩ ⪪ ⪫ ⪬ ⪭ ⪮ ⪯ ⪰ ⪱ ⪲ ⪳ ⪴ ⪵ ⪶ ⪷ ⪸ ⪹ ⪺ ⪽ ⪾ ⪿ "
        "⫀ ⫁ ⫂ ⫃ ⫄ ⫅ ⫆ ⫇ ⫈ ⫉ ⫊ ⫋ ⫌ ⫏ ⫐ ⫑ ⫒ ⫓ ⫔ ⫕ ⫖ ⫟ ⫠ ⫡ ⫢ "
        "⫤ ⫦ ⫧ ⫨ ⫩ ⫪ ⫫ ⫳ ⫴ ⫵ ⫶ ⫹ ⫺ 〒"
    )

    glyphs_by_width = {}
    for glyph in COMMON_WIDTH_MATH_GLYPHS.split(" "):
        codepoint = ord(glyph)
        glyph_name = get_glyph_name(ttFont, codepoint)
        if glyph_name is None:
            # The font does not have this glyph, so move on...
            continue
        glyph_width = ttFont["hmtx"][glyph_name][0]
        if glyph_width not in glyphs_by_width:
            glyphs_by_width[glyph_width] = set([glyph_name])
        else:
            glyphs_by_width[glyph_width].add(glyph_name)

    most_common_width = None
    num_glyphs = 0
    for glyph_width, glyph_names in glyphs_by_width.items():
        if most_common_width is None:
            num_glyphs = len(glyph_names)
            most_common_width = glyph_width
        else:
            if len(glyph_names) > num_glyphs:
                most_common_width = glyph_width
                num_glyphs = len(glyph_names)

    if most_common_width and len(glyphs_by_width.keys()) > 1:
        outliers_summary = []
        for w, names in glyphs_by_width.items():
            if not w == most_common_width:
                outliers_summary.append(f"Width = {w}:\n{', '.join(names)}\n")
        outliers_summary = "\n".join(outliers_summary)
        yield WARN, Message(
            "width-outliers",
            f"The most common width is {most_common_width} among a set of {num_glyphs}"
            " math glyphs.\nThe following math glyphs have a different width, though:"
            f"\n\n{outliers_summary}",
        )
    else:
        yield PASS, "Looks good."


@check(
    id="com.google.fonts/check/tabular_kerning",
    rationale="""
        Tabular glyphs should not have kerning, as they are meant to be used in tables.

        This check looks for kerning in:
        - all glyphs in a font in combination with tabular numerals;
        - tabular symbols in combination with tabular numerals.

        "Tabular symbols" is defined as:
        - for fonts with a "tnum" feature, all "tnum" substitution target glyphs;
        - for fonts without a "tnum" feature, all glyphs that have the same width
        as the tabular numerals, but limited to numbers, math and currency symbols.

        This check may produce false positives for fonts with no "tnum" feature
        and with equal-width numerals (and other same-width symbols) that are
        not intended to be used as tabular numerals.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4440",
    experimental="Since 2024/Jun/04",
)
def com_google_fonts_check_tabular_kerning(ttFont):
    """Check tabular widths don't have kerning."""
    from vharfbuzz import Vharfbuzz
    import uharfbuzz as hb
    import unicodedata

    EXCLUDE = [
        "\u0600",  # Arabic
        "\u0601",  # Arabic
        "\u0602",  # Arabic
        "\u0603",  # Arabic
        "\u0604",  # Arabic
        "\u06DD",  # Arabic
        "\u0890",  # Arabic
        "\u0891",  # Arabic
        "\u0605",  # Arabic
        "\u08E2",  # Arabic
        "\u2044",  # General Punctuation
        "\u2215",  # Mathematical Operators
    ]
    IGNORE_GLYPHS = [
        ".notdef",
        "NULL",
    ]
    GID_OFFSET = 0xF0000

    vhb = Vharfbuzz(ttFont.reader.file.name)
    best_cmap = ttFont.getBestCmap()
    unicode_for_glyphs = {v: k for k, v in best_cmap.items()}

    def nominal_glyph_func(font, code_point, data):
        if code_point > GID_OFFSET:
            return code_point - GID_OFFSET
        return 0

    funcs = hb.FontFuncs.create()
    funcs.set_nominal_glyph_func(nominal_glyph_func)
    vhb.hbfont.funcs = funcs

    def glyph_width(ttFont, glyph_name):
        return ttFont["hmtx"].metrics[glyph_name][0]

    def glyph_name_for_character(_ttFont, character):
        return best_cmap.get(ord(character))

    def unique_combinations(list_1, list_2):
        unique_combinations = []

        for i in range(len(list_1)):
            for j in range(len(list_2)):
                unique_combinations.append((list_1[i], list_2[j]))

        return unique_combinations

    def has_feature(ttFont, featureTag):
        if "GSUB" in ttFont and ttFont["GSUB"].table.FeatureList:
            for FeatureRecord in ttFont["GSUB"].table.FeatureList.FeatureRecord:
                if FeatureRecord.FeatureTag == featureTag:
                    return True
        if "GPOS" in ttFont and ttFont["GPOS"].table.FeatureList:
            for FeatureRecord in ttFont["GPOS"].table.FeatureList.FeatureRecord:
                if FeatureRecord.FeatureTag == featureTag:
                    return True
        return False

    def buf_to_width(buf):
        x_cursor = 0

        for _info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            x_cursor += pos.x_advance

        return x_cursor

    def glyph_name_to_gid(ttFont, glyph_name):
        if glyph_name.startswith("gid"):
            gid = int(glyph_name[3:])
            return gid
        return ttFont.getGlyphID(glyph_name)

    def get_substitutions(
        ttFont,
        featureTag,
        lookupType=1,
    ):
        substitutions = {}
        if "GSUB" in ttFont:
            for FeatureRecord in ttFont["GSUB"].table.FeatureList.FeatureRecord:
                if FeatureRecord.FeatureTag == featureTag:
                    for LookupIndex in FeatureRecord.Feature.LookupListIndex:
                        for SubTable in (
                            ttFont["GSUB"].table.LookupList.Lookup[LookupIndex].SubTable
                        ):
                            if SubTable.LookupType == lookupType:
                                substitutions.update(SubTable.mapping)
        return substitutions

    def get_kerning(glyph_list):
        # Either glyph is in EXCLUDED
        # Also stripping .ss01, .ss02, etc
        unicodes = [
            chr(unicode_for_glyphs[x])
            for x in [y.split(".")[0] for y in glyph_list]
            if x in unicode_for_glyphs
        ]
        excluded = set(EXCLUDE) & set(unicodes)
        if excluded:
            return 0

        glyph_list = [
            chr(GID_OFFSET + glyph_name_to_gid(ttFont, glyph_name))
            for glyph_name in glyph_list
        ]

        # Either glyph is .notdef
        if chr(GID_OFFSET) in glyph_list:
            return 0

        text = "".join(glyph_list)
        width1 = buf_to_width(vhb.shape(text, {"features": {"kern": True}}))
        width2 = buf_to_width(vhb.shape(text, {"features": {"kern": False}}))
        return width1 - width2

    def get_str_buffer(glyph_list):
        glyph_list = [
            chr(GID_OFFSET + glyph_name_to_gid(ttFont, glyph_name))
            for glyph_name in glyph_list
        ]
        text = "".join(glyph_list)
        buffer = vhb.shape(text)
        string = vhb.serialize_buf(buffer)
        return string

    def digraph_kerning(ttFont, glyph_list, expected_kerning):
        return (
            len(get_str_buffer(glyph_list).split("|")) > 1
            and get_kerning(glyph_list) == expected_kerning
        )

    def mark_glyphs(ttFont):
        marks = []
        if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
            class_def = ttFont["GDEF"].table.GlyphClassDef.classDefs
            glyphOrder = ttFont.getGlyphOrder()
            for name in glyphOrder:
                if name in class_def and class_def[name] == 3:
                    marks.append(name)
        return marks

    # Font has no numerals at all
    if not all([glyph_name_for_character(ttFont, c) for c in "0123456789"]):
        yield SKIP, "Font has no numerals at all"
        return

    all_glyphs = list(
        set(ttFont.getGlyphOrder()) - set(IGNORE_GLYPHS) - set(mark_glyphs(ttFont))
    )
    tabular_glyphs = []
    tabular_numerals = []

    # Fonts with tnum feautre
    if has_feature(ttFont, "tnum"):
        tabular_glyphs = list(get_substitutions(ttFont, "tnum").values())
        buf = vhb.shape("0123456789", {"features": {"tnum": True}})
        tabular_numerals = vhb.serialize_buf(buf, glyphsonly=True).split("|")

    # Without tnum feature
    else:
        # Find out if font maybe has tabular numerals by default
        glyph_widths = [
            glyph_width(ttFont, glyph_name_for_character(ttFont, c))
            for c in "0123456789"
        ]
        if len(set(glyph_widths)) == 1:
            tabular_width = glyph_width(ttFont, glyph_name_for_character(ttFont, "0"))
            tabular_numerals = [
                glyph_name_for_character(ttFont, c) for c in "0123456789"
            ]
            # Collect all glyphs with the same width as the tabular numerals
            for glyph in all_glyphs:
                unicode = unicode_for_glyphs.get(glyph)
                if (
                    unicode
                    and glyph_width(ttFont, glyph) == tabular_width
                    and unicodedata.category(chr(unicode))
                    in (
                        "Nd",  # Decimal number
                        "No",  # Other number
                        "Nl",  # Letter-like number
                        "Sm",  # Math symbol
                        "Sc",  # Currency symbol
                    )
                ):
                    tabular_glyphs.append(glyph)

    # Font has no tabular numerals
    if not tabular_numerals:
        yield SKIP, "Font has no tabular numerals"
        return

    # Actually check for kerning
    if has_feature(ttFont, "kern"):
        for sets in (
            (all_glyphs, tabular_numerals),
            (tabular_numerals, tabular_glyphs),
        ):
            combinations = unique_combinations(sets[0], sets[1])
            for x, y in combinations:
                for a, b in ((x, y), (y, x)):
                    kerning = get_kerning([a, b])
                    if kerning != 0:
                        # Check if either a or b are digraphs that themselves
                        # have kerning when decomposed in ccmp
                        # that would throw off the reading, skip if it's identical
                        # to the kerning of the whole sequence
                        if digraph_kerning(ttFont, [a], kerning) or digraph_kerning(
                            ttFont, [b], kerning
                        ):
                            pass
                        else:
                            yield FAIL, Message(
                                "has-tabular-kerning",
                                f"Kerning between {a} and {b} is {kerning}, should be 0",
                            )


@check(
    id="com.google.fonts/check/alt_caron",
    conditions=["is_ttf"],
    rationale="""
        Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright
        or quotesingle or comma or caron(comb). It should be composed with a
        distinctive glyph which doesn't look like an apostrophe.

        Source:
        https://ilovetypography.com/2009/01/24/on-diacritics/
        http://diacritics.typo.cz/index.php?id=5
        https://www.typotheque.com/articles/lcaron
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3308",
)
def com_google_fonts_check_alt_caron(ttFont):
    """Check accent of Lcaron, dcaron, lcaron, tcaron"""

    CARON_GLYPHS = set(
        (
            0x013D,  # LATIN CAPITAL LETTER L WITH CARON
            0x010F,  # LATIN SMALL LETTER D WITH CARON
            0x013E,  # LATIN SMALL LETTER L WITH CARON
            0x0165,  # LATIN SMALL LETTER T WITH CARON
        )
    )

    WRONG_CARON_MARKS = set(
        (
            0x02C7,  # CARON
            0x030C,  # COMBINING CARON
        )
    )

    # This may be expanded to include other comma-lookalikes:
    BAD_CARON_MARKS = set(
        (
            0x002C,  # COMMA
            0x2019,  # RIGHT SINGLE QUOTATION MARK
            0x201A,  # SINGLE LOW-9 QUOTATION MARK
            0x0027,  # APOSTROPHE
        )
    )

    passed = True

    glyphOrder = ttFont.getGlyphOrder()
    reverseCmap = ttFont["cmap"].buildReversed()

    for name in glyphOrder:
        if reverseCmap.get(name, set()).intersection(CARON_GLYPHS):
            glyph = ttFont["glyf"][name]
            if not glyph.isComposite():
                yield WARN, Message(
                    "decomposed-outline",
                    f"{name} is decomposed and therefore could not be checked."
                    f" Please check manually.",
                )
                continue
            if len(glyph.components) == 1:
                yield WARN, Message(
                    "single-component",
                    f"{name} is composed of a single component and therefore"
                    f" could not be checked. Please check manually.",
                )
            if len(glyph.components) > 1:
                for component in glyph.components:
                    # Uses absolutely wrong caron mark
                    # Purge other endings in the future (not .alt)
                    codepoints = reverseCmap.get(
                        component.glyphName.replace(".case", "")
                        .replace(".uc", "")
                        .replace(".sc", ""),
                        set(),
                    )
                    if codepoints.intersection(WRONG_CARON_MARKS):
                        passed = False
                        yield FAIL, Message(
                            "wrong-mark",
                            f"{name} uses component {component.glyphName}.",
                        )

                    # Uses bad mark
                    if codepoints.intersection(BAD_CARON_MARKS):
                        yield WARN, Message(
                            "bad-mark", f"{name} uses component {component.glyphName}."
                        )
    if passed:
        yield PASS, "Looks good!"


@check(
    id="com.google.fonts/check/gsub/smallcaps_before_ligatures",
    rationale="""
        OpenType small caps should be defined before ligature lookups to ensure
        proper functionality.

        Rainer Erich Scheichelbauer (a.k.a. MekkaBlue) pointed out in a tweet
        (https://twitter.com/mekkablue/status/1297486769668132865) that the ordering
        of small caps and ligature lookups can lead to bad results such as the example
        he provided of the word "WAFFLES" in small caps, but with an unfortunate
        lowercase ffl ligature substitution.
	
        This check attempts to detect this kind of mistake.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3020",
    experimental="Since 2024/Jun/10",
    conditions=["is_ttf"],
)
def com_google_fonts_check_gsub_smallcaps_before_ligatures(ttFont):
    """
    Ensure 'smcp' (small caps) lookups are defined before ligature lookups in the 'GSUB' table.
    """
    if "GSUB" not in ttFont:
        return FAIL, Message(
            "missing-gsub-table", "Font does not contain a GSUB table."
        )

    gsub_table = ttFont["GSUB"].table
    lookup_order = {
        lookup.LookupType: idx
        for idx, lookup in enumerate(gsub_table.LookupList.Lookup)
    }

    smcp_indices = [
        idx
        for idx, feature in enumerate(gsub_table.FeatureList.FeatureRecord)
        if feature.FeatureTag == "smcp"
    ]
    liga_indices = [
        idx
        for idx, feature in enumerate(gsub_table.FeatureList.FeatureRecord)
        if feature.FeatureTag == "liga"
    ]

    if not smcp_indices or not liga_indices:
        return FAIL, Message(
            "missing-lookups", "'smcp' or 'liga' lookups not found in GSUB table."
        )

    first_smcp_index = min(smcp_indices)
    first_liga_index = min(liga_indices)

    if first_smcp_index < first_liga_index:
        return PASS, "'smcp' lookups are defined before 'liga' lookups."
    else:
        return FAIL, Message(
            "feature-ordering", "'smcp' lookups are not defined before 'liga' lookups."
        )
