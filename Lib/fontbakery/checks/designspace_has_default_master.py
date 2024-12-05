from fontbakery.prelude import check, FAIL, PASS, Message


@check(
    id="designspace_has_default_master",
    rationale="""
        We expect that designspace files declare on of the masters as default.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3168",
)
def check_designspace_has_default_master(designSpace):
    """Ensure a default master is defined."""
    if not designSpace.findDefault():
        yield FAIL, Message("not-found", "Unable to find a default master.")
    else:
        yield PASS, "We located a default master."
