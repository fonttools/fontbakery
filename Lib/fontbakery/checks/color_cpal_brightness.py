from fontbakery.prelude import check, Message, WARN


@check(
    id="color_cpal_brightness",
    rationale="""
        Layers of a COLRv0 font should not be too dark or too bright. When layer colors
        are set explicitly, they can't be changed and they may turn out illegible
        against dark or bright backgrounds.

        While traditional color-less fonts can be colored in design apps or CSS, a
        black color definition in a COLRv0 font actually means that that layer will be
        rendered in black regardless of the background color. This leads to text
        becoming invisible against a dark background, for instance when using a dark
        theme in a web browser or operating system.

        This check ensures that layer colors are at least 10% bright and at most 90%
        bright, when not already set to the current color (0xFFFF).
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3908",
)
def check_color_cpal_brightness(config, ttFont):
    """Color layers should have a minimum brightness."""
    from fontbakery.utils import pretty_print_list

    def color_brightness(hex_value):
        """Generic color brightness formula"""
        return (hex_value[0] * 299 + hex_value[1] * 587 + hex_value[2] * 114) / 1000

    minimum_brightness = 256 * 0.1
    FOREGROUND_COLOR = 0xFFFF
    dark_glyphs = []
    if "COLR" in ttFont.keys() and ttFont["COLR"].version == 0:
        for key in ttFont["COLR"].ColorLayers:
            for layer in ttFont["COLR"].ColorLayers[key]:
                # 0xFFFF is the foreground color, ignore
                if layer.colorID != FOREGROUND_COLOR:
                    hex_value = ttFont["CPAL"].palettes[0][layer.colorID]
                    layer_brightness = color_brightness(hex_value)
                    if (
                        layer_brightness < minimum_brightness
                        or layer_brightness > 256 - minimum_brightness
                    ):
                        if key not in dark_glyphs:
                            dark_glyphs.append(key)
    if dark_glyphs:
        dark_glyphs = pretty_print_list(config, sorted(dark_glyphs))
        yield WARN, Message(
            "glyphs-too-dark-or-too-bright",
            f"The following glyphs have layers that are too bright or"
            f" too dark: {dark_glyphs}.\n"
            f"\n"
            f" To fix this, please either set the color definitions of all"
            f" layers in question to current color (0xFFFF), or alter"
            f" the brightness of these layers significantly.",
        )
