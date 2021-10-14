# GNU + Linux Installation Guide

You'll need Python 3.6 (or newer) to run FontBakery. Install with your GNU+Linux package manager or from [www.python.org](https://www.python.org).

## Install

    pip install fontbakery

## Upgrade

    pip install --upgrade fontbakery

## Additional Dependencies

The following are optional dependencies that you can install to extend the functionality of Font Bakery.  Please note that some tests will not be executed if these optional dependencies are not present on your system.

### Microsoft Font Validator

Font Validator has useful tests for a font's glyf table. We use [Hintak's fork](https://github.com/HinTak/Font-Validator).

* download the latest [release](https://github.com/HinTak/Font-Validator/releases) for your OS.
* unzip it
* Change the unzipped binary's permissions, `chmod 755 FontValidator`
* Move the binary to your bin folder, `mv /path/to/unzipped/FontValidator /usr/local/bin/FontValidator`


