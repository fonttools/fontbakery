from pathlib import Path

from fontbakery.prelude import check, FAIL, Message
from fontbakery.utils import exit_with_install_instructions
from fontbakery.checks.shaping.utils import (
    create_report_item,
    fix_svg,
    get_from_test_with_default,
    get_shaping_parameters,
    run_a_set_of_shaping_tests,
)


@check(
    id="shaping/collides",
    rationale="""
        Fonts with complex layout rules can benefit from regression tests to ensure
        that the rules are behaving as designed. This checks runs a shaping test
        suite and reports instances where the glyphs collide in unexpected ways.

        Shaping test suites should be written by the font engineer and referenced
        in the FontBakery configuration file. For more information about write
        shaping test files and how to configure FontBakery to read the shaping
        test suites, see https://simoncozens.github.io/tdd-for-otl/
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3223",
)
def check_shaping_collides(config, ttFont):
    """Check that no collisions are found while shaping"""
    yield from run_a_set_of_shaping_tests(
        config,
        ttFont,
        run_collides_glyph_test,
        lambda test, configuration: "collidoscope" in test
        or "collidoscope" in configuration,
        collides_glyph_test_results,
        setup_glyph_collides,
    )


def setup_glyph_collides(ttFont, configuration):
    try:
        from collidoscope import Collidoscope
    except ImportError:
        exit_with_install_instructions("shaping")

    filename = Path(ttFont.reader.file.name)
    collidoscope_configuration = configuration.get("collidoscope")
    if not collidoscope_configuration:
        return {
            "bases": True,
            "marks": True,
            "faraway": True,
            "adjacent_clusters": True,
        }
    col = Collidoscope(
        filename,
        collidoscope_configuration,
        direction=configuration.get("direction", "LTR"),
    )
    return {"collidoscope": col}


def run_collides_glyph_test(
    filename, vharfbuzz, test, configuration, failed_shaping_tests, extra_data
):
    try:
        from stringbrewer import StringBrewer
    except ImportError:
        exit_with_install_instructions("shaping")

    col = extra_data["collidoscope"]
    is_stringbrewer = (
        get_from_test_with_default(test, configuration, "input_type", "string")
        == "pattern"
    )
    parameters = get_shaping_parameters(test, configuration)
    allowed_collisions = get_from_test_with_default(
        test, configuration, "allowedcollisions", []
    )
    if is_stringbrewer:
        sb = StringBrewer(
            recipe=test["input"], ingredients=configuration["ingredients"]
        )
        strings = sb.generate_all()
    else:
        strings = [test["input"]]

    for shaping_text in strings:
        output_buf = vharfbuzz.shape(shaping_text, parameters)
        glyphs = col.get_glyphs(shaping_text, buf=output_buf)
        collisions = col.has_collisions(glyphs)
        bumps = [f"{c.glyph1}/{c.glyph2}" for c in collisions]
        bumps = [b for b in bumps if b not in allowed_collisions]
        if bumps:
            draw = fix_svg(col.draw_overlaps(glyphs, collisions))
            failed_shaping_tests.append((shaping_text, bumps, draw, output_buf))


def collides_glyph_test_results(vharfbuzz, shaping_file, failed_shaping_tests):
    report_items = []
    seen_bumps = {}
    for shaping_text, bumps, draw, buf in failed_shaping_tests:
        # Make HTML report here.
        if tuple(bumps) in seen_bumps:
            continue
        seen_bumps[tuple(bumps)] = True
        report_item = create_report_item(
            vharfbuzz,
            f"{',' .join(bumps)} collision found in"
            f" e.g. <span class='tf'>{shaping_text}</span> <div>{draw}</div>",
            buf1=buf,
        )
        report_items.append(report_item)
    header = (
        f"{shaping_file}: {len(failed_shaping_tests)} collisions found while shaping"
    )
    yield FAIL, Message("shaping-collides", header + ".\n" + "\n".join(report_items))
