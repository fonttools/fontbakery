from fontbakery.prelude import check, PASS, FAIL


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
