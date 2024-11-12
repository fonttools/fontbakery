from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="ots",
    rationale="""
       The OpenType Sanitizer (OTS) is a tool that checks that the font is
       structually well-formed and passes various sanity checks. It is used by
       many web browsers to check web fonts before using them; fonts which fail
       such checks are blocked by browsers.

       This check runs OTS on the font and reports any errors or warnings that
       it finds.
       """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_ots(font):
    """Checking with ots-sanitize."""
    import ots

    try:
        process = ots.sanitize(font.file, check=True, capture_output=True)

    except ots.CalledProcessError as e:
        yield FAIL, Message(
            "ots-sanitize-error",
            f"ots-sanitize returned an error code ({e.returncode})."
            f" Output follows:\n\n{e.stderr.decode()}{e.stdout.decode()}",
        )
    else:
        if process.stderr:
            yield WARN, Message(
                "ots-sanitize-warn",
                "ots-sanitize passed this file, however warnings were printed:\n\n"
                f"{process.stderr.decode()}",
            )
