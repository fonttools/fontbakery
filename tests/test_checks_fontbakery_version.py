from unittest.mock import patch, MagicMock

import pytest
import requests

from conftest import check_id
from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.checks.fontbakery_version import is_up_to_date


@pytest.mark.parametrize(
    "installed, latest, result",
    [
        # True when installed >= latest
        ("0.5.0", "0.5.0", True),
        ("0.5.1", "0.5.0", True),
        ("0.5.1", "0.5.0.post2", True),
        ("2.0.0", "1.5.1", True),
        ("0.8.10", "0.8.9", True),
        ("0.5.2.dev73+g8c9ebc0.d20181023", "0.5.1", True),
        ("0.8.10.dev1+g666b3425", "0.8.9", True),
        ("0.8.10.dev2+gfa9260bf", "0.8.9.post2", True),
        ("0.8.10a9", "0.8.9", True),
        ("0.8.10rc1.dev3+g494879af.d20220825", "0.8.9", True),
        # False when installed < latest
        ("0.4.1", "0.5.0", False),
        ("0.3.4", "0.3.5", False),
        ("1.0.0", "1.0.1", False),
        ("0.8.9", "0.8.10", False),
        ("0.5.0", "0.5.0.post2", False),
        ("0.8.9.dev1+g666b3425", "0.8.9.post2", False),
        ("0.5.2.dev73+g8c9ebc0.d20181023", "0.5.2", False),
        ("0.5.2.dev73+g8c9ebc0.d20181023", "0.5.3", False),
        ("0.8.10rc0", "0.8.10", False),
        ("0.8.10rc0", "0.8.10.post", False),
        ("0.8.10rc1.dev3+g494879af.d20220825", "0.8.10", False),
        ("0.8.10rc1.dev3+g494879af.d20220825", "0.8.10.post", False),
    ],
)
def test_is_up_to_date(installed, latest, result):
    assert is_up_to_date(installed, latest) is result


class MockDistribution:
    """Helper class to mock pip-api's Distribution class."""

    def __init__(self, version: str):
        self.name = "fontbakery"
        self.version = version

    def __repr__(self):
        return f"<Distribution(name='{self.name}', version='{self.version}')>"


# We don't want to make an actual GET request to PyPI.org, so we'll mock it.
# We'll also mock pip-api's 'installed_distributions' method.
@patch("pip_api.installed_distributions")
@patch("requests.get")
def test_check_fontbakery_version(mock_get, mock_installed):
    """Check if FontBakery is up-to-date"""
    from fontbakery.codetesting import CheckTester

    check = CheckTester("fontbakery_version")

    # Any of the test fonts can be used here.
    # The check requires a 'font' argument but it doesn't do anything with it.
    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    mock_response = MagicMock()
    mock_response.status_code = 200

    # Test the case of installed version being the same as PyPI's version.
    latest_ver = installed_ver = "0.1.0"
    mock_response.json.return_value = {"info": {"version": latest_ver}}
    mock_get.return_value = mock_response
    mock_installed.return_value = {"fontbakery": MockDistribution(installed_ver)}
    assert_PASS(check(font))

    # Test the case of installed version being newer than PyPI's version.
    installed_ver = "0.1.1"
    mock_installed.return_value = {"fontbakery": MockDistribution(installed_ver)}
    assert_PASS(check(font))

    # Test the case of installed version being older than PyPI's version.
    installed_ver = "0.0.1"
    mock_installed.return_value = {"fontbakery": MockDistribution(installed_ver)}
    msg = assert_results_contain(check(font), FAIL, "outdated-fontbakery")
    assert (
        f"Current FontBakery version is {installed_ver},"
        f" while a newer {latest_ver} is already available."
    ) in msg

    # Test the case of an unsuccessful response to the GET request.
    mock_response.status_code = 500
    mock_response.content = "500 Internal Server Error"
    msg = assert_results_contain(check(font), FAIL, "unsuccessful-request-500")
    assert "Request to PyPI.org was not successful" in msg

    # Test the case of the GET request failing due to a connection error.
    mock_get.side_effect = requests.exceptions.ConnectionError
    msg = assert_results_contain(check(font), FAIL, "connection-error")
    assert "Request to PyPI.org failed with this message" in msg


@pytest.mark.xfail(reason="Often happens until rebasing")
@check_id("fontbakery_version")
def test_check_fontbakery_version_live_apis(check):
    """Check if FontBakery is up-to-date. (No API-mocking edition)"""

    # Any of the test fonts can be used here.
    # The check requires a 'font' argument but it doesn't do anything with it.
    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    # The check will make an actual request to PyPI.org,
    # and will query 'pip' to determine which version of 'fontbakery' is installed.
    # The check should PASS.
    assert_PASS(check(font))
