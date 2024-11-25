from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="googlefonts/description/broken_links",
    conditions=["network", "description_and_article_html"],
    rationale="""
        The snippet of HTML in the DESCRIPTION.en_us.html/ARTICLE.en_us.html file is
        added to the font family webpage on the Google Fonts website. For that reason,
        all hyperlinks in it must be properly working.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/4110",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_description_broken_links(description_and_article_html, font):
    """Does DESCRIPTION file contain broken links?"""
    import requests

    for source, doc in description_and_article_html.items():
        broken_links = []
        unique_links = []
        for a_href in doc.iterfind(".//a[@href]"):
            link = a_href.get("href")

            # avoid requesting the same URL more then once
            if link in unique_links:
                continue

            if link.startswith("mailto:") and "@" in link and "." in link.split("@")[1]:
                yield FAIL, Message("email", f"Found an email address: {link}")
                continue

            unique_links.append(link)
            try:
                response = requests.head(link, allow_redirects=True, timeout=10)
                code = response.status_code
                # Status 429: "Too Many Requests" is acceptable
                # because it means the website is probably ok and
                # we're just perhaps being too agressive in probing the server!
                if code not in [requests.codes.ok, requests.codes.too_many_requests]:
                    broken_links.append(f"{link} (status code: {code})")
            except requests.exceptions.Timeout:
                yield WARN, Message(
                    "timeout",
                    f"Timedout while attempting to access: '{link}'."
                    f" Please verify if that's a broken link.",
                )
            except requests.exceptions.RequestException:
                broken_links.append(link)

        if broken_links:
            broken_links_list = "\n\t".join(broken_links)
            yield FAIL, Message(
                "broken-links",
                f"The following links are broken"
                f" in the {source} file:\n\t"
                f"{broken_links_list}",
            )
