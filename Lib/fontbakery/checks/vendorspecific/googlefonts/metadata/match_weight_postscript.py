from fontbakery.prelude import check, FAIL


@check(
    id="googlefonts/metadata/match_weight_postscript",
    conditions=[
        "font_metadata",
        "not is_variable_font",
    ],
    rationale="""
        The METADATA.pb file has a field for each font file called 'weight',
        with a numeric value from 100 to 900. This check ensures that the
        weight value seems appropriate given the style name in the font's
        postScriptName. For example, a font with a postScriptName ending in
        'Bold' should have a weight value of 700.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_match_weight_postscript(font_metadata):
    """METADATA.pb weight matches postScriptName for static fonts."""
    WEIGHTS = {
        "Thin": 100,
        "ThinItalic": 100,
        "ExtraLight": 200,
        "ExtraLightItalic": 200,
        "Light": 300,
        "LightItalic": 300,
        "Regular": 400,
        "Italic": 400,
        "Medium": 500,
        "MediumItalic": 500,
        "SemiBold": 600,
        "SemiBoldItalic": 600,
        "Bold": 700,
        "BoldItalic": 700,
        "ExtraBold": 800,
        "ExtraBoldItalic": 800,
        "Black": 900,
        "BlackItalic": 900,
    }
    pair = []
    for k, weight in WEIGHTS.items():
        if weight == font_metadata.weight:
            pair.append((k, weight))

    if not pair:
        yield FAIL, (
            f"METADATA.pb: Font weight value ({font_metadata.weight}) is invalid."
        )
    elif not (
        font_metadata.post_script_name.endswith("-" + pair[0][0])
        or font_metadata.post_script_name.endswith("-" + pair[1][0])
    ):
        yield FAIL, (
            f"METADATA.pb: Mismatch between postScriptName"
            f' ("{font_metadata.post_script_name}")'
            f" and weight value ({pair[0][1]}). The name must be"
            f' ended with "{pair[0][0]}" or "{pair[1][0]}".\n'
        )
