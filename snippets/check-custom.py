import os

from fontbakery.checkrunner import Section, PASS, FAIL, WARN, ERROR, INFO, SKIP
from fontbakery.callable import condition, check, disable
from fontbakery.constants import PriorityLevel
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS

profile_imports = ("fontbakery.profiles.universal",)
profile = profile_factory(default_section=Section("Custom Checks"))

# ================================================
#
# Custom check list
#
# ================================================
# define new custom checks that are implemented in
# this source file by check ID.  Format these as a
# Python list.
# The check ID here is an example that demonstrates
# the example pass check in this module.  It is safe
# to remove the check ID when you remove the example
# check from this module
CUSTOM_PROFILE_CHECKS = UNIVERSAL_PROFILE_CHECKS + [
    "org.example/check/valid/testpass",
]

# ================================================
#
# Fontbakery check exclusion list
#
# ================================================
# define check ID's in the upstream `universal` profile
# that should be excluded as a Python tuple
excluded_check_ids = (
    # "com.google.fonts/check/dsig",
)

# ================================================
#
# Example test implementation
#
# ================================================

# The following are example implementations of
# pass and fail checks.  They are commented out
# and are not executed.

# # Test failure template
# @check(
#     id="org.example/check/valid/testfail",
#     rationale="""
#         This is the test failure rationale.
#     """,
# )
# def org_example_check_valid_test_fail():
#     """A test failure example."""
#     yield FAIL, "test failure message"


# # Test pass template
# @check(
#     id="org.example/check/valid/testpass",
#     rationale="""
#         This is the test pass rationale.
#     """,
# )
# def org_example_check_valid_test_pass():
#     """A test pass example."""
#     yield PASS, "test pass message"

# ================================================
#
# Begin check definitions
#
# ================================================

# TEST PASS EXAMPLE
# This check is a live example that is executed when
# you run this custom profile.  It is safe to remove
# this code when you implement your own checks.
@check(
    id="org.example/check/valid/testpass",
    rationale="""
        This is a test pass rationale.
    """,
)
def org_example_check_valid_test_pass():
    """A test pass example."""
    yield PASS, "test pass message"


# ================================================
#
# End check definitions
#
# ================================================

# This function identifies the skipped checks that are
# defined in the `excluded_check_ids` tuple at the head
# of this module.  Do not remove this function unless
# you do not intend to filter checks imported from the
# fontbakery universal profile test suite
def check_skip_filter(checkid, font=None, **iterargs):
    if font and checkid in excluded_check_ids:
        return False, ("Check skipped in Valid project profile")
    return True, None


# You should not need to edit the following block of code
profile.check_skip_filter = check_skip_filter
profile.auto_register(globals())
profile.test_expected_checks(CUSTOM_PROFILE_CHECKS, exclusive=True)
