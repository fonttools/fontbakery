## Font Bakery Install Instructions for MacOS

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

#### Additional dependencies

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

* go to https://developer.apple.com/download/more/?=font
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

