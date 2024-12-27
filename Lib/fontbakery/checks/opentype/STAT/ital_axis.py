from fontbakery.prelude import check, Message, FAIL, WARN, SKIP


def get_STAT_axis(ttFont, tag):
    for axis in ttFont["STAT"].table.DesignAxisRecord.Axis:
        if axis.AxisTag == tag:
            return axis
    return None


def get_STAT_axis_value(ttFont, tag):
    for i, axis in enumerate(ttFont["STAT"].table.DesignAxisRecord.Axis):
        if axis.AxisTag == tag:
            for axisValue in ttFont["STAT"].table.AxisValueArray.AxisValue:
                if axisValue.AxisIndex == i:
                    linked_value = None
                    if hasattr(axisValue, "LinkedValue"):
                        linked_value = axisValue.LinkedValue
                    return axisValue.Value, axisValue.Flags, linked_value
    return None, None, None


def check_has_ital(font):
    if "STAT" not in font.ttFont:
        yield FAIL, Message(
            "no-stat",
            f"Font {font.file} has no STAT table",
        )
        return

    if "ital" not in [
        axis.AxisTag for axis in font.ttFont["STAT"].table.DesignAxisRecord.Axis
    ]:
        yield FAIL, Message(
            "missing-ital-axis",
            f"Font {font.file} lacks an 'ital' axis in the STAT table.",
        )


def check_ital_is_binary_and_last(font, is_italic):
    if "STAT" not in font.ttFont:
        return

    if not get_STAT_axis(font.ttFont, "ital"):
        yield SKIP, "Font {font.file} doesn't have an ital axis"
        return

    tags = [axis.AxisTag for axis in font.ttFont["STAT"].table.DesignAxisRecord.Axis]
    ital_pos = tags.index("ital")
    if ital_pos != len(tags) - 1:
        yield WARN, Message(
            "ital-axis-not-last",
            f"Font {font.file} has 'ital' axis in position"
            f" {ital_pos + 1} of {len(tags)}.",
        )

    value, flags, linked_value = get_STAT_axis_value(font.ttFont, "ital")
    if (value, flags, linked_value) == (None, None, None):
        yield SKIP, "No 'ital' axis in STAT."
        return

    if is_italic:
        expected_value = 1.0  # Italic
        expected_flags = 0x0000  # AxisValueTableFlags empty
    else:
        expected_value = 0.0  # Upright
        expected_flags = 0x0002  # ElidableAxisValueName

    if value != expected_value:
        yield WARN, Message(
            "wrong-ital-axis-value",
            f"{font.file} has STAT table 'ital' axis with wrong value."
            f" Expected: {expected_value}, got '{value}'",
        )

    if flags != expected_flags:
        yield WARN, Message(
            "wrong-ital-axis-flag",
            f"{font.file} has STAT table 'ital' axis with wrong flags."
            f" Expected: {expected_flags}, got '{flags}'",
        )

    # If we are Roman, check for the linked value
    if not is_italic:
        if linked_value != 1.0:  # Roman should be linked to a fully-italic.
            yield WARN, Message(
                "wrong-ital-axis-linkedvalue",
                f"{font.file} has STAT table 'ital' axis with wrong linked value."
                f" Expected: 1.0, got '{linked_value}'",
            )


def segment_vf_collection(fonts):
    roman_italic = []
    italics = []
    non_italics = []
    for font in fonts:
        if "-Italic[" in font.file:
            italics.append(font)
        else:
            non_italics.append(font)

    for italic in italics:
        # Find a matching roman
        suspected_roman = italic.file.replace("-Italic[", "[")

        found_roman = None
        for non_italic in non_italics:
            if non_italic.file == suspected_roman:
                found_roman = non_italic
                break

        if found_roman:
            non_italics.remove(found_roman)
            roman_italic.append((found_roman, italic))
        else:
            roman_italic.append((None, italic))

    # Now add all the remaining non-italic fonts
    for roman in non_italics:
        roman_italic.append((roman, None))

    return roman_italic


@check(
    id="opentype/STAT/ital_axis",
    rationale="""
        Check that related Upright and Italic VFs have an
        'ital' axis in the STAT table.

        Since the STAT table can be used to create new instances, it is
        important to ensure that such an 'ital' axis be the last one
        declared in the STAT table so that the eventual naming of new
        instances follows the subfamily traditional scheme (RIBBI / WWS)
        where "Italic" is always last.

        The 'ital' axis should also be strictly boolean, only accepting
        values of 0 (for Uprights) or 1 (for Italics). This usually works
        as a mechanism for selecting between two linked variable font files.

        Also, the axis value name for uprights must be set as elidable.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/2934",
        "https://github.com/fonttools/fontbakery/issues/3668",
        "https://github.com/fonttools/fontbakery/issues/3669",
    ],
)
def check_STAT_ital_axis(fonts, config):
    """Ensure VFs have 'ital' STAT axis."""

    for roman, italic in segment_vf_collection(fonts):
        if roman and italic:
            # These should definitely both have an ital axis
            yield from check_has_ital(roman)
            yield from check_has_ital(italic)
            yield from check_ital_is_binary_and_last(roman, False)
            yield from check_ital_is_binary_and_last(italic, True)
        elif italic:
            yield FAIL, Message(
                "missing-roman",
                f"Italic font {italic.file} has no matching Roman font.",
            )
        elif roman:
            yield from check_ital_is_binary_and_last(roman, False)
