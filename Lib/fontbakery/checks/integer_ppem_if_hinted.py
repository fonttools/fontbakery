from fontbakery.prelude import check, Message, FAIL


@check(
    id="integer_ppem_if_hinted",
    conditions=["is_hinted"],
    rationale="""
        Hinted fonts must have head table flag bit 3 set.

        Per https://docs.microsoft.com/en-us/typography/opentype/spec/head,
        bit 3 of Head::flags decides whether PPEM should be rounded. This bit should
        always be set for hinted fonts.

        Note:
        Bit 3 = Force ppem to integer values for all internal scaler math;
                May use fractional ppem sizes if this bit is clear;
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2338",
)
def check_integer_ppem_if_hinted(ttFont):
    """PPEM must be an integer on hinted fonts."""

    if not ttFont["head"].flags & (1 << 3):
        yield FAIL, Message(
            "bad-flags",
            (
                "This is a hinted font, so it must have bit 3 set on the flags of"
                " the head table, so that PPEM values will be rounded into an"
                " integer value.\n"
                "\n"
                "This can be accomplished by using the 'gftools fix-hinting' command:\n"
                "\n"
                "```\n"
                "# create virtualenv\n"
                "python3 -m venv venv"
                "\n"
                "# activate virtualenv\n"
                "source venv/bin/activate"
                "\n"
                "# install gftools\n"
                "pip install git+https://www.github.com/googlefonts/gftools\n"
                "```\n"
            ),
        )
