DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING = """
        The expected pattern for the copyright string adheres to the following rules:

        * It must say "Copyright" followed by a 4 digit year (optionally followed by
          a hyphen and another 4 digit year)

        * Additional years or year ranges are also valid.

        * An optional comma can be placed here.

        * Then it must say "The <familyname> Project Authors" and, within parentheses,
          a URL for a git repository must be provided. But we have an exception
          for the fonts from the Noto project, that simply have
          "google llc. all rights reserved" here.

        * The check is case insensitive and does not validate whether the familyname
          is correct, even though we'd obviously expect it to be.


        Here is an example of a valid copyright string:

        "Copyright 2017 The Archivo Black Project Authors
         (https://github.com/Omnibus-Type/ArchivoBlack)"
"""
EXPECTED_COPYRIGHT_PATTERN = r"copyright \d{4}(-\d{4})?(,\s*\d{4}(-\d{4})?)*,? (the .* project authors \([^\@]*\)|google llc. all rights reserved)"  # noqa:E501 pylint:disable=C0301
