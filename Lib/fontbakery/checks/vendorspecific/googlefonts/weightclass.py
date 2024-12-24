from fontbakery.checks.vendorspecific.googlefonts.conditions import expected_font_names
from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/weightclass",
    rationale="""
        Google Fonts expects variable fonts, static ttfs and static otfs to have
        differing OS/2 usWeightClass values.

        - For Variable Fonts, Thin-Black must be 100-900

        - For static ttfs, Thin-Black can be 100-900 or 250-900

        - For static otfs, Thin-Black must be 250-900

        If static otfs are set lower than 250, text may appear blurry in
        legacy Windows applications.

        Glyphsapp users can change the usWeightClass value of an instance by adding
        a 'weightClass' customParameter.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_weightclass(font, ttFonts):
    """
    Check the OS/2 usWeightClass is appropriate for the font's best SubFamily name.
    """
    value = font.ttFont["OS/2"].usWeightClass
    expected_names = expected_font_names(font.ttFont, ttFonts)
    expected_value = expected_names["OS/2"].usWeightClass
    style_name = font.ttFont["name"].getBestSubFamilyName()
    has_expected_value = value == expected_value
    fail_message = (
        "Best SubFamily name is '{}'. Expected OS/2 usWeightClass is {}, got {}."
    )
    if font.is_variable_font:
        if not has_expected_value:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, expected_value, value)
            )
    # overrides for static Thin and ExtaLight fonts
    # for static ttfs, we don't mind if Thin is 250 and ExtraLight is 275.
    # However, if the values are incorrect we will recommend they set Thin
    # to 100 and ExtraLight to 250.
    # for static otfs, Thin must be 250 and ExtraLight must be 275
    elif "Thin" in style_name:
        if font.is_ttf and value not in [100, 250]:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, expected_value, value)
            )
        if font.is_cff and value != 250:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, 250, value)
            )

    elif "ExtraLight" in style_name:
        if font.is_ttf and value not in [200, 275]:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, expected_value, value)
            )
        if font.is_cff and value != 275:
            yield FAIL, Message(
                "bad-value", fail_message.format(style_name, 275, value)
            )

    elif not has_expected_value:
        yield FAIL, Message(
            "bad-value", fail_message.format(style_name, expected_value, value)
        )
