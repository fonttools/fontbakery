# macOS Installation Guide

You'll need Python 3.6 (or newer) to run Font Bakery. Install the [`python` formula](https://formulae.brew.sh/formula/python) with the [Homebrew](https://brew.sh) package manager using the instructions below.

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

### Apple OS X Font Tools

Apple provides various font utilities, and `ftxvalidator` is especially useful as it runs the same checks that are run for users when they install a font using Font Book.  Please note that the use of the OS X Font Tools application `ftxvalidator` requires *macOS v10.13 or greater* before you attempt to install the application using the instructions below.

You must use your Apple ID to sign in to [https://developer.apple.com](https://developer.apple.com) and then:

* go to [https://developer.apple.com/download/more/?=font](https://developer.apple.com/download/more/?=font)
* download `Font_Tools_for_Xcode_9.dmg`
* double-click on `Font_Tools_for_Xcode_9.dmg`
* double-click on `macOS Font Tools.pkg`
* follow the instructions to install, clicking "continue", "agree", "install", etc

If you wish to run the installation process in Terminal, you can do it this way:

```
cd ~/Downloads/ ;
hdiutil attach osxfonttools.dmg ;
mkdir -p /tmp/ftx ;
cd /tmp/ftx ;
cp "/Volumes/OS X Font Tools/OS X Font Tools.pkg" . ;
xar -xf "OS X Font Tools.pkg" ;
cd fontTools.pkg/ ;
cat Payload | gunzip -dc | cpio -i ;
sudo mv ftx* /usr/local/bin/ ;
```

### Microsoft Font Validator

Font Validator has useful tests for a font's glyf table. We use [Hintak's fork](https://github.com/HinTak/Font-Validator).

* download the latest [release](https://github.com/HinTak/Font-Validator/releases) for your OS.
* unzip it
* Change the unzipped binary's permissions, `chmod 755 FontValidator`
* Move the binary to your bin folder, `mv /path/to/unzipped/FontValidator /usr/local/bin/FontValidator`

