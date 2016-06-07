[![Latest PyPI Version](https://img.shields.io/pypi/v/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Python](https://img.shields.io/pypi/pyversions/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![Coveralls.io Test Coverage Status](https://img.shields.io/coveralls/googlefonts/fontbakery.svg)](https://coveralls.io/r/googlefonts/fontbakery)

# ![Font Bakery](Data/logo.png)

Font Bakery is a set of command-line tools for testing font projects, and a web interface for reviewing them.
It runs checks on TrueType files and the test logs can be parsed into graphical views by the Font Bakery web app.

Optionally, if you are developing a font project publicly with Github or a similar host, you can set up a Continuous Integration server like Travis to run FontBakery on each commit, so that with each update your files are tested in the CI server and then uploaded to the project's `gh-pages` branch for browsing and testing live.

Font Bakery is not an official Google project, and Google provides no support for it.

Font Bakery has been presented at the following events:

* 2014-04-03: Libre Graphics Meeting 2014 [slides](https://speakerdeck.com/davelab6/lgm-2014-font-bakery)

## Install

### Mac OS X

Install the dependencies with [Homebrew](http://brew.sh), [PIP](http://pip.readthedocs.org) and [gem](https://rubygems.org):

```sh
xcode-select --install;
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" # install homebrew
brew tap davelab6/webfonttools; 
brew update; 
brew install sfnt2woff sfnt2woff-zopfli woff2 ttf2eot sfntly; # optional web font tools good to have, from davelab6 tap
brew install ots --HEAD; # fontbakery dependency, from davelab6 tap
brew install python giflib libspiro; # fontforge optional dependencies
brew install fontforge --with-extra-tools --HEAD ; # fontforge
brew install libmagic ttfautohint swig; # fontbakery dependencies
easy_install pip # install pip
pip install virtualenv; # optional, can be useful
pip install --upgrade git+https://github.com/behdad/fontTools.git; # fontbakery dependency
pip install --upgrade git+https://github.com/googlefonts/fontcrunch.git; # fontbakery dependency
pip install --upgrade git+https://github.com/davelab6/pyfontaine.git; # fontbakery dependency
sudo gem install travis; # fontbakery dependencies
sudo pip install fontbakery; # fontbakery's latest release
```

Alternatively you can install the current development version with

    sudo pip install git+https://github.com/googlefonts/fontbakery.git; # install fontbakery as root to ensure it uses system python

### GNU+Linux

```sh
sudo add-apt-repository --yes ppa:fontforge/fontforge;
sudo apt-get update -qq;
sudo apt-get install python-fontforge ttfautohint swig libicu-dev git;
sudo pip install pyicu;
pip install git+https://github.com/behdad/fontTools.git;
pip install git+https://github.com/googlefonts/fontcrunch.git; 
pip install git+https://github.com/googlefonts/fontbakery.git; 
git clone https://github.com/khaledhosny/ots.git; # install ots from source
cd ots; 
./autogen.sh;
./configure;
make CXXFLAGS=-DOTS_DEBUG;
sudo make install;
cd ..;
rm -rf ots;
sudo pip install fontbakery; # fontbakery's latest release
```

Alternatively you can install the current development version with

    sudo pip install git+https://github.com/googlefonts/fontbakery.git; # install fontbakery as root to ensure it uses system python

## Usage

All fontbakery commands begin with `fontbakery-`

    cd ~/src/github.com/davelab6/fontproject/
    fontbakery-check-ttf.py *.ttf

It is helpful to run in verbose mode.

    fontbakery-check-ttf.py --verbose *.ttf

The check tool will fix some problems, and save ttf.fix files in the same directory as the original ttf files.

