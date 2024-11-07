from fontbakery.prelude import check, Message, INFO


@check(
    id="epar",
    rationale="""
        The EPAR table is/was a way of expressing common licensing permissions and
        restrictions in metadata; while almost nothing supported it, Dave Crossland
        wonders that having this INFO-level check could help make it more popular.

        More info is available at:
        https://davelab6.github.io/epar/
    """,
    severity=1,
    proposal="https://github.com/fonttools/fontbakery/issues/226",
)
def check_epar(ttFont):
    """EPAR table present in font?"""

    if "EPAR" not in ttFont:
        yield INFO, Message(
            "lacks-EPAR",
            "EPAR table not present in font. To learn more see"
            " https://github.com/fonttools/fontbakery/issues/818",
        )
