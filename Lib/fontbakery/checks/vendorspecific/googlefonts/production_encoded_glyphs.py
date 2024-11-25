from fontbakery.prelude import check, disable, Message, FAIL


# FIXME!
# Temporarily disabled since GFonts hosted Cabin files seem to have changed in ways
# that break some of the assumptions in the check implementation below.
# More info at https://github.com/fonttools/fontbakery/issues/2581
@disable
@check(
    id="googlefonts/production_encoded_glyphs",
    conditions=["api_gfonts_ttFont"],
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_production_encoded_glyphs(ttFont, api_gfonts_ttFont):
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
