from fontbakery.prelude import check, Message, WARN


@check(
    id="googlefonts/description/eof_linebreak",
    conditions=["description"],
    rationale="""
        Some older text-handling tools sometimes misbehave if the last line of data
        in a text file is not terminated with a newline character (also known as '\\n').

        We know that this is a very small detail, but for the sake of keeping all
        DESCRIPTION.en_us.html files uniformly formatted throughout the GFonts
        collection, we chose to adopt the practice of placing this final linebreak
        character on them.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2879",
)
def check_description_eof_linebreak(description):
    """DESCRIPTION.en_us.html should end in a linebreak."""
    if description[-1] != "\n":
        yield WARN, Message(
            "missing-eof-linebreak",
            "The last characther on DESCRIPTION.en_us.html"
            " is not a line-break. Please add it.",
        )
