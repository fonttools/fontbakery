from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/consistent_repo_urls",
    conditions=["family_metadata"],
    rationale="""
        Sometimes, perhaps due to copy-pasting, projects may declare different URLs
        between the font.coyright and the family.sources.repository_url fields.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4056",
)
def check_metadata_consistent_repo_urls(
    config, family_metadata, license_contents, is_ofl, description
):
    """
    METADATA.pb: Check URL on copyright string is the same as in repository_url field.
    """
    repo_url = family_metadata.source.repository_url
    if not repo_url:
        yield FAIL, Message(
            "lacks-repo-url", "Please add a family.source.repository_url entry."
        )
        return

    import re

    A_GITHUB_URL = r"github.com/[\w-]+/[\w-]+"

    def clean_url(url):
        if ")" in url:
            url = url.split(")")[0].strip()
        if url.endswith("/"):
            url = url[:-1]
        if url.endswith(".git"):
            url = url[:-4]
        return url

    bad_urls = []
    repo_url = clean_url(family_metadata.source.repository_url)
    a_url = repo_url

    for font_md in family_metadata.fonts:
        if "http" in font_md.copyright:
            link = clean_url("http" + font_md.copyright.split("http")[1])
            if not a_url:
                a_url = link
            elif link != repo_url:
                bad_urls.append(("font copyright string", link))

    if is_ofl and license_contents:
        string = license_contents.strip().split("\n")[0]
        if "http" in string:
            link = clean_url("http" + string.split("http")[1])
            if not a_url:
                a_url = link
            elif clean_url(link) != a_url:
                bad_urls.append(("OFL text", link))

    if a_url and description:
        headless = re.sub(r"^https?://", "", a_url)
        for match in set(re.findall(A_GITHUB_URL, description)):
            if clean_url(match) != headless:
                bad_urls.append(("HTML description", match))

    if bad_urls:
        from fontbakery.utils import pretty_print_list

        bad_urls = pretty_print_list(
            config, [f"{location} has '{url}'" for location, url in bad_urls]
        )
        yield FAIL, Message(
            "mismatch",
            f"Repository URL is {a_url}\n\nBut: {bad_urls}\n",
        )
