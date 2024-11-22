from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/escaped_strings",
    rationale="""
        In some cases we've seen designer names and other fields with escaped strings
        in METADATA files (such as "Juli\\303\\241n").

        Nowadays the strings can be full unicode strings (such as "Julián") and do
        not need escaping.

        Escaping quotes or double-quotes is fine, though.
    """,
    conditions=["metadata_file"],
    proposal="https://github.com/fonttools/fontbakery/issues/2932",
)
def check_metadata_escaped_strings(metadata_file):
    """Ensure METADATA.pb does not use escaped strings."""
    for line in open(metadata_file, "r", encoding="utf-8").readlines():
        # Escaped quotes are fine!
        # What we're really interested in detecting are things like
        # "Juli\303\241n" instead of "Julián"
        line = line.replace("\\'", "")
        line = line.replace('\\"', "")

        for quote_char in ["'", '"']:
            segments = line.split(quote_char)
            if len(segments) >= 3:
                a_string = segments[1]
                if "\\" in a_string:
                    yield FAIL, Message(
                        "escaped-strings",
                        f"Found escaped chars at '{a_string}'."
                        f" Please use an unicode string instead.",
                    )
