## Font Bakery Install Instructions for GNU+Linux

To install:

    pip install fontbakery;
    
To upgrade:

    pip install --upgrade fontbakery;

#### Additional Dependencies

##### FontForge

From a PPA on Ubuntu:

    sudo add-apt-repository --yes ppa:fontforge/fontforge;
    sudo apt-get update -qq;
    sudo apt-get install python-fontforge

##### Microsoft Font Validator

A prebuilt binary of the Microsoft Font Validator is currently available at the `prebuilt/fval` directory in this repo.
(The corresponding source code is available under a free license at https://github.com/Microsoft/Font-Validator).
In order to enable this check, you'll need to have the mono runtime installed in your system.
You'll also need to have `FontValidator.exe` available in the system path.
Try:

    sudo apt-get install mono-runtime libmono-system-windows-forms4.0-cil;
    export PATH=$PATH:$FONTBAKERY_GIT_REPO/prebuilt/fval;

...where `$FONTBAKERY_GIT_REPO` should be the name of the directory where you checked out Font Bakery source code.
Obviously, you can also use any other alternative way of making `FontValidator.exe` available in your system path.

FontValidator includes some hinting instruction validation checks.
These rely on a customized version of the Freetype library.
In order to enable those, you'll need to use the custom build available in this repo by doing:

    export LD_PRELOAD=$FONTBAKERY_GIT_REPO/prebuilt/custom_freetype/lib/libfreetype.so

The corresponding modified freetype source code is available at <https://github.com/felipesanches/freetype2>

If your vanilla system freetype is used instead, then all FontValidator checks will still be run, except for the hinting validation ones.

##### Remote ftxvalidator

The script available at `prebuilt/workarounds/ftxvalidator/ssh-implementation/ftxvalidator` let's you execute the Mac OS tool `ftxvalidator` on a remote host. It is designed as a drop in replacement to be put in your `/usr/local/bin` directory.

In order to use it you must also add your client's ssh public key to `.ssh/authorized_keys` on the remote machine.

