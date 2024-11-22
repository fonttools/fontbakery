from fontbakery.prelude import check, Message, PASS, WARN, SKIP, INFO


@check(
    id="typenetwork/varfont/fvar_axes_order",
    rationale="""
        If a font doesn’t have a STAT table, instances get sorted better on Adobe Apps
        when fvar axes follow a specific order: 'opsz', 'wdth', 'wght','ital', 'slnt'.

        We should deprecate this check since STAT is a required table.
        """,
    conditions=["is_variable_font"],
    proposal=[
        "https://github.com/fonttools/fontbakery/pull/4260",
        # "https://github.com/TypeNetwork/fontQA/issues/25", # Currently private repo.
    ],
)
def check_varfont_fvar_axes_order(ttFont):
    """Check fvar axes order"""
    prefferedOrder = ["opsz", "wdth", "wght", "ital", "slnt"]
    fontRegisteredAxes = []
    customAxes = []

    if "STAT" in ttFont.keys():
        yield SKIP, "The font has a STAT table. This will control instances order."
    else:
        for index, axis in enumerate(ttFont["fvar"].axes):
            if axis.axisTag in prefferedOrder:
                fontRegisteredAxes.append(axis.axisTag)
            else:
                customAxes.append((axis.axisTag, index))

        filtered = [axis for axis in prefferedOrder if axis in fontRegisteredAxes]

        if filtered != fontRegisteredAxes:
            yield WARN, Message(
                "axes-incorrect-order",
                "Font’s registered axes are not in a correct order to get good"
                "instances sorting on Adobe apps.\n\n"
                f"Current order is {fontRegisteredAxes}, but it should be {filtered}",
            )
        else:
            yield PASS, "Font’s axes follow the preferred sorting."

        if customAxes:
            yield INFO, Message(
                "custom-axes",
                "The font has custom axes with the indicated order:\n\n"
                f"{customAxes}\n\n"
                "Its order can depend on the kind of variation and the subfamily"
                "groups that may create.",
            )
