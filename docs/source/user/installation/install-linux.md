# Linux + GNU Installation Guide

You'll need Python 3.6 (or newer) to run FontBakery. Install with your Linux package manager or from [www.python.org](https://www.python.org).

## Install

    pip install fontbakery

## Upgrade

    pip install --upgrade fontbakery

## Additional Dependencies

The following are optional dependencies that you can install to extend the functionality of Font Bakery.  Please note that some tests will not be executed if these optional dependencies are not present on your system.

### FontForge

From a PPA on Ubuntu:

    sudo add-apt-repository --yes ppa:fontforge/fontforge;
    sudo apt-get update -qq;
    sudo apt-get install python-fontforge

### Microsoft Font Validator

Font Validator has useful tests for a font's glyf table. We use [Hintak's fork](https://github.com/HinTak/Font-Validator).

* download the latest [release](https://github.com/HinTak/Font-Validator/releases) for your OS.
* unzip it
* Change the unzipped binary's permissions, `chmod 755 FontValidator`
* Move the binary to your bin folder, `mv /path/to/unzipped/FontValidator /usr/local/bin/FontValidator`


### Remote ftxvalidator

The script available at `prebuilt/workarounds/ftxvalidator/ssh-implementation/ftxvalidator` lets you execute the macOS tool `ftxvalidator` on a remote host. It is designed as a drop-in replacement to be put in your `/usr/local/bin` directory.

In order to use it you must also add your client's ssh public key to `.ssh/authorized_keys` on the remote machine.
