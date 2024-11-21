from fontbakery.prelude import check, FAIL, Message
from fontbakery.checks.shaping.utils import (
    create_report_item,
    get_shaping_parameters,
    run_a_set_of_shaping_tests,
)


def run_shaping_regression(
    filename, vharfbuzz, test, configuration, failed_shaping_tests, extra_data
):
    shaping_text = test["input"]
    parameters = get_shaping_parameters(test, configuration)
    output_buf = vharfbuzz.shape(shaping_text, parameters)
    expectation = test["expectation"]
    if isinstance(expectation, dict):
        expectation = expectation.get(filename.name, expectation["default"])
    output_serialized = vharfbuzz.serialize_buf(
        output_buf, glyphsonly="+" not in expectation
    )

    if output_serialized != expectation:
        failed_shaping_tests.append((test, expectation, output_buf, output_serialized))


def generate_shaping_regression_report(vharfbuzz, shaping_file, failed_shaping_tests):
    report_items = []
    for test, expected, output_buf, output_serialized in failed_shaping_tests:
        extra_data = {
            k: test[k]
            for k in ["script", "language", "direction", "features", "variations"]
            if k in test
        }
        # Make HTML report here.
        if "=" in expected:
            buf2 = vharfbuzz.buf_from_string(expected)
        else:
            buf2 = expected

        report_item = create_report_item(
            vharfbuzz,
            "Shaping did not match",
            text=test["input"],
            buf1=output_buf,
            buf2=buf2,
            note=test.get("note"),
            extra_data=extra_data,
        )
        report_items.append(report_item)

    header = f"{shaping_file}: Expected and actual shaping not matching"
    yield FAIL, Message("shaping-regression", header + "\n" + "\n".join(report_items))


@check(
    id="shaping/regression",
    rationale="""
        Fonts with complex layout rules can benefit from regression tests to ensure
        that the rules are behaving as designed. This checks runs a shaping test
        suite and compares expected shaping against actual shaping, reporting
        any differences.

        Shaping test suites should be written by the font engineer and referenced
        in the FontBakery configuration file. For more information about write
        shaping test files and how to configure FontBakery to read the shaping
        test suites, see https://simoncozens.github.io/tdd-for-otl/
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3223",
)
def check_shaping_regression(config, ttFont):
    """Check that texts shape as per expectation"""
    yield from run_a_set_of_shaping_tests(
        config,
        ttFont,
        run_shaping_regression,
        lambda test, configuration: "expectation" in test,
        generate_shaping_regression_report,
    )
