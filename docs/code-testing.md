## Font Bakery Code Testing

Font Bakery `check-googlefonts` provides over 130 checks for fonts and families according to the quality requirements of the Google Fonts team.
In addition to a complete architectural overhaul, release 0.3.1 introduced a set of code tests to assure the quality of the Font Bakery suite of checks.
This "testsuite for the testsuite" initially covered a third of the full set of check and as of version 0.4.1 covers 55%.
We aim to reach 100% test coverage.

In order to run the code tests you need to have the tox dependence installed and then run:

    tox

All future pull-requests adding new checks must also provide a corresponding code test.
Travis is configured to automatically run the code tests and pull-requests cannot be merged if any test is failing.

The Travis build logs can be seen at <https://travis-ci.org/googlefonts/fontbakery>
