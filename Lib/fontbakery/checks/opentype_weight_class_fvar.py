from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/weight_class_fvar",
    rationale="""
        According to Microsoft's OT Spec the OS/2 usWeightClass
        should match the fvar default value.
    """,
    conditions=["is_variable_font", "has_wght_axis"],
    proposal="https://github.com/googlefonts/gftools/issues/477",
)
def check_weight_class_fvar(ttFont):
    """Checking if OS/2 usWeightClass matches fvar."""

    fvar = ttFont["fvar"]
    default_axis_values = {a.axisTag: a.defaultValue for a in fvar.axes}

    fvar_value = default_axis_values.get("wght")
    os2_value = ttFont["OS/2"].usWeightClass

    if os2_value != int(fvar_value):
        yield FAIL, Message(
            "bad-weight-class",
            f"OS/2 usWeightClass is '{os2_value}', "
            f"but should match fvar default value '{fvar_value}'.",
        )
