# Windows Installation Guide

You'll need Python 3.7 (or newer) to run FontBakery.  Use the instructions provided at  [www.python.org](https://www.python.org) to download and install Python 3.7+ on the Windows platform.

## Install

    pip install fontbakery

Should the above commands give you permission errors, try installing FontBakery into your user directory:

    pip install --user fontbakery

## Upgrade

    pip install --upgrade fontbakery


You then need to add the directory to your environment path. Follow all ways on https://superuser.com/questions/949560/how-do-i-set-system-environment-variables-in-windows-10 until you get to the dialog where you can set variables either system-wide or for your user account. What you need to do is add `%LOCALAPPDATA%\Python\PythonYOURPYTHONVERSION\Scripts` to your user account's PATH variable, e.g. `%LOCALAPPDATA%\Python\Python37\Scripts` for Python 3.7. 

If this doesn't work for you, use `py -3 -m fontbakery` everywhere you'd use the command `fontbakery`.

## Additional Dependencies

The following are optional dependencies that you can install to extend the functionality of Font Bakery.  Please note that some tests will not be executed if these optional dependencies are not present on your system.

### Microsoft Font Validator

Font Validator has useful tests for a font's glyf table. We use [Hintak's fork](https://github.com/HinTak/Font-Validator).

1. Download the latest [release](https://github.com/HinTak/Font-Validator/releases) for Windows (e.g. `FontVal-something-win32+64.zip`).
2. Extract the archive somewhere and remember where
3. Repeat the steps above to add fontbakery to the PATH variable and add the directory where you extracted the `FontValidator.exe`.

