from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/repo/upstream_yaml_has_required_fields",
    rationale="""
        If a family has been pushed using the gftools packager, we must check that all
        the required fields in the upstream.yaml file have been populated.
    """,
    conditions=["upstream_yaml"],
    severity=10,
    proposal="https://github.com/fonttools/fontbakery/issues/3338",
)
def check_repo_upstream_yaml_has_required_fields(upstream_yaml):
    """Check upstream.yaml file contains all required fields"""
    required_fields = set(["branch", "files"])
    upstream_fields = set(upstream_yaml.keys())

    missing_fields = required_fields - upstream_fields
    if missing_fields:
        yield FAIL, Message(
            "missing-fields",
            f"The upstream.yaml file is missing the following fields:"
            f" {list(missing_fields)}",
        )
