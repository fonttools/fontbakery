# (Text) Shaping checks

In addition to helping you find structural issues in a font, FontBakery contains
a Shaping profile that can be used for validating that a font's OpenType layout
features work as expected. To run the Shaping profile checks you need to provide
one or more test suite files. These files are written in JSON format and include
the parameters and values required by the checks.

The [**shaping**](./shaping/) directory includes a few examples of such test suite
files to illustrate the expected format and syntax the JSON files must follow.
They are also annotated with comments that explain the intent of tests and how
they can be customized. Copying and modifying these files can form the basis for
your own text shaping test suite.

To run the Shaping checks, you first need to instruct `fontbakery` where your test
suite files are located. This can be done by creating a configuration file in YAML
format. Its contents will specify the directory where the JSON files can be found:

```
com.google.fonts/check/shaping:
    test_directory: examples/shaping
```

After saving this file — as `shaping.yml`, for example — you can then run
the Shaping profile checks using the following command:

    fontbakery check-shaping --config shaping.yml Font.ttf

For best results, generate an HTML report using the `--html` option.

    fontbakery check-shaping --config shaping.yml --html shaping.html Font.ttf

The report will include SVG illustrations for any failing tests.

For more information on the Shaping checks, see https://simoncozens.github.io/tdd-for-otl/
