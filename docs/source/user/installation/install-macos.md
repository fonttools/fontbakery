# macOS Installation Guide

You'll need Python 3.7 (or newer) to run Font Bakery. Install the [`python` formula](https://formulae.brew.sh/formula/python) with the [Homebrew](https://brew.sh) package manager using the instructions below.

## Install

Install macOS developer tools and the Homebrew package manager:

```
xcode-select --install ;
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Install Homebrew Python 3:

```
brew install python
```

Use pip3 to install fontbakery:

```
pip3 install fontbakery
```

## Upgrade

If you already installed a previous version of Font Bakery, upgrade to a newer version with:

```
pip3 install --upgrade fontbakery
```

## Additional Dependencies

The following are optional dependencies that you can install to extend the functionality of Font Bakery.  Please note that some tests will not be executed if these optional dependencies are not present on your system.


### Microsoft Font Validator

Font Validator has useful tests for a font's glyf table. We use [Hintak's fork](https://github.com/HinTak/Font-Validator).

* download the latest [release](https://github.com/HinTak/Font-Validator/releases) for your OS.
* unzip it
* Change the unzipped binary's permissions, `chmod 755 FontValidator`
* Move the binary to your bin folder, `mv /path/to/unzipped/FontValidator /usr/local/bin/FontValidator`

