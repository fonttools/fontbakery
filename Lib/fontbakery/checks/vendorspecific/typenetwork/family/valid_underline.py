from fontbakery.prelude import check, Message, FAIL


@check(
    id="typenetwork/family/valid_underline",
    rationale="""
        If underline thickness is not set nothing gets rendered on Figma.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
    misc_metadata={"affects": [("Figma", "unspecified")]},
)
def check_family_valid_underline(ttFont):
    """Font has a valid underline thickness?"""

    underlineThickness = ttFont["post"].underlineThickness
    if underlineThickness is None or underlineThickness == 0:
        yield FAIL, Message(
            "invalid-underline-thickness",
            f"Thickness of the underline is {underlineThickness} which is not valid.",
        )
