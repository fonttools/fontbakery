from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="opentype/fvar/regular_coords_correct",
    rationale="""
        According to the Open-Type spec's registered design-variation tags,instances in a variable font should have certain prescribed values.
        If a variable font has a 'wght' (Weight) axis, the valid coordinate range is 1-1000.
        If a variable font has a 'wdth' (Width) axis, the valid numeric range is strictly greater than zero.
        If a variable font has a 'slnt' (Slant) axis, then the coordinate of its 'Regular' instance is required to be 0.
        If a variable font has a 'ital' (Slant) axis, then the coordinate of its 'Regular' instance is required to be 0.
    """,
    conditions=["is_variable_font"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1707",
        "https://github.com/fonttools/fontbakery/issues/2572",
    ],
)
def check_fvar_regular_coords_correct(
    ttFont,
    regular_wght_coord,
    regular_wdth_coord,
    regular_slnt_coord,
    regular_ital_coord,
    regular_opsz_coord,
):
    """Axes and named instances fall within correct ranges?"""

    REGULAR_COORDINATE_EXPECTATIONS = [
        ("wght", 400, regular_wght_coord),
        ("wdth", 100, regular_wdth_coord),
        ("slnt", 0, regular_slnt_coord),
        ("ital", 0, regular_ital_coord),
    ]

    if (
        regular_wght_coord is None
        and regular_wdth_coord is None
        and regular_slnt_coord is None
        and regular_ital_coord is None
        and regular_opsz_coord is None
    ):
        yield FAIL, Message("no-regular-instance", '"Regular" instance not present.')
        return

    for axis, expected, actual in REGULAR_COORDINATE_EXPECTATIONS:
        if actual is not None and actual != expected:
            yield FAIL, Message(
                f"{axis}-not-{expected}",
                f"Regular instance has {axis} coordinate of {actual},"
                f" expected {expected}",
            )

    actual = regular_opsz_coord
    if actual and not (10 <= actual <= 16):
        yield WARN, Message(
            "opsz",
            f"Regular instance has opsz coordinate of {actual},"
            f" expected between 10 and 16",
        )
