[![Latest PyPI Version](https://img.shields.io/pypi/v/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Python](https://img.shields.io/pypi/pyversions/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://github.com/googlefonts/fontbakery/blob/master/LICENSE.txt)

# [![Font Bakery](data/logo.png)](https://fontbakery.appspot.com)

Font Bakery is a command-line tool for testing font projects. It runs checks on TrueType files, and Google Fonts related metadata files.

If you are developing a font project publicly with Github (or a similar host) you can set up a Continuous Integration service (like [Travis](https://www.travis-ci.org)) to run FontBakery on each commit, so that with each update your files are tested.

Font Bakery is not an official Google project, and Google provides no support for it.

## Web Usage

To use Font Bakery through a web UI is currently not supported.
There is an old version of a drag-and-drop web app still hosted at [fontbakery.appspot.com](https://fontbakery.appspot.com) but not actively maintained anymore.

A modern web dashboard is under development at <https://github.com/googlefonts/fontbakery-dashboard/> and will allow monitoring the check results of collections of font families, such as the entire Google Fonts collection.

The web dashboard was initially developed in this repository, but later it was split out into its own git repo.

## Auxiliary scripts

All auxiliary scripts provided by fontbakery up to v0.3.2 have been moved into a separate python package called `gftools` (which stands for 'Google Fonts Tools') available at https://github.com/googlefonts/tools/ and at http://pypi.python.org/gftools. Fontbakery (starting on the v0.3.3 release) is now solely focused on font family automated quality tests.

Installing the latest version of the auxiliary scripts should be as easy as:
```
pip install gftools --upgrade
```

For any further guidance, please see the gftools documentation at https://github.com/googlefonts/tools/

## Command Line Usage

Install Font Bakery as a package, following the [installation instructions](https://github.com/googlefonts/fontbakery#install).
This puts the `fontbakery` command in your `$PATH`, and makes its subcommands accessible as described below.

Here's the output of the command line help:

```
$ fontbakery -h
usage: fontbakery [-h] [--list-subcommands] subcommand

Run fontbakery subcommands:
    build-contributors
    check-collection
    check-googlefonts
    check-noto-version
    check-specification
    generate-glyphdata

Subcommands have their own help messages. These are usually accessible with the -h/--help flag positioned after the subcommand.
I.e.: fontbakery subcommand -h

positional arguments:
  subcommand          the subcommand to execute

optional arguments:
  -h, --help          show this help message and exit
  --list-subcommands  print the list of subcommnds to stdout, separated by a space character. This is usually only used to generate the shell completion code.
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

# install fontbakery
easy_install pip;
pip install fontbakery
```

For upgrading to a newer version (if you already installed a previous version of fontbakery) you should do:
```
pip install --upgrade fontbakery
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

# install fontbakery
pip install fontbakery
```

For upgrading to a newer version (if you already installed a previous version of fontbakery) you should do:
```
pip install --upgrade fontbakery
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
# cleanup
rm build/ -rf
rm dist/ -rf
rm venv/ -rf

# create a fresh python virtual env
virtualenv venv
. venv/bin/activate

# Remove the '-git' suffix and bump up the version number on setup.py
vim setup.py
git add setup.py
git commit -m "Updating version in preparation for a new release"

# install fontbakery on it and run our code tests
python setup.py install
pip install pytest
pytest Lib/fontbakery --verbose

# crate the package
python setup.py bdist_wheel

# Register a git tag for this release and publish it
git tag -a v0.3.2 -m "FontBakery version 0.3.2 (2017-Oct-11)"
git push upstream --tags

# and finally upload the new package to PyPI
twine upload dist/*

# Then we append a '-git' suffix on setup.py
vim setup.py
git add setup.py
git commit -m "Adding '-git' to version for the next release cycle"
```

We keep setup.py with a '-git' suffix in the version number during development cycles (such as 'v0.3.2-git' meaning v0.3.2 plus further development changes).

### Self-tests using pytest

Font Bakery check-googlefonts target provides a total of 125 tests for fonts and families according to the quality requirements of the Google Fonts team.
In addition to a complete architectural overhaul, release 0.3.1 introduced a set of self-tests to assure the quality of the Font Bakery tests themselves. Such "testsuite for the testsuite" initially covered a third of the full set of tests and currently (as of version 0.3.2) covers a bit more than half of them (52.8%). Upcoming releases will aim at reaching 100% self-test coverage.

In order to run the self-tests you need to have the pytest dependence installed and then run:

```
pytest Lib/fontbakery --verbose
```

All future pull-requests adding new tests must also provide a corresponding self-test. Travis is configured to automatically run the self-tests and pull-requests cannot be merged if any self-test is failing.

The Travis build logs can be seen at: https://travis-ci.org/googlefonts/fontbakery/
