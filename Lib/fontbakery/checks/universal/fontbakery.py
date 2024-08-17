import re

from packaging.version import VERSION_PATTERN

from fontbakery.prelude import FAIL, PASS, Message, check

re_version = re.compile(r"^\s*" + VERSION_PATTERN + r"\s*$", re.VERBOSE | re.IGNORECASE)


def _parse_package_version(version_string: str) -> dict:
    """
    Parses a Python package version string.
    """
    match = re_version.search(version_string)
    if not match:
        raise ValueError(
            f"Python version '{version_string}' was not a valid version string"
        )
    release = match.group("release")
    pre_rel = match.group("pre")
    post_rel = match.group("post")
    dev_rel = match.group("dev")

    # Split MAJOR.MINOR.PATCH numbers, and convert them to integers
    major, minor, patch = map(int, release.split("."))
    version_parts = {
        "major": major,
        "minor": minor,
        "patch": patch,
    }
    # Add the release-kind booleans
    version_parts["pre"] = pre_rel is not None
    version_parts["post"] = post_rel is not None
    version_parts["dev"] = dev_rel is not None

    return version_parts


def is_up_to_date(installed_str, latest_str):
    installed_dict = _parse_package_version(installed_str)
    latest_dict = _parse_package_version(latest_str)

    installed_rel = [*installed_dict.values()][:3]
    latest_rel = [*latest_dict.values()][:3]

    # Compare MAJOR.MINOR.PATCH parts
    for inst_version, last_version in zip(installed_rel, latest_rel):
        if inst_version > last_version:
            return True
        if inst_version < last_version:
            return False

    # All MAJOR.MINOR.PATCH integers are the same between 'installed' and 'latest';
    # therefore FontBakery is up-to-date, unless
    # a) a pre-release is installed or FB is installed in development mode (in which
    #    case the version number installed must be higher), or
    # b) a post-release has been issued.

    installed_is_pre_or_dev_rel = installed_dict.get("pre") or installed_dict.get("dev")
    latest_is_post_rel = latest_dict.get("post")

    return not (installed_is_pre_or_dev_rel or latest_is_post_rel)


@check(
    id="fontbakery_version",
    conditions=["network"],
    rationale="""
        Running old versions of FontBakery can lead to a poor report which may
        include false WARNs and FAILs due do bugs, as well as outdated
        quality assurance criteria.

        Older versions will also not report problems that are detected by new checks
        added to the tool in more recent updates.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2093",
)
def check_fontbakery_version(font, config):
    """Do we have the latest version of FontBakery installed?"""
    import pip_api
    import requests

    try:
        response = requests.get(
            "https://pypi.org/pypi/fontbakery/json", timeout=config.get("timeout")
        )

    except requests.exceptions.ConnectionError as err:
        return FAIL, Message(
            "connection-error",
            f"Request to PyPI.org failed with this message:\n{err}",
        )

    status_code = response.status_code
    if status_code != 200:
        return FAIL, Message(
            f"unsuccessful-request-{status_code}",
            f"Request to PyPI.org was not successful:\n{response.content}",
        )

    latest = response.json()["info"]["version"]
    installed = str(pip_api.installed_distributions()["fontbakery"].version)

    if not is_up_to_date(installed, latest):
        return FAIL, Message(
            "outdated-fontbakery",
            f"Current FontBakery version is {installed},"
            f" while a newer {latest} is already available."
            f" Please upgrade it with 'pip install -U fontbakery'",
        )
    else:
        return PASS, "FontBakery is up-to-date."
