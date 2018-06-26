[![Latest PyPI Version](https://img.shields.io/pypi/v/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Python](https://img.shields.io/pypi/pyversions/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://github.com/googlefonts/fontbakery/blob/master/LICENSE.txt)

# [![Font Bakery](data/logo.png)](https://fontbakery.appspot.com)

Font Bakery is a command-line tool ensuring the quality of font projects. It runs checks on TrueType files, and Google Fonts related metadata files.

If you are developing a font project publicly with Github (or a similar host) you can set up a Continuous Integration service (like [Travis](https://www.travis-ci.org)) to run Font Bakery on each commit, so that with each update all checks will be run on your files.

This project is currently maintained by Felipe Corrêa da Silva Sanches <juca@members.fsf.org>, with very frequent contributions from Lasse Fister, Marc Foley and Dave Crossland.

Font Bakery is not an official Google project, and Google provides no support for it.

## Command Line Tools

Since v0.3.3 Font Bakery is solely focused on automated quality checking of font families.

Font Bakery up to v0.3.2 provided some auxiliary scripts, and these have been moved into a separate "Google Fonts Tools" python package `gftools` at <https://github.com/googlefonts/tools> and packaged at <https://pypi.python.org/pypi/gftools>

Installing the latest version of the auxiliary scripts should be as easy as:

    pip install gftools --upgrade

## Web Usage

A web dashboard for monitoring check-results of the full Google Fonts collection (or possibly other collections of font families) was initialy developed in this repository, but is now available at <https://github.com/googlefonts/fontbakery-dashboard>

(There is an older drag-and-drop web app still hosted at <https://fontbakery.appspot.com> but this is not actively maintained.)

## Command Line Usage

Install Font Bakery as a package, following the [installation instructions](https://github.com/googlefonts/fontbakery#install), and you will have a `fontbakery` command in your `$PATH`

This has several subcommands, described in the help function:

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

This is the central script to run the FontBakery suite of checks.
It runs the checks (`specifications/googlefonts.py`) that we use for QA of <https://github.com/google/fonts>

To run the checks on some fonts:

    $ cd ~/path/to/fontproject/
    $ fontbakery check-googlefonts *.ttf

For more detailed output, run in verbose mode:

    $ fontbakery check-googlefonts --verbose *.ttf

To save a json formatted report (where check results are saved to `report.json`) do:

    $ fontbakery check-googlefonts --json report.json *.ttf

Run hand picked checks for all fonts in the `google/fonts` repository:


    $ fontbakery check-googlefonts \
        -c com.google.fonts/check/034 \
        -c com.google.fonts/check/044 \
        -n -o "*check" -g "*check" \
        path/to/fonts/{apache,ofl,ufl}/*/*.ttf

* `-c` selects a check by id
* `-n` turns off the progress bar
* `-o "*check"` change execution order to run each check for all fonts instead of all checks for each font.
* `-g "*check"` creates a summary report per check

Here's the output of `fontbakery check-googlefonts -h`:

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
                            Report checks with a result of this status or higher.
                            One of: DEBUG, PASS, INFO, SKIP, WARN, FAIL, ERROR.
                            (default: WARN)
      -m LOGLEVEL_MESSAGES, --loglevel-messages LOGLEVEL_MESSAGES
                            Report log messages of this status or higher.
                            Messages are all status lines within a check.
                            One of: DEBUG, PASS, INFO, SKIP, WARN, FAIL, ERROR.
                            (default: LOGLEVEL)
      -n, --no-progress     In a tty as stdout, don't render the progress indicators.
      -C, --no-colors       No colors for tty output
      --json JSON_FILE      Write a json formatted report to JSON_FILE.
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
                            "*check"     -- order by check
                            ITERATED_ARGS: font
                            A sections default is equivalent to: "*iterargs, *check".
                            A common use case is `-o "*check"` when checking the whole
                            collection against a selection of checks picked with `--checkid`.

Note: on Windows, color and progress bar output is disabled because the standard Windows terminal displays the escape characters instead. Pull Requests to fix this are welcome.

If you need to generate a list of all issues in a font family collection, such as the Google Fonts collection, checkout that repo and then run:

    sh bin/fontbakery-check-collection.sh path-to-collection-directory

This will create a folder called `check_results/` then run the `check-googlefonts` subcommand on every family, saving individual per-family reports in json format into subdirectories.

## Install

### Mac OS X

Minimal install procedure:

#### Step 1
```
# install os x developer tools and the homebrew package manager
xcode-select --install;
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)";
```

#### Step 2
```
# then instal python version 2 so that we don't rely
# on the python interpreter originally shipped on MacOSX
brew install python2;
```

#### Step 3
```
# and finally, use pip2 to install fontbakery
pip2 install fontbakery
```

#### Upgrades

For upgrading to a newer version (if you already installed a previous version of Font Bakery) you should do:
```
pip2 install --upgrade fontbakery
```

#### Additional dependencies

##### OTS: OpenType Sanitizer

```sh
# install ots
brew tap bramstein/webfonttools;
brew update;
brew install ots --HEAD;
```

##### FontForge

```sh
# install fontforge
brew install giflib libspiro icu4c;
brew install fontforge --with-extra-tools;
```

##### Apple OS X Font Tools

Apple provides various font utilities, and `ftxvalidator` is especially useful as it runs the same checks that are run for users when they install a font using Font Book.

You must use your Apple ID to sign in to http://developer.apple.com and download `osxfonttools.dmg` and then:

```sh
cd ~/Downloads/ ;
hdiutil attach osxfonttools.dmg ;
mkdir -p /tmp/ftx ;
cd /tmp/ftx ;
cp "/Volumes/OS X Font Tools/OS X Font Tools.pkg" . ;
xar -xf "OS X Font Tools.pkg" ;
cd fontTools.pkg/ ;
cat Payload | gunzip -dc | cpio -i ;
sudo mv ftx* /usr/local/bin/
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

For upgrading to a newer version (if you already installed a previous version of Font Bakery) you should do:

    pip install --upgrade fontbakery

## Microsoft Font Validator

A prebuilt binary of the Microsoft Font Validator is currently available at the `prebuilt/fval` directory in this repo.
(The corresponding source code is available under a free license at https://github.com/Microsoft/Font-Validator).
In order to enable this check, you'll need to have the mono runtime installed in your system.
You'll also need to have `FontValidator.exe` available in the system path.
One way to achieved would be:


    sudo apt-get install mono-runtime libmono-system-windows-forms4.0-cil
    export PATH=$PATH:$FONTBAKERY_GIT_REPO/prebuilt/fval

...where `$FONTBAKERY_GIT_REPO` should be the name of the directory where you checked out Font Bakery source code.
Obviously, you can also use any other alternative way of making `FontValidator.exe` available in your system path.

FontValidator includes some hinting instruction validation checks.
These rely on a customized version of the Freetype library.
In order to enable those, you'll need to use the custom build available in this repo by doing:

    export LD_PRELOAD=$FONTBAKERY_GIT_REPO/prebuilt/custom_freetype/lib/libfreetype.so

The corresponding modified freetype source code is available at <https://github.com/felipesanches/freetype2>

If your vanilla system freetype is used instead, then all FontValidator checks will still be run, except for the hinting validation ones.

## Bash completion

Font Bakery comes with a minimal Bash completion script to help you to type the subcommands that follow directly after the `fontbakery` command by hitting the tab key.

There's no special completion support for the arguments of the subcommands yet.

First, install `bash-completion` package.

If you want to use the file directly in a running Bash shell:

    $ source path-to/fontbakery/bin/bash-completion

If you are using a python virtual environment (that is not a system-wide installation), run:

    $ . path-to/fontbakery/bin/bash-completion

To install it, copy or symlink the `path-to/fontbakery/bin/bash_completion` file into your `bash_completion.d` directory as `fontbakery`.
Eg for GNU+Linux,

    ln -s path-to/fontbakery/bin/bash_completion /etc/bash_completion.d/fontbakery

On macOS the `bash_completion.d` directory may be `/sw/etc/bash_completion.d/fontbakery` or `/opt/local/etc/bash_completion.d/fontbakery`

Then restart your Terminal or bash shell.

# Developer Notes

## Updating the distribution package

Releases to PyPI are performed by tagging a commit and then running the following commands (with the proper version number and date):

```
# cleanup
rm build/ -rf
rm dist/ -rf
rm venv/ -rf

# create a fresh python virtual env
virtualenv venv
. venv/bin/activate

# Install tox and run our code tests
pip install tox
tox

# Register a git tag for this release and publish it
git tag -a v0.4.0 -m "Font Bakery version 0.4.0 (2018-May-16)"
git push upstream --tags

# create the package
python setup.py bdist_wheel --universal

# and finally upload the new package to PyPI
pip install twine
twine upload dist/*
```

## Code Testing

Font Bakery `check-googlefonts` provides over 130 checks for fonts and families according to the quality requirements of the Google Fonts team.
In addition to a complete architectural overhaul, release 0.3.1 introduced a set of code tests to assure the quality of the Font Bakery suite of checks.
This "testsuite for the testsuite" initially covered a third of the full set of check and as of version 0.4.1 covers 55%.
We aim to reach 100% test coverage.

In order to run the code tests you need to have the tox dependence installed and then run:

    tox

All future pull-requests adding new checks must also provide a corresponding code test.
Travis is configured to automatically run the code tests and pull-requests cannot be merged if any test is failing.

The Travis build logs can be seen at <https://travis-ci.org/googlefonts/fontbakery>

## Cached Vendor ID data

This project hosts a copy of the Microsoft's Vendor ID list at Lib/fontbakery/Lib/data/fontbakery-microsoft-vendorlist.cache

This is meant only as a caching mechanism. The latest data can always be fetched from Microsoft's website directly at: <https://www.microsoft.com/typography/links/vendorlist.aspx>
