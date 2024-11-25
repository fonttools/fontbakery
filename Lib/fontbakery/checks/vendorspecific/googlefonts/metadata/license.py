from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/license",
    conditions=["family_metadata"],
    rationale="""
        The license field in METADATA.pb must contain one of the
        three values "APACHE2", "UFL" or "OFL". (New fonts should
        generally be OFL unless there are special circumstances.)
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_license(family_metadata):
    """METADATA.pb license is "APACHE2", "UFL" or "OFL"?"""
    expected_licenses = ["APACHE2", "OFL", "UFL"]
    if family_metadata.license not in expected_licenses:
        yield FAIL, Message(
            "bad-license",
            f'METADATA.pb license field ("{family_metadata.license}")'
            f" must be one of the following: {expected_licenses}",
        )
