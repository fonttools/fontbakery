from fontbakery.prelude import check, Message, WARN


@check(
    id="mandatory_avar_table",
    rationale="""
        Most variable fonts should include an avar table to correctly define
        axes progression rates.

        For example, a weight axis from 0% to 100% doesn't map directly to 100 to 1000,
        because a 10% progression from 0% may be too much to define the 200,
        while 90% may be too little to define the 900.

        If the progression rates of axes is linear, this check can be ignored.
        Fontmake will also skip adding an avar table if the progression rates
        are linear. However, it is still recommended that designers visually proof
        each instance is at the expected weight, width etc.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3100"
    # NOTE: This is a high-priority WARN.
)
def check_mandatory_avar_table(ttFont):
    """Ensure variable fonts include an avar table."""
    if "avar" not in ttFont:
        yield WARN, Message(
            "missing-avar",
            (
                "This variable font does not have an avar table."
                " Most variable fonts should include an avar table to correctly"
                " define axes progression rates."
            ),
        )
