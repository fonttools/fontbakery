from fontbakery.prelude import check, FAIL


@check(
    id="googlefonts/version_bump",
    conditions=["api_gfonts_ttFont", "github_gfonts_ttFont"],
    rationale="""
        We check that the version number has been bumped since the last release on
        Google Fonts. This helps to ensure that the version being PRed is newer than
        the one currently hosted on fonts.google.com.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_version_bump(ttFont, api_gfonts_ttFont, github_gfonts_ttFont):
    """Version number has increased since previous release on Google Fonts?"""
    v_number = ttFont["head"].fontRevision
    api_gfonts_v_number = api_gfonts_ttFont["head"].fontRevision
    github_gfonts_v_number = github_gfonts_ttFont["head"].fontRevision

    if v_number == api_gfonts_v_number:
        yield FAIL, (
            f"Version number {v_number:0.3f} is equal to version on **Google Fonts**."
        )

    if v_number < api_gfonts_v_number:
        yield FAIL, (
            f"Version number {v_number:0.3f} is less than on"
            f" **Google Fonts** ({api_gfonts_v_number:0.3f})."
        )

    if v_number == github_gfonts_v_number:
        yield FAIL, (
            f"Version number {v_number:0.3f} is equal to version on"
            f" google/fonts **GitHub repo**."
        )

    if v_number < github_gfonts_v_number:
        yield FAIL, (
            f"Version number {v_number:0.3f} is less than on"
            f" google/fonts **GitHub repo** ({github_gfonts_v_number:0.3f})."
        )
