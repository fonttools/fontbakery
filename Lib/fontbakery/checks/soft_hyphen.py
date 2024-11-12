from fontbakery.prelude import check, Message, WARN, PASS


@check(
    id="soft_hyphen",
    rationale="""
        The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark
        a hyphenation possibility within a word in the absence of or
        overriding dictionary hyphenation.

        It is sometimes designed empty with no width (such as a control character),
        sometimes the same as the traditional hyphen, sometimes double encoded with
        the hyphen.

        That being said, it is recommended to not include it in the font at all,
        because discretionary hyphenation should be handled at the level of the
        shaping engine, not the font. Also, even if present, the software would
        not display that character.

        More discussion at:
        https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/4046",
        "https://github.com/fonttools/fontbakery/issues/3486",
    ],
)
def check_soft_hyphen(ttFont):
    """Does the font contain a soft hyphen?"""
    if 0x00AD in ttFont["cmap"].getBestCmap().keys():
        yield WARN, Message("softhyphen", "This font has a 'Soft Hyphen' character.")
    else:
        yield PASS, "Looks good!"
