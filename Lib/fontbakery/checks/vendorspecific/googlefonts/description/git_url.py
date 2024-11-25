from fontbakery.prelude import check, Message, INFO, FAIL


@check(
    id="googlefonts/description/git_url",
    conditions=["description_html", "not is_noto"],
    rationale="""
        The contents of the DESCRIPTION.en-us.html file are displayed on the
        Google Fonts website in the about section of each font family specimen page.

        Since all of the Google Fonts collection is composed of libre-licensed fonts,
        this check enforces a policy that there must be a hypertext link in that page
        directing users to the repository where the font project files are
        made available.

        Such hosting is typically done on sites like Github, Gitlab, GNU Savannah or
        any other git-based version control service.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2523",
)
def check_description_git_url(description_html):
    """Does DESCRIPTION file contain a upstream Git repo URL?"""
    git_urls = []
    for a_href in description_html.iterfind(".//a[@href]"):
        link = a_href.get("href")
        if "://git" in link:
            git_urls.append(link)
            yield INFO, Message("url-found", f"Found a git repo URL: {link}")

    if not git_urls:
        yield FAIL, Message(
            "lacks-git-url",
            "Please host your font project on a public Git repo"
            " (such as GitHub or GitLab) and place a link"
            " in the DESCRIPTION.en_us.html file.",
        )
