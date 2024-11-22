from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="googlefonts/metadata/broken_links",
    conditions=["network", "family_metadata"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/2550",
        "https://github.com/fonttools/fontbakery/issues/4110",
    ],
    rationale="""
        This check ensures that any URLs found within the copyright
        field of the METADATA.pb file are valid.
    """,
)
def check_metadata_broken_links(family_metadata):
    """Does METADATA.pb copyright field contain broken links?"""
    import requests

    broken_links = []
    unique_links = []
    for font_metadata in family_metadata.fonts:
        copyright_str = font_metadata.copyright
        if "mailto:" in copyright_str:
            # avoid reporting more then once
            if copyright_str in unique_links:
                continue

            unique_links.append(copyright_str)
            yield FAIL, Message("email", f"Found an email address: {copyright_str}")
            continue

        if "http" in copyright_str:
            link = "http" + copyright_str.split("http")[1]

            for endchar in [" ", ")"]:
                if endchar in link:
                    link = link.split(endchar)[0]

            # avoid requesting the same URL more then once
            if link in unique_links:
                continue

            unique_links.append(link)
            try:
                response = requests.head(link, allow_redirects=True, timeout=10)
                code = response.status_code
                # Status 429: "Too Many Requests" is acceptable
                # because it means the website is probably ok and
                # we're just perhaps being too agressive in probing the server!
                if code not in [requests.codes.ok, requests.codes.too_many_requests]:
                    # special case handling for github.com/$user/$repo/$something
                    chunks = link.split("/")
                    good = False
                    if len(chunks) == 6 and chunks[2].endswith("github.com"):
                        protocol, _, domain, user, repo, something = chunks
                        for branch in ["main", "master"]:
                            alternate_link = (
                                f"{protocol}//{domain}/{user}/"
                                f"{repo}/tree/{branch}/{something}"
                            )
                            response = requests.head(
                                alternate_link, allow_redirects=True, timeout=10
                            )
                            code = response.status_code
                            if code in [
                                requests.codes.ok,
                                requests.codes.too_many_requests,
                            ]:
                                yield WARN, Message(
                                    "bad-github-url",
                                    f"Could not fetch '{link}'.\n\n"
                                    f"But '{alternate_link}' seems to be good."
                                    f" Please consider using that instead.\n",
                                )
                                good = True
                    if not good:
                        broken_links.append(f"{link} (status code: {code})")
            except requests.exceptions.Timeout:
                yield WARN, Message(
                    "timeout",
                    f"Timed out while attempting to access: '{link}'."
                    f" Please verify if that's a broken link.",
                )
            except requests.exceptions.RequestException:
                broken_links.append(link)

    if len(broken_links) > 0:
        broken_links_list = "\n\t".join(broken_links)
        yield FAIL, Message(
            "broken-links",
            f"The following links are broken in the METADATA.pb file:\n"
            f"\t{broken_links_list}",
        )
