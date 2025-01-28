from fontbakery.prelude import check, Message, ERROR, INFO, PASS


@check(
    id="fontdata_namecheck",
    rationale="""
        We need to check names are not already used, and today the best place to check
        that is http://namecheck.fontdata.com
    """,
    conditions=["network", "familyname"],
    proposal="https://github.com/fonttools/fontbakery/issues/494",
)
def check_fontdata_namecheck(ttFont, familyname):
    """Familyname must be unique according to namecheck.fontdata.com"""
    import requests

    FB_ISSUE_TRACKER = "https://github.com/fonttools/fontbakery/issues"
    API_URL = f"https://namecheck.fontdata.com/api/?q={familyname.replace(' ', '+')}"
    HTML_URL = f"http://namecheck.fontdata.com/?q={familyname.replace(' ', '+')}"
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        # "1.0" means there is a 100% confidence that the name is already in use
        if data["data"]["confidence"]["1.0"] > 0:
            yield INFO, Message(
                "name-collision",
                f'The family name "{familyname}" seems'
                f" to be already in use.\n"
                f"Please visit {HTML_URL} for more info.",
            )
        else:
            yield PASS, "Font familyname seems to be unique."
    except requests.exceptions.RequestException:
        import sys

        yield ERROR, Message(
            "namecheck-service",
            f"Failed to access: {API_URL}.\n"
            f"\t\tThis check relies on the external service"
            f" http://namecheck.fontdata.com via the internet."
            f" While the service cannot be reached or does not"
            f" respond this check is broken.\n"
            f"\n"
            f"\t\tYou can exclude this check with the command line"
            f" option:\n"
            f"\t\t-x fontdata_namecheck\n"
            f"\n"
            f"\t\tOr you can wait until the service is available again.\n"
            f"\t\tIf the problem persists please report this issue"
            f" at: {FB_ISSUE_TRACKER}\n"
            f"\n"
            f"\t\tOriginal error message:\n"
            f"\t\t{sys.exc_info()[0]}",
        )
