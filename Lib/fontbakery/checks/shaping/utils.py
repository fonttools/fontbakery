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
from difflib import ndiff
from pathlib import Path
from os.path import basename

from fontTools.unicodedata import ot_tag_to_script

from fontbakery.prelude import FAIL, PASS, SKIP, Message
from fontbakery.utils import exit_with_install_instructions


def fix_svg(svg):
    svg = svg.replace("<svg", '<svg style="height:100px;margin:10px;"')
    svg = svg.replace("\n", " ")
    return svg


def create_report_item(
    vharfbuzz,
    message,
    text=None,
    buf1=None,
    buf2=None,
    note=None,
    extra_data=None,
):
    from vharfbuzz import FakeBuffer

    message = f"* {message}"
    if text:
        message += f": {text}"
    if note:
        message += f" ({note})"
    if extra_data:
        message += f"\n\n      {extra_data}"
    message += "\n\n"

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
        message += f"      Expected: {serialized_buf2}\n"

    if buf1:
        serialized_buf1 = vharfbuzz.serialize_buf(
            buf1, glyphsonly=(buf2 and isinstance(buf2, str))
        )
        message += f"      Got     : {serialized_buf1}\n"

    # Report a diff table
    if serialized_buf1 and serialized_buf2:
        diff = list(ndiff([serialized_buf1], [serialized_buf2]))
        if diff and diff[-1][0] == "?":
            message += f"               {diff[-1][1:]}\n"

    # Now draw it as SVG
    if buf1:
        message += f"  Got: {fix_svg(vharfbuzz.buf_to_svg(buf1))}"

    if buf2 and isinstance(buf2, FakeBuffer):
        try:
            message += f" Expected: {fix_svg(vharfbuzz.buf_to_svg(buf2))}"
        except KeyError:
            pass

    return message


def get_from_test_with_default(test, configuration, el, default=None):
    defaults = configuration.get("defaults", {})
    return test.get(el, defaults.get(el, default))


def get_shaping_parameters(test, configuration):
    params = {}
    for el in ["script", "language", "direction", "features", "shaper"]:
        params[el] = get_from_test_with_default(test, configuration, el)
    params["variations"] = get_from_test_with_default(
        test, configuration, "variations", {}
    )
    return params


# This is a very generic "do something with shaping" test runner.
# It'll be given concrete meaning later.
def run_a_set_of_shaping_tests(
    config, ttFont, run_a_test, test_filter, generate_report, preparation=None
):
    try:
        from vharfbuzz import Vharfbuzz

        filename = Path(ttFont.reader.file.name)
        vharfbuzz = Vharfbuzz(filename)
    except ImportError:
        exit_with_install_instructions("shaping")

    shaping_file_found = False
    ran_a_test = False
    extra_data = None
    if "shaping" not in config:
        yield SKIP, "Shaping test directory not defined in configuration file"
        return

    shaping_basedir = config["shaping"].get("test_directory")
    if not shaping_basedir:
        yield SKIP, "Shaping test directory not defined in configuration file"
        return

    for shaping_file in Path(shaping_basedir).glob("*.json"):
        shaping_file_found = True
        try:
            shaping_input_doc = json.loads(shaping_file.read_text(encoding="utf-8"))
        except Exception as e:
            yield FAIL, Message(
                "shaping-invalid-json", f"{shaping_file}: Invalid JSON: {e}."
            )
            return

        configuration = shaping_input_doc.get("configuration", {})
        try:
            shaping_tests = shaping_input_doc["tests"]
        except KeyError:
            yield FAIL, Message(
                "shaping-missing-tests",
                f"{shaping_file}: JSON file must have a 'tests' key.",
            )
            return

        if preparation:
            extra_data = preparation(ttFont, configuration)

        failed_shaping_tests = []
        for test in shaping_tests:
            if not test_filter(test, configuration):
                continue

            if "input" not in test:
                yield FAIL, Message(
                    "shaping-missing-input",
                    f"{shaping_file}: test is missing an input key.",
                )
                return

            exclude_fonts = test.get("exclude", [])
            if basename(filename) in exclude_fonts:
                continue

            only_fonts = test.get("only")
            if only_fonts and basename(filename) not in only_fonts:
                continue

            run_a_test(
                filename,
                vharfbuzz,
                test,
                configuration,
                failed_shaping_tests,
                extra_data,
            )
            ran_a_test = True

        if ran_a_test:
            if not failed_shaping_tests:
                yield PASS, f"{shaping_file}: No regression detected"
            else:
                yield from generate_report(
                    vharfbuzz, shaping_file, failed_shaping_tests
                )

    if not shaping_file_found:
        yield SKIP, "No test files found."

    if not ran_a_test:
        yield SKIP, "No applicable tests ran."


def is_complex_shaper_font(ttFont):
    try:
        from ufo2ft.constants import INDIC_SCRIPTS, USE_SCRIPTS
    except ImportError:
        exit_with_install_instructions("shaping")

    for table in ["GSUB", "GPOS"]:
        if table not in ttFont:
            continue
        if not ttFont[table].table.ScriptList:
            continue
        for rec in ttFont[table].table.ScriptList.ScriptRecord:
            script = ot_tag_to_script(rec.ScriptTag)
            if script in USE_SCRIPTS or script in INDIC_SCRIPTS:
                return True
            if script in ["Khmr", "Mymr"]:
                return True
    return False
