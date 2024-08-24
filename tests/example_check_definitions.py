from fontbakery.prelude import check, PASS, FAIL


@check(
    id="check_for_testing_configuration",
    rationale="""
        Check that we can inject the configuration object and read it.
    """,
)
def check_for_testing_configuration(config):
    """Check if we can inject a config file"""
    if (
        config
        and "example_profile" in config
        and config["example_profile"]["OK"] == 123
    ):
        yield PASS, "we have injected a config"
    else:
        yield FAIL, "config variable didn't look like we expected"
