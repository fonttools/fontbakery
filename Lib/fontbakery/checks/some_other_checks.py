from typing import List

from fontbakery.prelude import (
    check,
    Message,
    PASS,
    FAIL,
    WARN,
    SKIP,
)
from fontbakery.checks.opentype.layout import feature_tags
from fontbakery.utils import (
    bullet_list,
    get_glyph_name,
    iterate_lookup_list_with_extensions,
)


@check(
    id="cjk_chws_feature",
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
def check_cjk_chws_feature(ttFont):
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
    id="transformed_components",
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
def check_transformed_components(ttFont, is_hinted):
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
    id="gpos7",
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
def check_gpos7(ttFont):
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
    id="freetype_rasterizer",
    conditions=["ttFont"],
    severity=10,
    rationale="""
        Malformed fonts can cause FreeType to crash.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3642",
)
def check_freetype_rasterizer(font):
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
    id="sfnt_version",
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
def check_sfnt_version(ttFont, is_ttf, is_cff, is_cff2):
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
    id="interpolation_issues",
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
def check_interpolation_issues(ttFont, config):
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
    id="math_signs_width",
    rationale="""
        It is a common practice to have math signs sharing the same width
        (preferably the same width as tabular figures accross the entire font family).

        This probably comes from the will to avoid additional tabular math signs
        knowing that their design can easily share the same width.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3832",
)
def check_math_signs_width(ttFont):
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
    id="alt_caron",
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
def check_alt_caron(ttFont):
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
