# Font Bakery Command Line Usage

Install Font Bakery as a package with the instructions in the [Installation Guides](https://font-bakery.readthedocs.io/en/stable/user/installation/index.html), and you will have a `fontbakery` command in your `$PATH`.

This has several subcommands, described in the help function:

    $ fontbakery -h
    usage: fontbakery [-h] [--list-subcommands] subcommand
    
    Run fontbakery subcommands:
        build-contributors
        check-adobefonts
        check-fontbureau
        check-fontwerk
        check-fontval
        check-googlefonts
        check-notofonts
        check-profile
        check-ufo
        check-universal
        generate-glyphdata
    
    Subcommands have their own help messages. These are usually 
    accessible with the -h/--help flag positioned after the subcommand.
    I.e.: fontbakery subcommand -h
    
    positional arguments:
      subcommand          the subcommand to execute
    
    optional arguments:
      -h, --help          show this help message and exit
      --list-subcommands  print the list of subcommands to stdout, separated 
                          by a space character. This is usually only used to 
                          generate the shell completion code.

## fontbakery check-universal

The "universal" profile contains checks for best practices agreed upon on the type design community.

The initial set of checks was choses to be not only the full opentype profile but also those checks originally included in both `adobefonts` and `googlefonts` profiles.

The goal is to keep the vendor-specific profiles with only the minimal set of checks that are really specific, while the shared ones are placed on the universal profile.

We should always consider contributing new checks (or moving existing ones) to this universal profile, if appropriate.

## fontbakery check-adobefonts / check-fontbureau / check-fontwerk / check-notofonts

Usage is analogous to the Google Fonts profile described below.

## fontbakery check-googlefonts

This is the command used by foundries checking their projects for Google Fonts 



It runs the checks that we use in the [`profiles/googlefonts.py` Python script](https://github.com/fonttools/fontbakery/blob/main/Lib/fontbakery/profiles/googlefonts.py)

To run the checks on some fonts:

    $ cd ~/path/to/fontproject/
    $ fontbakery check-googlefonts *.ttf

For more detailed output, run in verbose mode:

    $ fontbakery check-googlefonts --verbose *.ttf

To save a json formatted report (where check results are saved to `report.json`) do:

    $ fontbakery check-googlefonts --json report.json *.ttf

Run hand picked checks for all fonts in the `google/fonts` repository:


    $ fontbakery check-googlefonts \
        -c com.google.fonts/check/xavgcharwidth \
        -c com.google.fonts/check/font_version \
        -n -o "*check" -g "*check" \
        path/to/fonts/{apache,ofl,ufl}/*/*.ttf

* `-c` selects a check by id
* `-n` turns off the progress bar
* `-o "*check"` change execution order to run each check for all fonts instead of all checks for each font.
* `-g "*check"` creates a summary report per check

Here's the output of `fontbakery check-googlefonts -h`:

    $ fontbakery check-googlefonts -h
    usage: fontbakery check-googlefonts [-h] [--configuration CONFIGFILE]
                                        [-c CHECKID] [-x EXCLUDE_CHECKID] [-v]
                                        [-l LOGLEVEL] [-m LOGLEVEL_MESSAGES]
                                        [--succinct] [-n] [-C] [-S] [-L]
                                        [--dark-theme] [--light-theme]
                                        [--json JSON_FILE] [--ghmarkdown MD_FILE]
                                        [--html HTML_FILE] [-g ITERATED_ARG]
                                        [-o ORDER] [-J JOBS] [-j]
                                        [fonts [fonts ...]]

    Check TTF files against a profile.

    positional arguments:
      fonts                 font file path(s) to check. Wildcards like *.ttf are allowed.

    optional arguments:
      -h, --help            show this help message and exit
      --configuration CONFIGFILE
                            Read configuration file (TOML/YAML).
      -c CHECKID, --checkid CHECKID
                            Explicit check-ids (or parts of their name) to be executed. Use this option multiple times to select multiple checks.
      -x EXCLUDE_CHECKID, --exclude-checkid EXCLUDE_CHECKID
                            Exclude check-ids (or parts of their name) from execution. Use this option multiple times to exclude multiple checks.
      -v, --verbose         Shortcut for `-l PASS`.
      -l LOGLEVEL, --loglevel LOGLEVEL
                            Report checks with a result of this status or higher.
                            One of: DEBUG, PASS, SKIP, INFO, WARN, FAIL, ERROR.
                            (default: INFO)
      -m LOGLEVEL_MESSAGES, --loglevel-messages LOGLEVEL_MESSAGES
                            Report log messages of this status or higher.
                            Messages are all status lines within a check.
                            One of: DEBUG, PASS, SKIP, INFO, WARN, FAIL, ERROR.
                            (default: LOGLEVEL)
      --succinct            This is a slightly more compact and succint output layout.
      -n, --no-progress     In a tty as stdout, don't render the progress indicators.
      -C, --no-colors       No colors for tty output.
      -S, --show-sections   Show section summaries.
      -L, --list-checks     List the checks available in the selected profile.
      --dark-theme          Use a color theme with dark colors.
      --light-theme         Use a color theme with light colors.
      --json JSON_FILE      Write a json formatted report to JSON_FILE.
      --ghmarkdown MD_FILE  Write a GitHub-Markdown formatted report to MD_FILE.
      --html HTML_FILE      Write a HTML report to HTML_FILE.
      -g ITERATED_ARG, --gather-by ITERATED_ARG
                            Optional: collect results by ITERATED_ARG
                            In terminal output: create a summary counter for each ITERATED_ARG.
                            In json output: structure the document by ITERATED_ARG.
                            One of: font, *check
      -o ORDER, --order ORDER
                            Comma separated list of order arguments.
                            The execution order is determined by the order of the check
                            definitions and by the order of the iterable arguments.
                            A section defines its own order. `--order` can be used to
                            override the order of *all* sections.
                            Despite the ITERATED_ARGS there are two special
                            values available:
                            "*iterargs" -- all remainig ITERATED_ARGS
                            "*check"    -- order by check
                            ITERATED_ARGS: font
                            A sections default is equivalent to: "*iterargs, *check".
                            A common use case is `-o "*check"` when checking the whole
                            collection against a selection of checks picked with `--checkid`.
      -J JOBS, --jobs JOBS  Use multi-processing to run the checks. The argument is the number
                            of worker processes. A sensible number is the cpu count of your
                            system, detected: 2. As an automated shortcut see -j/--auto-jobs.
                            Use 0 to run in single-processing mode (default 0).
      -j, --auto-jobs       Use the auto detected cpu count (= 2) as number of worker processes
                            in multi-processing. This is equivalent to : `--jobs 2`


Note: on Windows, color and progress bar output is disabled because the standard Windows terminal displays the escape characters instead. Pull Requests to fix this are welcome.

If you need to generate a list of all issues in a font family collection, the FontBakery repo has a small script to do so for the Google Fonts collection. Feel free to use that snippet and adapt it to the directory structure of your collection.

For checking the GFonts collection the script is used like this:

    sh snippets/fontbakery-check-gfonts-collection.sh path-to-collection-directory

This will create a folder called `check_results/` then run the `check-googlefonts` subcommand on every family, saving individual per-family reports in json format into subdirectories.

## fontbakery check-fontval

This is a wrapper around the Microsoft Font Validator.

Usage is similar to the check-googlefonts command described above.

## Configuration file

Some command-line parameters can be configured in a configuration file.
This may be in TOML or YAML format, and the name of this file is passed in
on the fontbakery command line with the `--configuration` parameter.
(`--config` for short.)

Currently, the following command-line parameters can be specified in the
configuration file:

- Instead of using `-c` to specify checks, a list of checks can be provided using the `explicit_checks` key:

```
explicit_checks = [
    'com.google.fonts/check/family/underline_thickness',
    'com.google.fonts/check/family/panose_familytype',
]
```

- Instead of using `-x` to exclude checks, a list of checks to exclude can be provided using the `exclude_checks` key.

- Instead of using `--order` to specify the check order, a list of checks can be provided using the `custom_order` key.

Additionally, the configuration file can be used to replace the status of
particular checks. To do this, you will need to know the *message ID*,
which is reported with the result. For example, when the
`com.google.fonts/check/mandatory_glyphs` check reports that the `.notdef`
glyph does not contain any outlines, it reports the message ID `empty` and
a `WARN` status. To replace this status and have it return a `FAIL` instead,
place this in the configuration file (if you are using YAML format):

```
overrides:
  com.google.fonts/check/mandatory_glyphs:
    empty: FAIL
```

Individual checks and profiles may give semantics to additional configuration values;
the whole configuration file is passed to checks which request access to it.
Currently supported values include:

- `is_icon_font`: A boolean value stating whether the fonts provided are icon fonts.
  (overriding a check on the PANOSE values of those fonts) Certain checks will be
  skipped for icon fonts.
