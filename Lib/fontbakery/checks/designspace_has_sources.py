from fontbakery.prelude import check, FAIL, PASS, Message


@check(
    id="designspace_has_sources",
    rationale="""
        This check parses a designspace file and tries to load the
        source files specified.

        This is meant to ensure that the file is not malformed,
        can be properly parsed and does include valid source file references.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3168",
)
def check_designspace_has_sources(designspace_sources):
    """See if we can actually load the source files."""
    if not designspace_sources:
        yield FAIL, Message("no-sources", "Unable to load source files.")
    else:
        yield PASS, "OK"
