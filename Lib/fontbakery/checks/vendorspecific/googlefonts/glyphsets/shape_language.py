from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.utils import markdown_table


@check(
    id="googlefonts/glyphsets/shape_languages",
    rationale="""
        This check uses a heuristic to determine which GF glyphsets a font supports.
        Then it checks the font for correct shaping behaviour for all languages in
        those glyphsets.
    """,
    conditions=[
        "network"
    ],  # use Shaperglot, which uses youseedee, which downloads Unicode files
    proposal=["https://github.com/googlefonts/fontbakery/issues/4147"],
)
def check_glyphsets_shape_languages(ttFont, config):
    """Shapes languages in all GF glyphsets."""
    from shaperglot.checker import Checker
    from shaperglot.languages import Languages
    from glyphsets import languages_per_glyphset, get_glyphsets_fulfilled

    def table_of_results(level, results):
        from fontbakery.utils import pretty_print_list

        results_table = []

        for message, languages in results.items():
            results_table.append(
                {
                    f"{level} messages": message,
                    "Languages": pretty_print_list(config, languages, quiet=True),
                }
            )
        return markdown_table(results_table)

    shaperglot_checker = Checker(ttFont.reader.file.name)
    shaperglot_languages = Languages()
    any_glyphset_supported = False

    warns = {}
    fails = {}
    glyphsets_fulfilled = get_glyphsets_fulfilled(ttFont)
    for glyphset in glyphsets_fulfilled:
        if glyphsets_fulfilled[glyphset]["percentage"] > 0.8:
            any_glyphset_supported = True
            for language_code in languages_per_glyphset(glyphset):
                reporter = shaperglot_checker.check(shaperglot_languages[language_code])
                name = shaperglot_languages[language_code]["name"]
                language_string = f"{language_code} ({name})"

                for w in reporter.warns:
                    if w.message not in warns.keys():
                        warns[w.message] = []
                    warns[w.message].append(language_string)

                for f in reporter.fails:
                    if f.message not in fails.keys():
                        fails[f.message] = []
                    fails[f.message].append(language_string)

    if fails:
        yield FAIL, Message(
            "failed-language-shaping",
            f"{glyphset} glyphset:\n{table_of_results('FAIL', fails)}\n",
        )

    if warns:
        yield WARN, Message(
            "warning-language-shaping",
            f"{glyphset} glyphset:\n{table_of_results('WARN', warns)}\n",
        )

    if not any_glyphset_supported:
        yield FAIL, Message(
            "no-glyphset-supported",
            (
                "No GF glyphset was found to be supported >80%,"
                " so language shaping support couldn't get checked."
            ),
        )
