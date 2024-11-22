from fontbakery.prelude import check, Message, FAIL


@check(
    id="typenetwork/family/valid_strikeout",
    rationale="""
        If strikeout size is not set, nothing gets rendered on Figma.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
    misc_metadata={"affects": [("Figma", "unspecified")]},
)
def check_family_valid_strikeout(ttFont):
    """Font has a value strikeout size?"""

    strikeoutSize = ttFont["OS/2"].yStrikeoutSize
    if strikeoutSize is None or strikeoutSize == 0:
        yield FAIL, Message(
            "invalid-strikeout-size",
            f"Size of the strikeout is {strikeoutSize} which is not valid.",
        )
