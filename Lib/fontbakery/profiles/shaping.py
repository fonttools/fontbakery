# Copyright 2020 Google Sans Authors
# Copyright 2021 Simon Cozens

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import sys
import textwrap
from difflib import ndiff
from pathlib import Path
from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, SKIP
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.section import Section
from vharfbuzz import Vharfbuzz, FakeBuffer
from os.path import basename, relpath
from stringbrewer import StringBrewer
from collidoscope import Collidoscope

shaping_basedir = Path("qa", "shaping_tests")

profile_imports = ()
profile = profile_factory(default_section=Section("Shaping Checks"))

SHAPING_PROFILE_CHECKS = [
    "com.google.fonts/check/shaping/regression",
    "com.google.fonts/check/shaping/forbidden",
    "com.google.fonts/check/shaping/collides",
]

STYLESHEET = """
<style type="text/css">
    @font-face {font-family: "TestFont"; src: url(%s);}
    .tf { font-family: "TestFont"; }
    .shaping pre { font-size: 1.2rem; }
    .shaping li {
        font-size: 1.2rem;
        border-top: 1px solid #ddd;
        padding: 12px;
        margin-top: 12px;
    }
    .shaping-svg {
        height: 100px;
        margin: 10px;
        transform: matrix(1, 0, 0, -1, 0, 0);
    }
</style>
"""


def get_stylesheet(vharfbuzz):
    filename = Path(vharfbuzz.filename)
    return STYLESHEET % relpath(filename, shaping_basedir)


def fix_svg(svg):
    return svg.replace('<svg', '<svg class="shaping-svg"')


def create_report_item(vharfbuzz,
                       message,
                       text=None,
                       buf1=None,
                       buf2=None,
                       type="item",
                       note=None,
                       extra_data=None):
    if text:
        message += f': <span class="tf">{text}</span>'

    if type == "item":
        message = f"<li>{message}"
        if note:
            message += f" ({note})"
        message += "</li>\n"
    elif type == "header":
        message = get_stylesheet(vharfbuzz) + f"\n<h4>{message}</h4>\n"

    if extra_data:
        message += f"\n\n<pre>{extra_data}</pre>\n\n"

    serialized_buf1 = None
    serialized_buf2 = None
    if buf2:
        if isinstance(buf2, FakeBuffer):
            try:
                serialized_buf2 = vharfbuzz.serialize_buf(buf2)
            except Exception:
                # This may fail if the glyphs are not found in the font
                serialized_buf2 = None
                buf2 = None  # Don't try to draw it either
        else:
            serialized_buf2 = buf2
        message += f"\n\n<pre>Expected: {serialized_buf2}</pre>\n\n"

    if buf1:
        serialized_buf1 = vharfbuzz.serialize_buf(buf1,
                                                  glyphsonly=(buf2 and
                                                              isinstance(buf2, str)))
        message += f"\n\n<pre>Got     : {serialized_buf1}</pre>\n\n"

    # Report a diff table
    if serialized_buf1 and serialized_buf2:
        diff = list(ndiff([serialized_buf1], [serialized_buf2]))
        if diff and diff[-1][0] == "?":
            message += f"\n\n<pre>         {diff[-1][1:]}</pre>\n\n"

    # Now draw it as SVG
    if buf1:
        message += "\nGot: " + fix_svg(vharfbuzz.buf_to_svg(buf1))

    if buf2 and isinstance(buf2, FakeBuffer):
        try:
            message += " Expected: " + fix_svg(vharfbuzz.buf_to_svg(buf2))
        except KeyError:
            pass

    return f'<div class="shaping">\n\n{message}\n\n</div>'


def get_from_test_with_default(test, configuration, el, default=None):
    defaults = configuration.get("defaults", {})
    return test.get(el, defaults.get(el, default))


def get_shaping_parameters(test, configuration):
    params = {}
    for el in ["script", "language", "direction", "features", "shaper"]:
        params[el] = get_from_test_with_default(test, configuration, el)
    return params


# This is a very generic "do something with shaping" test runner.
# It'll be given concrete meaning later.
def run_a_set_of_shaping_tests(config,
                               ttFont,
                               run_a_test,
                               test_filter,
                               generate_report,
                               preparation=None):
    filename = Path(ttFont.reader.file.name)
    vharfbuzz = Vharfbuzz(filename)
    shaping_file_found = False
    ran_a_test = False
    extra_data = None
    if "com.google.fonts/check/shaping" not in config:
        yield SKIP, "Shaping test directory not defined in configuration file"
        return

    shaping_basedir = config["com.google.fonts/check/shaping"].get("test_directory")
    if not shaping_basedir:
        yield SKIP, "Shaping test directory not defined in configuration file"
        return

    for shaping_file in Path(shaping_basedir).glob("*.json"):
        shaping_file_found = True
        try:
            shaping_input_doc = json.loads(shaping_file.read_text(encoding="utf-8"))
        except Exception as e:
            yield FAIL,\
                  Message("shaping-invalid-json",
                          f"{shaping_file}: Invalid JSON: {e}.")
            return

        configuration = shaping_input_doc.get("configuration", {})
        try:
            shaping_tests = shaping_input_doc["tests"]
        except KeyError:
            yield FAIL,\
                  Message("shaping-missing-tests",
                          f"{shaping_file}: JSON file must have a 'tests' key.")
            return

        if preparation:
            extra_data = preparation(ttFont, configuration)

        failed_shaping_tests = []
        for test in shaping_tests:
            if not test_filter(test, configuration):
                continue

            if not "input" in test:
                yield FAIL,\
                      Message("shaping-missing-input",
                              f"{shaping_file}: test is missing an input key.")
                return

            exclude_fonts = test.get("exclude", [])
            if basename(filename) in exclude_fonts:
                continue

            only_fonts = test.get("only")
            if only_fonts and basename(filename) not in only_fonts:
                continue

            run_a_test(filename,
                       vharfbuzz,
                       test,
                       configuration,
                       failed_shaping_tests,
                       extra_data)
            ran_a_test = True

        if ran_a_test:
            if not failed_shaping_tests:
                yield PASS, f"{shaping_file}: No regression detected"
            else:
                yield from generate_report(vharfbuzz,
                                           shaping_file,
                                           failed_shaping_tests)

    if not shaping_file_found:
        yield SKIP, "No test files found."

    if not ran_a_test:
        yield SKIP, "No applicable tests ran."


@check(
    id = "com.google.fonts/check/shaping/regression",
    rationale = """
        Fonts with complex layout rules can benefit from regression tests to ensure
        that the rules are behaving as designed. This checks runs a shaping test
        suite and compares expected shaping against actual shaping, reporting
        any differences.
        
        Shaping test suites should be written by the font engineer and referenced
        in the fontbakery configuration file. For more information about write
        shaping test files and how to configure fontbakery to read the shaping
        test suites, see https://simoncozens.github.io/tdd-for-otl/
    """,
    proposal = "https://github.com/googlefonts/fontbakery/pull/3223"
)
def com_google_fonts_check_shaping_regression(config, ttFont):
    """Check that texts shape as per expectation"""
    yield from run_a_set_of_shaping_tests(
        config,
        ttFont,
        run_shaping_regression,
        lambda test, configuration: "expectation" in test,
        gereate_shaping_regression_report,
    )


def run_shaping_regression(filename,
                           vharfbuzz,
                           test,
                           configuration,
                           failed_shaping_tests,
                           extra_data):
    shaping_text = test["input"]
    parameters = get_shaping_parameters(test, configuration)
    output_buf = vharfbuzz.shape(shaping_text, parameters)
    expectation = test["expectation"]
    if isinstance(expectation, dict):
        expectation = expectation.get(filename.name, expectation["default"])
    output_serialized = vharfbuzz.serialize_buf(output_buf,
                                                glyphsonly="+" not in expectation)

    if output_serialized != expectation:
        failed_shaping_tests.append((test, expectation, output_buf, output_serialized))


def gereate_shaping_regression_report(vharfbuzz, shaping_file, failed_shaping_tests):
    report_items = []
    header = f"{shaping_file}: Expected and actual shaping not matching"
    report_items.append(create_report_item(vharfbuzz, header, type="header"))
    for test, expected, output_buf, output_serialized in failed_shaping_tests:
        extra_data = {
            k: test[k]
            for k in ["script", "language", "direction", "features"]
            if k in test
        }
        # Make HTML report here.
        if "=" in expected:
            buf2 = vharfbuzz.buf_from_string(expected)
        else:
            buf2 = expected

        report_item = create_report_item(vharfbuzz,
                                         "Shaping did not match",
                                         text=test["input"],
                                         buf1=output_buf,
                                         buf2=buf2,
                                         note=test.get("note"),
                                         extra_data=extra_data)
        report_items.append(report_item)

    yield FAIL,\
          Message("shaping-regression",
                  header + "\n" + "\n".join(report_items))


@check(
    id="com.google.fonts/check/shaping/forbidden",
    rationale="""
        Fonts with complex layout rules can benefit from regression tests to ensure
        that the rules are behaving as designed. This checks runs a shaping test
        suite and reports if any glyphs are generated in the shaping which should
        not be produced. (For example, .notdef glyphs, visible viramas, etc.)
        
        Shaping test suites should be written by the font engineer and referenced in
        the Font Bakery configuration file. For more information about write shaping
        test files and how to configure fontbakery to read the shaping test suites,
        see https://simoncozens.github.io/tdd-for-otl/
    """,
    proposal = "https://github.com/googlefonts/fontbakery/pull/3223"
)
def com_google_fonts_check_shaping_forbidden(config, ttFont):
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
    msg = f"{shaping_file}: Forbidden glyphs found while shaping"
    report_items.append(create_report_item(vharfbuzz, msg, type="header"))
    for shaping_text, buf, forbidden in failed_shaping_tests:
        msg = f"{shaping_text} produced '{forbidden}'"
        report_items.append(create_report_item(vharfbuzz,
                                               msg,
                                               text=shaping_text,
                                               buf1=buf))

    yield FAIL,\
          Message("shaping-forbidden",
                  msg + ".\n" + "\n".join(report_items))


@check(
    id = "com.google.fonts/check/shaping/collides",
    rationale = """
        Fonts with complex layout rules can benefit from regression tests to ensure
        that the rules are behaving as designed. This checks runs a shaping test
        suite and reports instances where the glyphs collide in unexpected ways.
        
        Shaping test suites should be written by the font engineer and referenced
        in the fontbakery configuration file. For more information about write
        shaping test files and how to configure fontbakery to read the shaping
        test suites, see https://simoncozens.github.io/tdd-for-otl/
    """,
    proposal = "https://github.com/googlefonts/fontbakery/pull/3223"
)
def com_google_fonts_check_shaping_collides(config, ttFont):
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
    filename = Path(ttFont.reader.file.name)
    collidoscope_configuration = configuration.get("collidoscope")
    if not collidoscope_configuration:
        return {
            "bases": True,
            "marks": True,
            "faraway": True,
            "adjacent_clusters": True,
        }
    col = Collidoscope(filename,
                       collidoscope_configuration,
                       direction=configuration.get("direction", "LTR"))
    return {"collidoscope": col}


def run_collides_glyph_test(filename,
                            vharfbuzz,
                            test,
                            configuration,
                            failed_shaping_tests,
                            extra_data):
    col = extra_data["collidoscope"]
    is_stringbrewer = get_from_test_with_default(test,
                                                 configuration,
                                                 "input_type",
                                                 "string") == "pattern"
    parameters = get_shaping_parameters(test, configuration)
    allowed_collisions = get_from_test_with_default(test,
                                                    configuration,
                                                    "allowedcollisions",
                                                    [])
    if is_stringbrewer:
        sb = StringBrewer(recipe=test["input"],
                          ingredients=configuration["ingredients"])
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
    msg = f"{shaping_file}: {len(failed_shaping_tests)} collisions found while shaping"
    report_items.append(create_report_item(vharfbuzz, msg, type="header"))
    for shaping_text, bumps, draw, buf in failed_shaping_tests:
        # Make HTML report here.
        if tuple(bumps) in seen_bumps:
            continue
        seen_bumps[tuple(bumps)] = True
        report_item = create_report_item(vharfbuzz,
                                         f"{',' .join(bumps)} collision found in"
                                         f" e.g. <span class='tf'>{shaping_text}</span>"
                                         f" <div>{draw}</div>",
                                         buf1=buf)
        report_items.append(report_item)
    yield FAIL,\
          Message("shaping-collides",
                  msg + ".\n" + "\n".join(report_items))


profile.auto_register(globals())
profile.test_expected_checks(SHAPING_PROFILE_CHECKS, exclusive=True)
