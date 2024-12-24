from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/weightclass",
    rationale="""
        Check METADATA.pb font weights are correct.

        For static fonts, the metadata weight should be the same as the static font's
        OS/2 usWeightClass.

        For variable fonts, the weight value should be 400 if the font's wght axis range
        includes 400, otherwise it should be the value closest to 400.
    """,
    conditions=["font_metadata"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/2683",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_metadata_weightclass(font, font_metadata):
    """Check METADATA.pb font weights are correct."""
    # Weight name to value mapping:
    GF_API_WEIGHT_NAMES = {
        100: "Thin",
        200: "ExtraLight",
        250: "Thin",  # Legacy. Pre-vf epoch
        275: "ExtraLight",  # Legacy. Pre-vf epoch
        300: "Light",
        400: "Regular",
        500: "Medium",
        600: "SemiBold",
        700: "Bold",
        800: "ExtraBold",
        900: "Black",
    }
    CSS_WEIGHT_NAMES = {
        100: "Thin",
        200: "ExtraLight",
        300: "Light",
        400: "Regular",
        500: "Medium",
        600: "SemiBold",
        700: "Bold",
        800: "ExtraBold",
        900: "Black",
    }
    ttFont = font.ttFont
    if font.is_variable_font:
        axes = {f.axisTag: f for f in ttFont["fvar"].axes}
        if "wght" not in axes:
            # if there isn't a wght axis, use the OS/2.usWeightClass
            font_weight = ttFont["OS/2"].usWeightClass
            should_be = "the same"
        else:
            # if the wght range includes 400, use 400
            wght_includes_400 = (
                axes["wght"].minValue <= 400 and axes["wght"].maxValue >= 400
            )
            if wght_includes_400:
                font_weight = 400
                should_be = (
                    "400 because it is a varfont which includes"
                    " this coordinate in its 'wght' axis"
                )
            else:
                # if 400 isn't in the wght axis range, use the value closest to 400
                if abs(axes["wght"].minValue - 400) < abs(axes["wght"].maxValue - 400):
                    font_weight = axes["wght"].minValue
                else:
                    font_weight = axes["wght"].maxValue
                should_be = (
                    f"{font_weight} because it is the closest value to 400"
                    f" on the 'wght' axis of this variable font"
                )
    else:
        font_weight = ttFont["OS/2"].usWeightClass
        if font_weight not in [250, 275]:
            should_be = "the same"
        else:
            if font_weight == 250:
                expected_value = 100  # "Thin"
            if font_weight == 275:
                expected_value = 200  # "ExtraLight"
            should_be = (
                f"{expected_value}, corresponding to"
                f' CSS weight name "{CSS_WEIGHT_NAMES[expected_value]}"'
            )

    gf_weight_name = GF_API_WEIGHT_NAMES.get(font_weight, "bad value")
    css_weight_name = CSS_WEIGHT_NAMES.get(font_metadata.weight)

    if gf_weight_name != css_weight_name:
        yield FAIL, Message(
            "mismatch",
            f'OS/2 table has usWeightClass={ttFont["OS/2"].usWeightClass},'
            f' meaning "{gf_weight_name}" on the Google Fonts API.\n\n'
            f"On METADATA.pb it should be {should_be},"
            f" but instead got {font_metadata.weight}.\n",
        )
