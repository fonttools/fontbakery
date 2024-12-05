from fontbakery.prelude import check, WARN, Message


@check(
    id="designspace_has_consistent_groups",
    rationale="""
        Often designers will want kerning groups to be consistent across their
        whole Designspace, so this check helps flag if this isn't the case.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4814",
)
def check_designspace_has_consistent_groups(config, designSpace):
    """Confirms that all sources have the same kerning groups per Designspace."""

    default_source = designSpace.findDefault()
    reference = default_source.font.groups
    for source in designSpace.sources:
        if source is default_source:
            continue
        if source.font.groups != reference:
            yield (
                WARN,
                Message(
                    "mismatched-kerning-groups",
                    f"{source.filename} does not have the same kerning groups as default source.",
                ),
            )
