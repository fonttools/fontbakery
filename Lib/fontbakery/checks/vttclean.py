from fontbakery.prelude import check, Message, FAIL


@check(
    id="vttclean",
    rationale="""
        The goal here is to reduce filesizes and improve pageloading when dealing
        with webfonts.

        The VTT Talk sources are not necessary at runtime and endup being just dead
        weight when left embedded in the font binaries. The sources should be kept on
        the project files but stripped out when building release binaries.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2059",
)
def check_vtt_clean(ttFont, vtt_talk_sources):
    """There must not be VTT Talk sources in the font."""

    if vtt_talk_sources:
        yield FAIL, Message(
            "has-vtt-sources",
            f"Some tables containing VTT Talk (hinting) sources"
            f" were found in the font and should be removed in order"
            f" to reduce total filesize:"
            f" {', '.join(vtt_talk_sources)}",
        )
