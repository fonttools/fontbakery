from fontbakery.callable import check
from fontbakery.status import WARN
from fontbakery.message import Message


@check(
    id="com.google.fonts/check/dsig",
    rationale="""
        Microsoft Office 2013 and below products expect fonts to have a digital
        signature declared in a DSIG table in order to implement OpenType features.
        The EOL date for Microsoft Office 2013 products is 4/11/2023.
        This issue does not impact Microsoft Office 2016 and above products.

        As we approach the EOL date, it is now considered better to
        completely remove the table.

        But if you still want your font to support OpenType features on Office 2013,
        then you may find it handy to add a fake signature on a placeholder DSIG table
        by running one of the helper scripts provided at
        https://github.com/googlefonts/gftools

        Reference: https://github.com/fonttools/fontbakery/issues/1845
    """,
    proposal=[
        "legacy:check/045",
        "https://github.com/fonttools/fontbakery/issues/3398",
    ],
)
def com_google_fonts_check_dsig(ttFont):
    """Does the font have a DSIG table?"""
    if "DSIG" in ttFont:
        yield WARN, Message(
            "found-DSIG",
            "This font has a digital signature (DSIG table) which"
            " is only required - even if only a placeholder"
            " - on old programs like MS Office 2013 in order to"
            " work properly.\n"
            "The current recommendation is to completely"
            " remove the DSIG table.",
        )
