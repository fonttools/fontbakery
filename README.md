[![Latest PyPI Version](https://img.shields.io/pypi/v/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Python](https://img.shields.io/pypi/pyversions/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://github.com/googlefonts/fontbakery/blob/master/LICENSE.txt)

# [![Font Bakery](data/logo.png)](https://fontbakery.appspot.com)

Font Bakery is a command-line tool for testing font projects, also available as a drag-and-drop web app from [fontbakery.appspot.com](https://fontbakery.appspot.com)

It runs checks on TrueType files, and Google Fonts related metadata files.

If you are developing a font project publicly with Github (or a similar host) you can set up a Continuous Integration service (like [Travis](https://www.travis-ci.org)) to run FontBakery on each commit, so that with each update your files are tested.

Font Bakery is not an official Google project, and Google provides no support for it.

## Web Usage

To use Font Bakery through a web UI is currently not supported.

A web dashboard is under development at <https://github.com/googlefonts/fontbakery-dashboard/> and will allow monitoring the check results of collections of font families, such as the entire Google Fonts collection.

This tool was initially developed in this repository, but later it was split out into its own git repo.

## Command Line Usage

**For infrequent usage**, clone this repo and then run each tool by itself:

    PYTHONPATH=Lib python bin/fontbakery-metadata-vs-api.py <args>

Beware, some of the scripts in `bin` do have further dependencies. In that case and<br />
**for regular usage**, install Font Bakery as a package, following the [installation instructions](https://github.com/googlefonts/fontbakery#install) below.
This puts the `fontbakery` command in your `$PATH`, and makes all other subcommands accessible.

Here's the output of the command line help:

```
$ fontbakery -h
usage: fontbakery [-h] [--list-subcommands] subcommand

Run fontbakery subcommands:
    build-contributors
    build-font2ttf
    build-fontmetadata
    build-ofl
    check-bbox
    check-category
    check-collection
    check-copyright-notices
    check-font-version
    check-gf-github
    check-googlefonts
    check-name
    check-noto-version
    check-specification
    check-vtt-compatibility
    dev-testrunner
    family-html-snippet
    fix-ascii-fontmetadata
    fix-cmap
    fix-dsig
    fix-familymetadata
    fix-fsselection
    fix-fstype
    fix-gasp
    fix-glyph-private-encoding
    fix-glyphs
    fix-nameids
    fix-nonhinting
    fix-ttfautohint
    fix-vendorid
    fix-vertical-metrics
    generate-glyphdata
    list-panose
    list-variable-source
    list-weightclass
    list-widthclass
    metadata-vs-api
    nametable-from-filename
    ots
    update-families
    update-nameids
    update-version
```

### fontbakery check-googlefonts

This is the central script to run the fontbakery test suite. It runs the
tests (`specifications/googlefonts.py`) that we use for QA of https://github.com/google/fonts.

#### To run the tests on some fonts:

    $ cd ~/path/to/fontproject/
    $ fontbakery check-googlefonts *.ttf

#### For more detailed output, run in verbose mode:

    $ fontbakery check-googlefonts --verbose *.ttf

To save a json formatted report do:

    $ fontbakery check-googlefonts --json report.json *.ttf

The check results will be saved to a file called `report.json`.

#### Run hand picked checks for all fonts in the `google/fonts` repository:

```
$ fontbakery check-googlefonts \
    -c com.google.fonts/test/034 \
    -c com.google.fonts/test/044 \
    -n -o "*test" -g "*test" \
    path/to/fonts/{apache,ofl,ufl}/*/*.ttf
```

 * `-c` selects a test by id
 * `-n` turns off the progress bar
 * `-o "*test"` change execution order to run each test for all fonts instead of all tests for each font.
 * `-g "*test"` creates a summary report per test


Here's the output of `fontbakery check-googlefonts -h`

```
$ fontbakery check-googlefonts -h
usage: fontbakery-check-googlefonts.py [-h] [-c CHECKID] [-v] [-l LOGLEVEL]
                                       [-m LOGLEVEL_MESSAGES] [-n] [-C]
                                       [--json JSON_FILE] [-g ITERATED_ARG]
                                       [-o ORDER]
                                       arg_filepaths [arg_filepaths ...]

Check TTF files for common issues.

positional arguments:
  arg_filepaths         font file path(s) to check. Wildcards like *.ttf are allowed.

optional arguments:
  -h, --help            show this help message and exit
  -c CHECKID, --checkid CHECKID
                        Explicit check-ids to be executed.
                        Use this option multiple times to select multiple checks.
  -v, --verbose         Shortcut for `-l PASS`.
  -l LOGLEVEL, --loglevel LOGLEVEL
                        Report tests with a result of this status or higher.
                        One of: DEBUG, PASS, INFO, SKIP, WARN, FAIL, ERROR.
                        (default: WARN)
  -m LOGLEVEL_MESSAGES, --loglevel-messages LOGLEVEL_MESSAGES
                        Report log messages of this status or higher.
                        Messages are all status lines within a test.
                        One of: DEBUG, PASS, INFO, SKIP, WARN, FAIL, ERROR.
                        (default: LOGLEVEL)
  -n, --no-progress     In a tty as stdout, don't render the progress indicators.
  -C, --no-colors       No colors for tty output
  --json JSON_FILE      Write a json formatted report to JSON_FILE.
  -g ITERATED_ARG, --gather-by ITERATED_ARG
                        Optional: collect results by ITERATED_ARG
                        In terminal output: create a summary counter for each ITERATED_ARG.
                        In json output: structure the document by ITERATED_ARG.
                        One of: font, *test
  -o ORDER, --order ORDER
                        Comma separated list of order arguments.
                        The execution order is determined by the order of the test
                        definitions and by the order of the iterable arguments.
                        A section defines its own order. `--order` can be used to
                        override the order of *all* sections.
                        Despite the ITERATED_ARGS there are two special
                        values available:
                        "*iterargs" -- all remainig ITERATED_ARGS
                        "*test"     -- order by test
                        ITERATED_ARGS: font
                        A sections default is equivalent to: "*iterargs, *test".
                        A common use case is `-o "*test"` when testing the whole
                        collection against a selection of tests picked with `--checkid`.
```


### FontBakery web Dashboard

There is a web dashboard that is used for monitoring the check-results of the full Google Fonts collection (or possibly other collections of font families). This tool was initialy developed in this repository, but later it was split out into its own git repo, now available at: https://github.com/googlefonts/fontbakery-dashboard

### Automated testing of all Google Fonts

If you need to generate a list of all issues in a font family collection, such as the Google Fonts collection, you have to have a full checkout of it, and then you can run:

    `sh bin/fontbakery-check-collection.sh path-to-collection-directory

This will create a folder called `check_results/`, then run Font Bakery `check-googlefonts` on every family from the collection.
The output is individual per-family reports, in json format, saved in subdirectories with the names of the license directories.

## Other auxiliary fontbakery scripts

### fontbakery build-contributors

This is a project maintainence tool that generate a `CONTRIBUTORS.txt` file from a repository's git history.

```
usage: fontbakery build-contributors [-h] folder

positional arguments:
  folder      source folder which contains git commits

optional arguments:
  -h, --help  show this help message and exit
```

### fontbakery build-font2ttf

```
usage: fontbakery build-font2ttf [-h] [--with-otf] source [source ...]

positional arguments:
  source

optional arguments:
  -h, --help  show this help message and exit
  --with-otf  Generate otf file
```

### fontbakery build-fontmetadata

Calculates the visual weight, width or italic angle of fonts. For width, it
just measures the width of how a particular piece of text renders. For weight,
it measures the darkness of a piece of text. For italic angle it defaults to
the italicAngle property of the font. Then it starts a HTTP server and shows
you the results, or if you pass --debug then it just prints the values.

```
usage: fontbakery build-fontmetadata [-h] -f FILES [-d] [-e EXISTING] [-m]
                                     -o OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  -f FILES, --files FILES
                        The pattern to match for finding ttfs, eg
                        'folder_with_fonts/*.ttf'.
  -d, --debug           Debug mode, just print results
  -e EXISTING, --existing EXISTING
                        Path to existing font-metadata.csv
  -m, --missingmetadata
                        Only process fonts for which metadata is not available
                        yet
  -o OUTPUT, --output OUTPUT
                        CSV data output filename
```

### fontbakery check-bbox

A FontForge python script for printing bounding boxes to stdout.

```
usage: fontbakery check-bbox [-h] font

positional arguments:
  font        Font in OpenType (TTF/OTF) format

optional arguments:
  -h, --help  show this help message and exit
```

### fontbakery check-category

Comparison of category fields of local METADATA.pb files with data
corresponding metadata on the Google Fonts Developer API.

In order to use it you need to provide an API key.

```
usage: fontbakery-check-category.py [-h] [--verbose] key repo

positional arguments:
  key         Key from Google Fonts Developer API
  repo        Directory tree that contains directories with METADATA.pb files.

optional arguments:
  -h, --help  show this help message and exit
  --verbose   Print additional information
```

### fontbakery family-html-snippet

Generate a test html snippet for a family hosted on fonts.google.com This
script works well for quickly producing test cases using jsbin.

```
$ fontbakery
family-html-snippet "Exo" "Hello World" >>> ... <html> <head> <link
href="https://fonts.googleapis.com/css?family=Exo"/rel="stylesheet"> <style>
.g{font-family: 'Exo'; font-weight:400;} .h{font-family: 'Exo'; font-
weight:400; font-style: italic;} .m{font-family: 'Exo'; font-weight:700;} .n
{font-family: 'Exo'; font-weight:700; font-style: italic;} </style> </head>
<body> <p class='g'>Hello World</p> <p class='h'>Hello World</p> <p
class='m'>Hello World</p> <p class='n'>Hello World</p> </body> </html>
```

```
usage: fontbakery family-html-snippet [-h]
                                      [--subsets SUBSETS [SUBSETS ...]]
                                      family sample_text
positional arguments:
  family                family name on fonts.google.com
  sample_text           sample text used for each font

optional arguments:
  -h, --help            show this help message and exit
  --subsets SUBSETS [SUBSETS ...]
                        family subset(s) seperated by a space
```

### fontbakery fix-ascii-fontmetadata

Fixes TTF NAME table strings to be ascii only

```
usage: fontbakery fix-ascii-fontmetadata [-h] ttf_font [ttf_font ...]

positional arguments:
  ttf_font    Font in OpenType (TTF/OTF) format

optional arguments:
  -h, --help  show this help message and exit
```

### fontbakery fix-cmap

Manipulate a collection of fonts' cmap tables.

```
usage: fontbakery-fix-cmap.py [-h] [--format-4-subtables]
                              [--drop-mac-subtable] [--keep-only-pid-0]
                              fonts [fonts ...]

positional arguments:
  fonts

optional arguments:
  -h, --help            show this help message and exit
  --format-4-subtables, -f4
                        Convert cmap subtables to format 4
  --drop-mac-subtable, -dm
                        Drop Mac cmap subtables
  --keep-only-pid-0, -k0
                        Keep only cmap subtables with pid=0 and drop the rest.
```

### fontbakery fix-dsig

Fixes TTF to have a dummy DSIG table

```
usage: fontbakery fix-dsig [-h] [--autofix] ttf_font [ttf_font ...]

positional arguments:
  ttf_font    One or more font files

optional arguments:
  -h, --help  show this help message and exit
  --autofix   Apply autofix
```

### fontbakery-fix-familymetadata.py

Print out family metadata of the fonts

```
usage: fontbakery fix-familymetadata [-h] [--csv] font [font ...]

positional arguments:
  font

optional arguments:
  -h, --help  show this help message and exit
  --csv
```

### fontbakery fix-fsselection

Print out fsSelection bitmask of the fonts

```
usage: fontbakery fix-fsselection [-h] [--csv] [--autofix] font [font ...]

positional arguments:
  font

optional arguments:
  -h, --help  show this help message and exit
  --csv
  --autofix
```

### fontbakery fix-gasp

Fixes TTF GASP table

```
usage: fontbakery fix-gasp [-h] [--autofix] [--set SET]
                           ttf_font [ttf_font ...]

positional arguments:
  ttf_font    Font in OpenType (TTF/OTF) format

optional arguments:
  -h, --help  show this help message and exit
  --autofix   Apply autofix
  --set SET   Change gasprange value of key 0xFFFF to a new value
```

### fontbakery fix-glyph-private-encoding

Fixes TTF unencoded glyphs to have Private Use Area encodings

```
usage: fontbakery fix-glyph-private-encoding [-h] [--autofix]
                                             ttf_font [ttf_font ...]

positional arguments:
  ttf_font    Font in OpenType (TTF/OTF) format

optional arguments:
  -h, --help  show this help message and exit
  --autofix   Apply autofix. Otherwise just check if there are unencoded
              glyphs
```

### fontbakery fix-glyphs

Report issues on .glyphs font files

```
usage: fontbakery fix-glyphs [-h] font [font ...]

positional arguments:
  font

optional arguments:
  -h, --help  show this help message and exit
```

### fontbakery fix-nameids

Print out nameID strings of the fonts

```
usage: fontbakery fix-nameids [-h] [--autofix] [--csv] [--id ID]
                              [--platform PLATFORM]
                              font [font ...]

positional arguments:
  font

optional arguments:
  -h, --help            show this help message and exit
  --autofix             Apply autofix
  --csv                 Output data in comma-separate-values (CSV) file format
  --id ID, -i ID
  --platform PLATFORM, -p PLATFORM
```

### fontbakery fix-nonhinting

Fixes TTF GASP table so that its program contains the minimal recommended instructions

```
usage: fontbakery fix-nonhinting [-h] fontfile_in fontfile_out

positional arguments:
  fontfile_in   Font in OpenType (TTF/OTF) format
  fontfile_out  Filename for the output

optional arguments:
  -h, --help    show this help message and exit
```

### fontbakery fix-ttfautohint

Fixes TTF Autohint table

```
usage: fontbakery fix-ttfautohint [-h] ttf_font [ttf_font ...]

positional arguments:
  ttf_font    Font in OpenType (TTF/OTF) format

optional arguments:
  -h, --help  show this help message and exit
```

### fontbakery fix-vendorid

Print vendorID of TTF files

```
usage: fontbakery fix-vendorid [-h] arg_filepaths [arg_filepaths ...]

positional arguments:
  arg_filepaths  font file path(s) to check. Wildcards like *.ttf are allowed.

optional arguments:
  -h, --help     show this help message and exit
```

### fontbakery fix-vertical-metrics

```
usage: fontbakery fix-vertical-metrics  [-h] [-a ASCENTS] [-ah ASCENTS_HHEA]
                                        [-at ASCENTS_TYPO] [-aw ASCENTS_WIN]
                                        [-d DESCENTS] [-dh DESCENTS_HHEA]
                                        [-dt DESCENTS_TYPO]
                                        [-dw DESCENTS_WIN] [-l LINEGAPS]
                                        [-lh LINEGAPS_HHEA]
                                        [-lt LINEGAPS_TYPO] [--autofix]
                                        ttf_font [ttf_font ...]

positional arguments:
  ttf_font              Font file in OpenType (TTF/OTF) format

optional arguments:
  -h, --help            show this help message and exit
  -a ASCENTS, --ascents ASCENTS
                        Set new ascents value.
  -ah ASCENTS_HHEA, --ascents-hhea ASCENTS_HHEA
                        Set new ascents value in 'Horizontal Header' table
                        ('hhea'). This argument cancels --ascents.
  -at ASCENTS_TYPO, --ascents-typo ASCENTS_TYPO
                        Set new ascents value in 'Horizontal Header' table
                        ('OS/2'). This argument cancels --ascents.
  -aw ASCENTS_WIN, --ascents-win ASCENTS_WIN
                        Set new ascents value in 'Horizontal Header' table
                        ('OS/2.Win'). This argument cancels --ascents.
  -d DESCENTS, --descents DESCENTS
                        Set new descents value.
  -dh DESCENTS_HHEA, --descents-hhea DESCENTS_HHEA
                        Set new descents value in 'Horizontal Header' table
                        ('hhea'). This argument cancels --descents.
  -dt DESCENTS_TYPO, --descents-typo DESCENTS_TYPO
                        Set new descents value in 'Horizontal Header' table
                        ('OS/2'). This argument cancels --descents.
  -dw DESCENTS_WIN, --descents-win DESCENTS_WIN
                        Set new descents value in 'Horizontal Header' table
                        ('OS/2.Win'). This argument cancels --descents.
  -l LINEGAPS, --linegaps LINEGAPS
                        Set new linegaps value.
  -lh LINEGAPS_HHEA, --linegaps-hhea LINEGAPS_HHEA
                        Set new linegaps value in 'Horizontal Header' table
                        ('hhea')
  -lt LINEGAPS_TYPO, --linegaps-typo LINEGAPS_TYPO
                        Set new linegaps value in 'Horizontal Header' table
                        ('OS/2')
  --autofix             Autofix font metrics
```

### fontbakery list-panose

Print out Panose of the fonts

```
usage: fontbakery list-panose [-h] [--csv] font [font ...]

positional arguments:
  font

optional arguments:
  -h, --help  show this help message and exit
  --csv
```

### fontbakery list-weightclass

Print out usWeightClass of the fonts

```
usage: fontbakery list-weightclass [-h] [--csv] font [font ...]

positional arguments:
  font

optional arguments:
  -h, --help  show this help message and exit
  --csv
```

### fontbakery list-widthclass

Print out usWidthClass of the fonts

```
usage: fontbakery list-widthclass [-h] [--csv] [--set SET] [--autofix]
                                  font [font ...]

positional arguments:
  font

optional arguments:
  -h, --help  show this help message and exit
  --csv
  --set SET
  --autofix
```

### fontbakery metadata-vs-api

This script compares the info on local METADATA.pb files
with data fetched from the Google Fonts Developer API.

In order to use it you need to provide an API key.

```
usage: fontbakery metadata-vs-api [-h] [--cache CACHE] [--verbose]
                                  [--ignore-copy-existing-ttf] [--autofix]
                                  [--api API]
                                  key repo

positional arguments:
  key                   Key from Google Fonts Developer API.
  repo                  Directory tree that contains directories with
                        METADATA.pb files.

optional arguments:
  -h, --help            show this help message and exit.
  --cache CACHE         Directory to store a copy of the files in the fonts
                        developer api.
  --verbose             Print additional information.
  --ignore-copy-existing-ttf
  --autofix             Apply automatic fixes to files.
  --api API             Domain string to use to request.
```

### fontbakery update-families

Compare TTF files when upgrading families.

```
usage: fontbakery update-families [-h] [-v]
                                  arg_filepaths [arg_filepaths ...]

positional arguments:
  arg_filepaths      font file path(s) to check. Wildcards like *.ttf are
                     allowed.

optional arguments:
  -h, --help         show this help message and exit
  -v, --verbose      increase output verbosity
```

## Install

### Mac OS X

```sh
# install os x developer tools and the homebrew package manager
xcode-select --install;
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)";

# install ots
brew tap bramstein/webfonttools;
brew update;
brew install ots --HEAD;

# install fontforge
brew install python giflib libspiro icu4c;
brew install fontforge --with-extra-tools --HEAD ;

# install fonttools
easy_install pip;
pip install --upgrade git+https://github.com/behdad/fontTools.git;

# install python dependencies
pip install -r requirements.txt

# install travis, for setting up CI
sudo gem install travis; # fontbakery dependencies

# install fontbakery
pip install --upgrade git+https://github.com/googlefonts/fontbakery.git;
```

### GNU+Linux

```sh
# install fontforge
sudo add-apt-repository --yes ppa:fontforge/fontforge;
sudo apt-get update -qq;
sudo apt-get install python-fontforge

# install ots from source
git clone https://github.com/khaledhosny/ots.git;
cd ots;
./autogen.sh;
./configure;
make CXXFLAGS=-DOTS_DEBUG;
sudo make install;
cd ..;
rm -rf ots;

# install fonttools
pip install --upgrade git+https://github.com/behdad/fontTools.git;

# install python dependencies
pip install -r requirements.txt

# install fontbakery
pip install --upgrade git+https://github.com/googlefonts/fontbakery.git;
```

## Microsoft Font Validator

A prebuilt binary of the Microsoft Font Validator is currently available at the `prebuilt/fval` directory in this repo. (The corresponding source code is available under a free license at https://github.com/Microsoft/Font-Validator). In order to enable this check, you'll need to have the mono runtime installed in your system. You'll also need to have `FontValidator.exe` available in the system path. One way to achieved would be:

```
sudo apt-get install mono-runtime libmono-system-windows-forms4.0-cil
export PATH=$PATH:$FONTBAKERY_GIT_REPO/prebuilt/fval
```

...where `$FONTBAKERY_GIT_REPO` should be the name of the directory where you checked out Font Bakery source code. Obviously, you can also use any other alternative way of making `FontValidator.exe` available in your system path.

FontValidator includes some hinting instruction validation tests. These rely on a customized version of the Freetype library. In order to enable those, you'll need to use the custom build available in this repo by doing:

```
export LD_PRELOAD=$FONTBAKERY_GIT_REPO/prebuilt/custom_freetype/libfreetype.so
```

The corresponding modified freetype source code is available at:
https://github.com/felipesanches/freetype2

If your vanilla system freetype is used instead, then all FontValidator tests will still be run, except for the hinting validation ones.

## Bash completion

Fontbakery comes with a minimal Bash completion script. It can help you to type the subcommands that follow directly after the `fontbakery` command. Bash completion is accessed by hitting the [TAB] key when entering the command.

There's no special completion support for the arguments of the subcommands yet.

### Install

This will enable completion for `fontbakery` on each newly opened Bash.

* Install bash-completion. On many GNU+Linux distributions it is installed and enabled by default. Mac OS X users can find it in Fink or MacPorts.
* Copy or symlink the `path-to/fontbakery/bin/bash_completion` file to `/etc/bash_completion.d/fontbakery` (on Mac&nbsp;OS&nbsp;X to: `/sw/etc/bash_completion.d/fontbakery` or `/opt/local/etc/bash_completion.d/fontbakery`).
* Restart your shell.

### Alternative install

You can source the file directly in a running Bash and only for the running instance:

```
$ . path-to/fontbakery/bin/bash-completion
# OR
$ source path-to/fontbakery/bin/bash-completion
```

This is particularly useful if you are running `fontbakery` in a python virtual environment, i.e. not a system-wide installation.

### Font Bakery maintenance

This project is currently maintained by Felipe Corrêa da Silva Sanches <juca@members.fsf.org> with very frequent contributions from Lasse Fister, Marc Foley and Dave Crossland.

Releases to PyPI are performed by updating the version metadata on `setup.py` and then running the following commands (with the proper version number and date):

```
rm build/ -rf
rm dist/ -rf
python setup.py bdist_wheel
twine upload dist/*
git tag -a v0.3.2 -m "FontBakery version 0.3.2 (2017-Oct-11)"
git push upstream --tags
```

We also keep setup.py with a '-git' prefix in the version number during development cycles (such as 'v0.3.2-git' meaning v0.3.2 plus further development changes).

### Self-tests using pytest

Font Bakery check-googlefonts target provides a total of 125 tests for fonts and families according to the quality requirements of the Google Fonts team.
In addition to a complete architectural overhaul, release 0.3.1 introduced a set of self-tests to assure the quality of the Font Bakery tests themselves. Such "testsuite for the testsuite" initially covered a third of the full set of tests and currently (as of version 0.3.2) covers a bit more than half of them (52.8%). Upcoming releases will aim at reaching 100% self-test coverage.

In order to run the self-tests you need to have the pytest dependence installed and then run:

```
pytest Lib/fontbakery --verbose
```

All future pull-requests adding new tests must also provide a corresponding self-test. Travis is configured to automatically run the self-tests and pull-requests cannot be merged if any self-test is failing.

The Travis build logs can be seen at: https://travis-ci.org/googlefonts/fontbakery/
