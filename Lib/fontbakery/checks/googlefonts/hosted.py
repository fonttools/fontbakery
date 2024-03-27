from fontbakery.prelude import check, disable, Message, WARN, FAIL


@check(
    id="com.google.fonts/check/version_bump",
    conditions=["api_gfonts_ttFont", "github_gfonts_ttFont"],
    proposal="legacy:check/117",
    rationale="""
        We check that the version number has been bumped since the last release on
        Google Fonts. This helps to ensure that the version being PRed is newer than
        the one currently hosted on fonts.google.com.
    """,
)
def com_google_fonts_check_version_bump(
    ttFont, api_gfonts_ttFont, github_gfonts_ttFont
):
    """Version number has increased since previous release on Google Fonts?"""
    v_number = ttFont["head"].fontRevision
    api_gfonts_v_number = api_gfonts_ttFont["head"].fontRevision
    github_gfonts_v_number = github_gfonts_ttFont["head"].fontRevision

    if v_number == api_gfonts_v_number:
        yield FAIL, (
            f"Version number {v_number:0.3f} is"
            f" equal to version on **Google Fonts**."
        )

    if v_number < api_gfonts_v_number:
        yield FAIL, (
            f"Version number {v_number:0.3f} is less than on"
            f" **Google Fonts** ({api_gfonts_v_number:0.3f})."
        )

    if v_number == github_gfonts_v_number:
        yield FAIL, (
            f"Version number {v_number:0.3f} is equal to version on"
            f" google/fonts **GitHub repo**."
        )

    if v_number < github_gfonts_v_number:
        yield FAIL, (
            f"Version number {v_number:0.3f} is less than on"
            f" google/fonts **GitHub repo** ({github_gfonts_v_number:0.3f})."
        )


@check(
    id="com.google.fonts/check/production_glyphs_similarity",
    conditions=["api_gfonts_ttFont"],
    proposal="legacy:check/118",
    rationale="""
        We check that the glyphs in the font are similar to the glyphs in the
        version hosted on fonts.google.com. We do not expect updated fonts to
        have exactly the same glyphs as the previous version, but we do expect
        the changes to be minimal.
    """,
)
def com_google_fonts_check_production_glyphs_similarity(
    ttFont, api_gfonts_ttFont, config
):
    """Glyphs are similiar to Google Fonts version?"""
    from fontbakery.utils import pretty_print_list

    def glyphs_surface_area(ttFont):
        """Calculate the surface area of a glyph's ink"""
        from fontTools.pens.areaPen import AreaPen

        glyphs = {}
        glyph_set = ttFont.getGlyphSet()
        area_pen = AreaPen(glyph_set)

        for glyph in glyph_set.keys():
            glyph_set[glyph].draw(area_pen)

            area = area_pen.value
            area_pen.value = 0
            glyphs[glyph] = area
        return glyphs

    bad_glyphs = []
    these_glyphs = glyphs_surface_area(ttFont)
    gfonts_glyphs = glyphs_surface_area(api_gfonts_ttFont)

    shared_glyphs = set(these_glyphs) & set(gfonts_glyphs)

    this_upm = ttFont["head"].unitsPerEm
    gfonts_upm = api_gfonts_ttFont["head"].unitsPerEm

    for glyph in shared_glyphs:
        # Normalize area difference against comparison's upm
        this_glyph_area = (these_glyphs[glyph] / this_upm) * gfonts_upm
        gfont_glyph_area = (gfonts_glyphs[glyph] / gfonts_upm) * this_upm

        if abs(this_glyph_area - gfont_glyph_area) > 7000:
            bad_glyphs.append(glyph)

    if bad_glyphs:
        formatted_list = "\t* " + pretty_print_list(
            config, sorted(bad_glyphs), sep="\n\t* "
        )

        yield WARN, (
            "Following glyphs differ greatly from"
            f" Google Fonts version:\n{formatted_list}"
        )


# FIXME!
# Temporarily disabled since GFonts hosted Cabin files seem to have changed in ways
# that break some of the assumptions in the check implementation below.
# More info at https://github.com/fonttools/fontbakery/issues/2581
@disable
@check(
    id="com.google.fonts/check/production_encoded_glyphs",
    conditions=["api_gfonts_ttFont"],
    proposal="legacy:check/154",
)
def com_google_fonts_check_production_encoded_glyphs(ttFont, api_gfonts_ttFont):
    """Check font has same encoded glyphs as version hosted on
    fonts.google.com"""
    cmap = ttFont["cmap"].getcmap(3, 1).cmap
    gf_cmap = api_gfonts_ttFont["cmap"].getcmap(3, 1).cmap
    missing_codepoints = set(gf_cmap.keys()) - set(cmap.keys())

    if missing_codepoints:
        hex_codepoints = [
            "0x" + hex(c).upper()[2:].zfill(4) for c in sorted(missing_codepoints)
        ]
        yield FAIL, Message(
            "lost-glyphs",
            f"Font is missing the following glyphs"
            f" from the previous release"
            f" [{', '.join(hex_codepoints)}]",
        )
