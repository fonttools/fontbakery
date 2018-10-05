## Font Bakery Install Instructions for Windows

You'll need Python 3.6 (or newer) to run FontBakery, get it from www.python.org.

To install:

    pip install fontbakery
    
To upgrade:

    pip install --upgrade fontbakery
    
Should the above commands give you permission errors, try installing FontBakery into your user directory:

    pip install --user fontbakery

You then need to add the directory to your environment path. Follow all ways on https://superuser.com/questions/949560/how-do-i-set-system-environment-variables-in-windows-10 until you get to the dialog where you can set variables either system-wide or for your user account. What you need to do is add `%LOCALAPPDATA%\Python\PythonYOURPYTHONVERSION\Scripts` to your user account's PATH variable, e.g. `%LOCALAPPDATA%\Python\Python36\Scripts` for Python 3.6. 

If this doesn't work for you, wait for the next release of FontBakery after 0.5.1 and use `py -3 -m fontbakery` everywhere you'd use the command `fontbakery`.

### Additional Dependencies

#### OTS - Opentype Sanitizer

1. Grab a Windows release from https://github.com/khaledhosny/ots/releases
2. Put the contained `.exe` files somewhere and remember where
3. Repeat the steps above to add fontbakery to the PATH variable and add the directory where you put the `.exe`s this time.

#### FontForge

1. Grab a Windows release from https://github.com/fontforge/fontforge/releases
2. ???

#### Microsoft Font Validator

1. Grab a Windows release from https://github.com/HinTak/Font-Validator/releases (e.g. `FontVal-something-win32+64.zip`)
2. Extract the archive somewhere and remember where
3. Repeat the steps above to add fontbakery to the PATH variable and add the directory where you extracted the `FontValidator.exe`.

#### ftxvalidator

Not available for Windows.
