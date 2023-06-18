from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL
from fontbakery.fonts_profile import profile_factory

profile = profile_factory(default_section=Section("Just a Test"))


@check(
    id="com.google.fonts/check_for_testing/configuration",
    rationale="""
        Check that we can inject the configuration object and read it.
    """,
)
def com_google_fonts_check_for_testing_configuration(config):
    """Check if we can inject a config file"""
    if config and "a_test_profile" in config and config["a_test_profile"]["OK"] == 123:
        yield PASS, "we have injected a config"
    else:
        yield FAIL, "config variable didn't look like we expected"


profile.auto_register(globals())
