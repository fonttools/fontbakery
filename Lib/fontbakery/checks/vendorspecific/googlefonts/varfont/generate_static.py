from fontbakery.prelude import FAIL, PASS, Message, check


@check(
    id="googlefonts/varfont/generate_static",
    rationale="""
        Google Fonts may serve static fonts which have been generated from variable
        fonts. This check will attempt to generate a static ttf using fontTool's
        varLib mutator.

        The target font will be the mean of each axis e.g:

        **VF font axes**

        - min weight, max weight = 400, 800

        - min width, max width = 50, 100

        **Target Instance**

        - weight = 600

        - width = 75
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/1727",
)
def check_varfont_generate_static(ttFont):
    """Check a static ttf can be generated from a variable font."""
    import tempfile

    from fontTools.varLib import mutator

    try:
        loc = {
            k.axisTag: float((k.maxValue + k.minValue) / 2) for k in ttFont["fvar"].axes
        }
        with tempfile.TemporaryFile() as instance:
            font = mutator.instantiateVariableFont(ttFont, loc)
            font.save(instance)
            yield PASS, "fontTools.varLib.mutator generated a static font instance"
    except Exception as e:
        yield FAIL, Message(
            "varlib-mutator",
            f"fontTools.varLib.mutator failed"
            f" to generated a static font instance\n"
            f"{repr(e)}",
        )
