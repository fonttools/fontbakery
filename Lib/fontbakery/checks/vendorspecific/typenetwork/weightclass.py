from fontbakery.testable import Font
from fontbakery.prelude import check, condition, Message, PASS, FAIL, INFO


@condition(Font)
def stylename(font):
    ttFont = font.ttFont
    if ttFont["name"].getDebugName(16):
        styleName = ttFont["name"].getDebugName(17)
    else:
        styleName = ttFont["name"].getDebugName(2)
    return styleName


@condition(Font)
def tn_expected_os2_weight(font):
    """The weight name and the expected OS/2 usWeightClass value inferred from
    the style part of the font name.
    Here the common/expected values and weight names:
    100-250, Thin
    200-275, ExtraLight
    300, Light
    400, Regular
    500, Medium
    600, SemiBold
    700, Bold
    800, ExtraBold
    900, Black
    Thin is not set to 100 because of legacy Windows GDI issues:
    https://www.adobe.com/devnet/opentype/afdko/topic_font_wt_win.html
    """
    if not font.stylename:
        return None
    # Weight name to value mapping:
    TN_EXPECTED_WEIGHTS = {
        "Thin": [100, 250],
        "ExtraLight": [200, 275],
        "Light": 300,
        "Regular": 400,
        "Medium": 500,
        "SemiBold": 600,
        "Bold": 700,
        "ExtraBold": 800,
        "Black": 900,
    }
    stylename = font.stylename

    # Modify style name for weights using space separator
    prefixes = ["Semi ", "Ultra ", "Extra "]
    for prefix in prefixes:
        if prefix in stylename:
            stylename = stylename.replace(prefix, prefix.strip())

    if stylename == "Italic":
        weight_name = "Regular"
    elif stylename.endswith("Italic"):
        weight_name = stylename.replace("Italic", "").rstrip()
    elif stylename.endswith("Oblique"):
        weight_name = stylename.replace("Oblique", "").rstrip()
    else:
        weight_name = stylename

    expected = None
    for expectedWeightName, expectedWeightValue in TN_EXPECTED_WEIGHTS.items():
        if expectedWeightName.lower() in weight_name.lower().split(" "):
            expected = expectedWeightValue
            break

    return {"name": weight_name, "weightClass": expected}


@check(
    id="typenetwork/weightclass",
    conditions=["tn_expected_os2_weight"],
    rationale="""
        For Variable Fonts, it should be equal to default wght, for static ttfs,
        Thin-Black can be 100-900 or 250-900,
        for static otfs, Thin-Black must be 250-900.

        If static otfs are set lower than 250, text may appear blurry in
        legacy Windows applications.
        Glyphsapp users can change the usWeightClass value of an instance by adding
        a 'weightClass' customParameter.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_weightclass(font, tn_expected_os2_weight):
    """Checking OS/2 usWeightClass."""
    failed = False
    expected_value = tn_expected_os2_weight["weightClass"]
    weight_name = tn_expected_os2_weight["name"].lower()
    os2_value = font.ttFont["OS/2"].usWeightClass

    fail_message = "OS/2 usWeightClass is '{}' when it should be '{}'."
    no_value_message = "OS/2 usWeightClass is '{}' and weight name is '{}'."

    if font.is_variable_font:
        fvar = font.ttFont["fvar"]
        if font.has_wght_axis:
            default_axis_values = {a.axisTag: a.defaultValue for a in fvar.axes}
            fvar_value = default_axis_values.get("wght")

            if os2_value != int(fvar_value):
                failed = True
                yield FAIL, Message(
                    "bad-value", fail_message.format(os2_value, fvar_value)
                )
        else:
            if os2_value != 400:
                failed = True
                yield FAIL, Message("bad-value", fail_message.format(os2_value, 400))
    # overrides for static Thin and ExtaLight fonts
    # for static ttfs, we don't mind if Thin is 250 and ExtraLight is 275.
    # However, if the values are incorrect we will recommend they set Thin
    # to 100 and ExtraLight to 250.
    # for static otfs, Thin must be 250 and ExtraLight must be 275
    else:
        if not expected_value:
            failed = True
            yield INFO, Message(
                "no-value", no_value_message.format(os2_value, weight_name)
            )

        elif "thin" in weight_name.split(" "):
            if os2_value not in expected_value:
                failed = True
                yield FAIL, Message(
                    "bad-value", fail_message.format(os2_value, expected_value)
                )

        elif "extralight" in weight_name.split(" "):
            if os2_value not in expected_value:
                failed = True
                yield FAIL, Message(
                    "bad-value", fail_message.format(os2_value, expected_value)
                )

        elif os2_value != expected_value:
            failed = True
            yield FAIL, Message(
                "bad-value", fail_message.format(os2_value, expected_value)
            )

    if not failed:
        yield PASS, "OS/2 usWeightClass is good"
