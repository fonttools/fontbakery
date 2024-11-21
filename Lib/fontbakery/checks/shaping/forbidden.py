from fontbakery.prelude import check, FAIL, Message
from fontbakery.checks.shaping.utils import (
    create_report_item,
    get_from_test_with_default,
    get_shaping_parameters,
    run_a_set_of_shaping_tests,
)


@check(
    id="shaping/forbidden",
    rationale="""
        Fonts with complex layout rules can benefit from regression tests to ensure
        that the rules are behaving as designed. This checks runs a shaping test
        suite and reports if any glyphs are generated in the shaping which should
        not be produced. (For example, .notdef glyphs, visible viramas, etc.)

        Shaping test suites should be written by the font engineer and referenced in
        the FontBakery configuration file. For more information about write shaping
        test files and how to configure FontBakery to read the shaping test suites,
        see https://simoncozens.github.io/tdd-for-otl/
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3223",
)
def check_shaping_forbidden(config, ttFont):
    """Check that no forbidden glyphs are found while shaping"""
    yield from run_a_set_of_shaping_tests(
        config,
        ttFont,
        run_forbidden_glyph_test,
        lambda test, configuration: "forbidden_glyphs" in configuration,
        forbidden_glyph_test_results,
    )


def run_forbidden_glyph_test(
    filename, vharfbuzz, test, configuration, failed_shaping_tests, extra_data
):
    from stringbrewer import StringBrewer

    is_stringbrewer = (
        get_from_test_with_default(test, configuration, "input_type", "string")
        == "pattern"
    )
    parameters = get_shaping_parameters(test, configuration)
    forbidden_glyphs = configuration["forbidden_glyphs"]
    if is_stringbrewer:
        sb = StringBrewer(
            recipe=test["input"], ingredients=configuration["ingredients"]
        )
        strings = sb.generate_all()
    else:
        strings = [test["input"]]

    for shaping_text in strings:
        output_buf = vharfbuzz.shape(shaping_text, parameters)
        output_serialized = vharfbuzz.serialize_buf(output_buf, glyphsonly=True)
        glyph_names = output_serialized.split("|")
        for forbidden in forbidden_glyphs:
            if forbidden in glyph_names:
                failed_shaping_tests.append((shaping_text, output_buf, forbidden))


def forbidden_glyph_test_results(vharfbuzz, shaping_file, failed_shaping_tests):
    report_items = []
    for shaping_text, buf, forbidden in failed_shaping_tests:
        msg = f"{shaping_text} produced '{forbidden}'"
        report_items.append(
            create_report_item(vharfbuzz, msg, text=shaping_text, buf1=buf)
        )

    header = f"{shaping_file}: Forbidden glyphs found while shaping"
    yield FAIL, Message("shaping-forbidden", header + ".\n" + "\n".join(report_items))
