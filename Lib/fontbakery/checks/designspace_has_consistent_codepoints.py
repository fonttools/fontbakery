from fontbakery.prelude import check, FAIL, PASS, Message


@check(
    id="designspace_has_consistent_codepoints",
    rationale="""
        This check ensures that Unicode assignments are consistent
        across all sources specified in a designspace file.
    """,
    conditions=["designspace_sources"],
    proposal="https://github.com/fonttools/fontbakery/pull/3168",
)
def check_designspace_has_consistent_codepoints(designSpace, config):
    """Check codepoints consistency in a designspace file."""
    from fontbakery.utils import bullet_list

    default_source = designSpace.findDefault()
    default_unicodes = {g.name: g.unicode for g in default_source.font}
    failures = []
    for source in designSpace.sources:
        for g in source.font:
            if g.name not in default_unicodes:
                # Previous test will cover this
                continue

            if g.unicode != default_unicodes[g.name]:
                failures.append(
                    f"Source {source.filename} has"
                    f" {g.name}={g.unicode};"
                    f" default master has"
                    f" {g.name}={default_unicodes[g.name]}"
                )
    if failures:
        yield FAIL, Message(
            "inconsistent-codepoints",
            f"Unicode assignments were not consistent:\n\n"
            f"{bullet_list(config, failures)}",
        )
    else:
        yield PASS, "Unicode assignments were consistent."
