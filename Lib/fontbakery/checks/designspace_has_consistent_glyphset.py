from fontbakery.prelude import check, FAIL, PASS, Message


@check(
    id="designspace_has_consistent_glyphset",
    rationale="""
        This check ensures that non-default masters don't have glyphs
        not present in the default one.
    """,
    conditions=["designspace_sources"],
    proposal="https://github.com/fonttools/fontbakery/pull/3168",
)
def check_designspace_has_consistent_glyphset(designSpace, config):
    """Check consistency of glyphset in a designspace file."""
    from fontbakery.utils import bullet_list

    default_glyphset = set(designSpace.findDefault().font.keys())
    failures = []
    for source in designSpace.sources:
        master_glyphset = set(source.font.keys())
        outliers = master_glyphset - default_glyphset
        if outliers:
            outliers = ", ".join(list(outliers))
            failures.append(
                f"Source {source.filename} has glyphs not present"
                f" in the default master: {outliers}"
            )
    if failures:
        yield FAIL, Message(
            "inconsistent-glyphset",
            f"Glyphsets were not consistent:\n\n" f"{bullet_list(config, failures)}",
        )
    else:
        yield PASS, "Glyphsets were consistent."
