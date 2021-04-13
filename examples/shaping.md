Examples for the shaping check
==============================

As well as finding structural issues with a font, fontbakery contains a
check profile (`fontbakery.profiles.shaping`) which ensures that the
font's OpenType layout rules behave as designed. To run this check, the
designer must supply one or more test suites, which are represented as
JSON files.

The `shaping/` directory contains a number of JSON files which
illustrate the expected format and syntax of these test suites. They are also documented with comments to explain the intent of tests and how they can be customised. Copying and modifying these files can form a basis for your own shaping test suite.

To run the shaping check, you need to tell fontbakery where to find your test suite. This can be done by creating a fontbakery configuration file in YAML format and specifying the directory where the JSON files can be found:

```
com.google.fonts/check/shaping:
    test_directory: examples/shaping
```

If this file is saved as (e.g.) `fontbakery.yml`, then the shaping check can be run with the following command:

```
fontbakery check-profile --config fontbakery.yml fontbakery.profiles.shaping Font.ttf
```

For best results, generate a HTML report using the `--html report.html` flag to fontbakery, as this will contain SVG illustrations for failing tests.

For more information on the shaping check, see https://simoncozens.github.io/tdd-for-otl/
