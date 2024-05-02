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

from fontbakery.prelude import check, FAIL, PASS, SKIP, WARN, Message
from fontbakery.utils import exit_with_install_instructions

shaping_basedir = Path("qa", "shaping_tests")


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


@check(
    id="com.google.fonts/check/shaping/regression",
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
def com_google_fonts_check_shaping_regression(config, ttFont):
    """Check that texts shape as per expectation"""
    yield from run_a_set_of_shaping_tests(
        config,
        ttFont,
        run_shaping_regression,
        lambda test, configuration: "expectation" in test,
        generate_shaping_regression_report,
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
    id="com.google.fonts/check/shaping/forbidden",
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


@check(
    id="com.google.fonts/check/shaping/collides",
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


@check(
    id="com.google.fonts/check/dotted_circle",
    conditions=["is_ttf"],
    severity=3,
    rationale="""
        The dotted circle character (U+25CC) is inserted by shaping engines before
        mark glyphs which do not have an associated base, especially in the context
        of broken syllabic clusters.

        For fonts containing combining marks, it is recommended that the dotted circle
        character be included so that these isolated marks can be displayed properly;
        for fonts supporting complex scripts, this should be considered mandatory.

        Additionally, when a dotted circle glyph is present, it should be able to
        display all marks correctly, meaning that it should contain anchors for all
        attaching marks.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3600",
)
def com_google_fonts_check_dotted_circle(ttFont, config):
    """Ensure dotted circle glyph is present and can attach marks."""
    from fontbakery.utils import bullet_list, iterate_lookup_list_with_extensions

    mark_glyphs = []
    if (
        "GDEF" in ttFont
        and hasattr(ttFont["GDEF"].table, "GlyphClassDef")
        and hasattr(ttFont["GDEF"].table.GlyphClassDef, "classDefs")
    ):
        mark_glyphs = [
            k for k, v in ttFont["GDEF"].table.GlyphClassDef.classDefs.items() if v == 3
        ]

    # Only check for encoded
    mark_glyphs = set(mark_glyphs) & set(ttFont.getBestCmap().values())
    nonspacing_mark_glyphs = [g for g in mark_glyphs if ttFont["hmtx"][g][0] == 0]

    if not nonspacing_mark_glyphs:
        yield SKIP, "Font has no nonspacing mark glyphs."
        return

    if 0x25CC not in ttFont.getBestCmap():
        # How bad is this?
        if is_complex_shaper_font(ttFont):
            yield FAIL, Message(
                "missing-dotted-circle-complex",
                "No dotted circle glyph present and font uses a complex shaper",
            )
        else:
            yield WARN, Message(
                "missing-dotted-circle", "No dotted circle glyph present"
            )
        return

    # Check they all attach to dotted circle
    # if they attach to something else
    dotted_circle = ttFont.getBestCmap()[0x25CC]
    attachments = {dotted_circle: []}
    does_attach = {}

    def find_mark_base(lookup, attachments):
        if lookup.LookupType == 4:
            # Assume all-to-all
            for st in lookup.SubTable:
                for base in st.BaseCoverage.glyphs:
                    for mark in st.MarkCoverage.glyphs:
                        attachments.setdefault(base, []).append(mark)
                        does_attach[mark] = True

    iterate_lookup_list_with_extensions(ttFont, "GPOS", find_mark_base, attachments)

    unattached = []
    for g in nonspacing_mark_glyphs:
        if g in does_attach and g not in attachments[dotted_circle]:
            unattached.append(g)

    if unattached:
        yield FAIL, Message(
            "unattached-dotted-circle-marks",
            "The following glyphs could not be attached to the dotted circle glyph:\n\n"
            f"{bullet_list(config, sorted(unattached))}",
        )
    else:
        yield PASS, "All marks were anchored to dotted circle"


@check(
    id="com.google.fonts/check/soft_dotted",
    severity=3,
    rationale="""
        An accent placed on characters with a "soft dot", like i or j, causes
        the dot to disappear.
        An explicit dot above can be added where required.
        See "Diacritics on i and j" in Section 7.1, "Latin" in The Unicode Standard.

        Characters with the Soft_Dotted property are listed in
        https://www.unicode.org/Public/UCD/latest/ucd/PropList.txt

        See also:
        https://googlefonts.github.io/gf-guide/diacritics.html#soft-dotted-glyphs
    """,
    conditions=[
        "network"
    ],  # use Shaperglot, which uses youseedee, which downloads Unicode files
    proposal="https://github.com/fonttools/fontbakery/issues/4059",
)
def com_google_fonts_check_soft_dotted(ttFont):
    """Ensure soft_dotted characters lose their dot when combined with marks that
    replace the dot."""
    try:
        from vharfbuzz import Vharfbuzz
    except ImportError:
        exit_with_install_instructions("shaping")

    import itertools
    from beziers.path import BezierPath
    from fontTools import unicodedata

    cmap = ttFont["cmap"].getBestCmap()

    # Soft dotted strings know to be used in orthographies.
    ortho_soft_dotted_strings = set(
        "i̋ i̍ i᷆ i᷇ i̓ i̊ i̐ ɨ́ ɨ̀ ɨ̂ ɨ̋ ɨ̏ ɨ̌ ɨ̄ ɨ̃ ɨ̈ ɨ̧́ ɨ̧̀ ɨ̧̂ ɨ̧̌ ɨ̱́ ɨ̱̀ ɨ̱̈ "
        "į́ į̀ į̂ į̄ į̄́ į̄̀ į̄̂ į̄̌ į̃ į̌ ị́ ị̀ ị̂ ị̄ ị̃ ḭ́ ḭ̀ ḭ̄ j́ j̀ j̄ j̑ j̃ "
        "j̈ і́".split()
    )
    # Characters with Soft_Dotted property in Unicode.
    soft_dotted_chars = set(
        ord(c) for c in "iⅈ𝐢𝑖𝒊𝒾𝓲𝔦𝕚𝖎𝗂𝗶𝘪𝙞𝚒ⁱᵢįịḭɨᶤ𝼚ᶖjⅉ𝐣𝑗𝒋𝒿𝓳𝔧𝕛𝖏𝗃𝗷𝘫𝙟𝚓ʲⱼɉʝᶨϳіј"
    ) & set(cmap.keys())
    # Only check above marks used with Latin, Greek, Cyrillic scripts.
    mark_above_chars = set(
        (
            c
            for c in cmap.keys()
            if unicodedata.combining(chr(c)) == 230
            and unicodedata.block(chr(c)).startswith(
                ("Combining Diacritical Marks", "Cyrillic")
            )
        )
    )
    # Only check non above marks used with Latin, Grek, Cyrillic scripts
    # that are reordered before the above marks
    mark_non_above_chars = set(
        c
        for c in cmap.keys()
        if unicodedata.combining(chr(c)) < 230
        and unicodedata.block(chr(c)).startswith("Combining Diacritical Marks")
    )
    # Skip when no characters to test with
    if not soft_dotted_chars or not mark_above_chars:
        yield SKIP, "Font has no soft dotted characters or no mark above characters."
        return

    # Collect outlines to skip fonts where i and dotlessi are the same,
    # or i and I are the same.
    outlines_dict = {
        codepoint: BezierPath.fromFonttoolsGlyph(ttFont, glyphname)
        for codepoint, glyphname in cmap.items()
        if codepoint in [ord("i"), ord("I"), ord("ı")]
    }
    unclear = False
    if ord("i") in cmap.keys() and ord("I") in cmap.keys():
        if len(outlines_dict[ord("i")]) == len(outlines_dict[ord("I")]):
            unclear = True
    if not unclear and ord("i") in cmap.keys() and ord("ı") in cmap.keys():
        if len(outlines_dict[ord("i")]) == len(outlines_dict[ord("ı")]):
            unclear = True
    if unclear:
        yield SKIP, (
            "It is not clear if the soft dotted characters have glyphs with dots."
        )
        return

    # Use harfbuzz to check if soft dotted glyphs are substituted
    filename = ttFont.reader.file.name
    vharfbuzz = Vharfbuzz(filename)
    fail_unchanged_strings = []
    warn_unchanged_strings = []
    for sequence in sorted(
        itertools.product(
            soft_dotted_chars,
            # add "" to add cases without non above marks
            mark_non_above_chars.union(set((0,))),
            mark_above_chars,
        )
    ):
        soft, non_above, above = sequence
        if non_above:
            unchanged = f"{cmap[soft]}|{cmap[non_above]}|{cmap[above]}"
            text = f"{chr(soft)}{chr(non_above)}{chr(above)}"
        else:
            unchanged = f"{cmap[soft]}|{cmap[above]}"
            text = f"{chr(soft)}{chr(above)}"

        # Only check a few strings that we WARN about.
        if text not in ortho_soft_dotted_strings and len(warn_unchanged_strings) >= 20:
            continue

        buf = vharfbuzz.shape(text)
        output = vharfbuzz.serialize_buf(buf, glyphsonly=True)
        if output == unchanged:
            if text in ortho_soft_dotted_strings:
                fail_unchanged_strings.append(text)
            else:
                warn_unchanged_strings.append(text)

    message = ""
    if fail_unchanged_strings:
        fail_unchanged_strings = " ".join(fail_unchanged_strings)
        message += (
            f"The dot of soft dotted characters used in orthographies"
            f" _must_ disappear in the following strings: {fail_unchanged_strings}"
        )
    if warn_unchanged_strings:
        warn_unchanged_strings = " ".join(warn_unchanged_strings)
        if message:
            message += "\n\n"
        message += (
            f"The dot of soft dotted characters _should_ disappear in"
            f" other cases, for example: {warn_unchanged_strings}"
        )

    # Calculate font's affected languages for additional information
    if fail_unchanged_strings or warn_unchanged_strings:
        from shaperglot.checker import Checker
        from shaperglot.languages import Languages, gflangs

        languages = Languages()

        # Find all affected languages
        ortho_soft_dotted_langs = set()
        for c in ortho_soft_dotted_strings:
            for lang in gflangs:
                if (
                    c in gflangs[lang].exemplar_chars.base
                    or c in gflangs[lang].exemplar_chars.auxiliary
                ):
                    ortho_soft_dotted_langs.add(lang)
        if ortho_soft_dotted_langs:
            affected_languages = []
            unaffected_languages = []
            languages = Languages()
            checker = Checker(ttFont.reader.file.name)

            for lang in ortho_soft_dotted_langs:
                reporter = checker.check(languages[lang])
                string = (
                    f"{gflangs[lang].name} ({gflangs[lang].script}, "
                    f"{'{:,.0f}'.format(gflangs[lang].population)} speakers)"
                )
                if reporter.is_success:
                    affected_languages.append(string)
                else:
                    unaffected_languages.append(string)

            if affected_languages:
                affected_languages = ", ".join(affected_languages)
                message += (
                    f"\n\nYour font fully covers the following languages that require"
                    f" the soft-dotted feature: {affected_languages}. "
                )

            if unaffected_languages:
                unaffected_languages = ", ".join(unaffected_languages)
                message += (
                    f"\n\nYour font does *not* cover the following languages that"
                    f" require the soft-dotted feature: {unaffected_languages}."
                )

    if fail_unchanged_strings or warn_unchanged_strings:
        yield WARN, Message("soft-dotted", message)
    else:
        yield PASS, (
            "All soft dotted characters seem to lose their dot when combined with"
            " a mark above."
        )
