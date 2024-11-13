from fontbakery.prelude import check, Message, FAIL, PASS, WARN


@check(
    id="opentype/varfont/regular_wght_coord",
    rationale="""
        According to the OpenType spec's
        registered design-variation tag 'wght' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght

        If a variable font has a 'wght' (Weight) axis, then the coordinate of
        its 'Regular' instance is required to be 400.
    """,
    conditions=["is_variable_font", "has_wght_axis"],
    proposal="https://github.com/fonttools/fontbakery/issues/1707",
)
def check_varfont_regular_wght_coord(ttFont, regular_wght_coord):
    """The variable font 'wght' (Weight) axis coordinate must be 400 on the
    'Regular' instance."""

    if regular_wght_coord is None:
        yield FAIL, Message("no-regular-instance", '"Regular" instance not present.')
    elif regular_wght_coord == 400:
        yield PASS, "Regular:wght is 400."
    else:
        yield FAIL, Message(
            "wght-not-400",
            f'The "wght" axis coordinate of'
            f' the "Regular" instance must be 400.'
            f" Got {regular_wght_coord} instead.",
        )


@check(
    id="opentype/varfont/regular_wdth_coord",
    rationale="""
        According to the OpenType spec's
        registered design-variation tag 'wdth' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth

        If a variable font has a 'wdth' (Width) axis, then the coordinate of
        its 'Regular' instance is required to be 100.
    """,
    conditions=["is_variable_font", "has_wdth_axis"],
    proposal="https://github.com/fonttools/fontbakery/issues/1707",
)
def check_varfont_regular_wdth_coord(ttFont, regular_wdth_coord):
    """
    The variable font 'wdth' (Width) axis coordinate must be 100 on the 'Regular'
    instance.
    """

    if regular_wdth_coord is None:
        yield FAIL, Message("no-regular-instance", '"Regular" instance not present.')
    elif regular_wdth_coord == 100:
        yield PASS, "Regular:wdth is 100."
    else:
        yield FAIL, Message(
            "wdth-not-100",
            f'The "wdth" axis coordinate of'
            f' the "Regular" instance must be 100.'
            f" Got {regular_wdth_coord} as a default value instead.",
        )


@check(
    id="opentype/varfont/regular_slnt_coord",
    rationale="""
        According to the OpenType spec's
        registered design-variation tag 'slnt' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_slnt

        If a variable font has a 'slnt' (Slant) axis, then the coordinate of
        its 'Regular' instance is required to be zero.
    """,
    conditions=["is_variable_font", "has_slnt_axis"],
    proposal="https://github.com/fonttools/fontbakery/issues/1707",
)
def check_varfont_regular_slnt_coord(ttFont, regular_slnt_coord):
    """
    The variable font 'slnt' (Slant) axis coordinate must be zero on the 'Regular'
    instance.
    """

    if regular_slnt_coord is None:
        yield FAIL, Message("no-regular-instance", '"Regular" instance not present.')
    elif regular_slnt_coord == 0:
        yield PASS, "Regular:slnt is zero."
    else:
        yield FAIL, Message(
            "slnt-not-0",
            f'The "slnt" axis coordinate of'
            f' the "Regular" instance must be zero.'
            f" Got {regular_slnt_coord} as a default value instead.",
        )


@check(
    id="opentype/varfont/regular_ital_coord",
    rationale="""
        According to the OpenType spec's
        registered design-variation tag 'ital' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_ital

        If a variable font has a 'ital' (Italic) axis, then the coordinate of
        its 'Regular' instance is required to be zero.
    """,
    conditions=["is_variable_font", "has_ital_axis"],
    proposal="https://github.com/fonttools/fontbakery/issues/1707",
)
def check_varfont_regular_ital_coord(ttFont, regular_ital_coord):
    """
    The variable font 'ital' (Italic) axis coordinate must be zero on the 'Regular'
    instance.
    """

    if regular_ital_coord is None:
        yield FAIL, Message("no-regular-instance", '"Regular" instance not present.')
    elif regular_ital_coord == 0:
        yield PASS, "Regular:ital is zero."
    else:
        yield FAIL, Message(
            "ital-not-0",
            f'The "ital" axis coordinate of'
            f' the "Regular" instance must be zero.'
            f" Got {regular_ital_coord} as a default value instead.",
        )


@check(
    id="opentype/varfont/regular_opsz_coord",
    rationale="""
        According to the OpenType spec's
        registered design-variation tag 'opsz' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_opsz

        If a variable font has an 'opsz' (Optical Size) axis, then
        the coordinate of its 'Regular' instance is recommended to be
        a value in the range 10 to 16.
    """,
    conditions=["is_variable_font", "has_opsz_axis"],
    proposal="https://github.com/fonttools/fontbakery/issues/1707",
)
def check_varfont_regular_opsz_coord(ttFont, regular_opsz_coord):
    """
    The variable font 'opsz' (Optical Size) axis coordinate should be between 10 and 16
    on the 'Regular' instance.
    """

    if regular_opsz_coord is None:
        yield FAIL, Message("no-regular-instance", '"Regular" instance not present.')
    elif regular_opsz_coord >= 10 and regular_opsz_coord <= 16:
        yield PASS, f"Regular:opsz coordinate ({regular_opsz_coord}) looks good."
    else:
        yield WARN, Message(
            "opsz-out-of-range",
            f'The "opsz" (Optical Size) coordinate'
            f' on the "Regular" instance is recommended'
            f" to be a value in the range 10 to 16."
            f" Got {regular_opsz_coord} instead.",
        )
