## Font Bakery Install Instructions

### macOS

Minimal install procedure:

1. Install macOS developer tools and the homebrew package manager:

    xcode-select --install;
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)";

2. Install Homebrew Python 3

    brew install python


3. Use pip3 to install fontbakery

    pip3 install fontbakery

#### Upgrades

If you already installed a previous version of Font Bakery, upgrade to a newer version with:

    pip3 install --upgrade fontbakery

#### macOS Additional dependencies

##### OTS: OpenType Sanitizer

This checker is embedded in Chrome and Firefox, so it is important that font files pass OTS.
If available, Font Bakery will wrap around OTS and run it as part of its standard checking.
Install it with:

    curl -L -O https://github.com/khaledhosny/ots/releases/download/v7.1.7/ots-7.1.7-osx.zip
    unzip ots-7.1.7-osx.zip
    mv ots-7.1.7-osx/ots-sanitize /usr/local/bin/ots-sanitize
    rm -rf ots-7.1.7-osx
    rm ots-7.1.7-osx.zip


##### FontForge

FontForge has some font checking features, which Font Bakery will also wrap around and run, if available.
Install it with:

    brew install giflib libspiro icu4c;
    brew install fontforge --with-extra-tools;

##### Apple OS X Font Tools

Apple provides various font utilities, and `ftxvalidator` is especially useful as it runs the same checks that are run for users when they install a font using Font Book.  Please note that the use of the OS X Font Tools application `ftxvalidator` requires *macOS v10.13 or greater* before you attempt to install the application using the instructions below.

You must use your Apple ID to sign in to http://developer.apple.com and then:

* download `Font_Tools_for_Xcode_9.dmg`
* double-click on `Font_Tools_for_Xcode_9.dmg`
* double-click on `macOS Font Tools.pkg`
* follow the instructions to install, clicking "continue", "agree", "install", etc

If you wish to run the installation process in Terminal, you can do it this way:


    cd ~/Downloads/ ;
    hdiutil attach osxfonttools.dmg ;
    mkdir -p /tmp/ftx ;
    cd /tmp/ftx ;
    cp "/Volumes/OS X Font Tools/OS X Font Tools.pkg" . ;
    xar -xf "OS X Font Tools.pkg" ;
    cd fontTools.pkg/ ;
    cat Payload | gunzip -dc | cpio -i ;
    sudo mv ftx* /usr/local/bin/ ;

##### Microsoft Font Validator

TODO - see [#1929](https://github.com/googlefonts/fontbakery/issues/1928)

### GNU+Linux

To install:

    pip install fontbakery;
    
To upgrade:

    pip install --upgrade fontbakery;

#### GNU+Linux Additional Dependencies

##### OTS

From source:

    git clone https://github.com/khaledhosny/ots.git;
    cd ots;
    ./autogen.sh;
    ./configure;
    make CXXFLAGS=-DOTS_DEBUG;
    sudo make install;
    cd ..;
    rm -rf ots;

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

