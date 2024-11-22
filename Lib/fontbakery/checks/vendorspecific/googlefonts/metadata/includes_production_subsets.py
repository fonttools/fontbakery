from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/includes_production_subsets",
    conditions=["family_metadata", "production_metadata", "listed_on_gfonts_api"],
    rationale="""
        Check METADATA.pb file includes the same subsets as the family in production.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2989",
)
def check_metadata_includes_production_subsets(family_metadata, production_metadata):
    """Check METADATA.pb includes production subsets."""
    prod_families_metadata = {
        i["family"]: i for i in production_metadata["familyMetadataList"]
    }
    prod_family_metadata = prod_families_metadata[family_metadata.name]

    prod_subsets = set(prod_family_metadata["subsets"])
    local_subsets = set(family_metadata.subsets)
    missing_subsets = prod_subsets - local_subsets
    if len(missing_subsets) > 0:
        missing_subsets = ", ".join(sorted(missing_subsets))
        yield FAIL, Message(
            "missing-subsets",
            f"The following subsets are missing [{missing_subsets}]",
        )
