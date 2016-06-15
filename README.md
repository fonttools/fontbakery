[![Latest PyPI Version](https://img.shields.io/pypi/v/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Python](https://img.shields.io/pypi/pyversions/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)

# ![Font Bakery](data/logo.png)

Font Bakery is a command-line tool for testing font projects.
It runs checks on TrueType files.

If you are developing a font project publicly with Github (or a similar host) you can set up a Continuous Integration service (like [Travis](https://www.travis-ci.org)) to run FontBakery on each commit, so that with each update your files are tested.

Font Bakery is not an official Google project, and Google provides no support for it.

## Usage

    cd ~/path/to/fontproject/;
    fontbakery-check-ttf.py *.ttf;

For more detailed output, run in verbose mode:

    fontbakery-check-ttf.py --verbose *.ttf

It may fix some problems, and save `*.ttf.fix` files in the same directory as the original `.ttf` files.

The check results will be saved to a file called fontbakery-check-results.json.
You can view a summary report by running:

    python -m SimpleHTTPServer

And then opening http://0.0.0.0:8000/ in a web-browser.

## Install

### Mac OS X

```sh
# install os x developer tools and the homebrew package manager
xcode-select --install;
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)";

# install ots
brew tap davelab6/webfonttools; 
brew update; 
brew install ots --HEAD; 

# install fontforge
brew install python giflib libspiro icu4c;
brew install fontforge --with-extra-tools --HEAD ; 

# install fonttools
easy_install pip;
pip install --upgrade git+https://github.com/behdad/fontTools.git; 

# install pyfontaine
CFLAGS=-I/usr/local/opt/icu4c/include LDFLAGS=-L/usr/local/opt/icu4c/lib pip install pyicu;
pip install --upgrade git+https://github.com/davelab6/pyfontaine.git; 

# install travis, for setting up CI
sudo gem install travis; # fontbakery dependencies

# install fontbakery
pip install --upgrade git+https://github.com/googlefonts/fontbakery.git;
```

### GNU+Linux

```sh
# install fontforge
sudo add-apt-repository --yes ppa:fontforge/fontforge;
sudo apt-get update -qq;
sudo apt-get install python-fontforge

# install pyfontaine
sudo apt-get install libicu-dev git;
sudo pip install pyicu;
pip install --upgrade git+https://github.com/davelab6/pyfontaine.git; 

# install ots from source
git clone https://github.com/khaledhosny/ots.git; 
cd ots; 
./autogen.sh;
./configure;
make CXXFLAGS=-DOTS_DEBUG;
sudo make install;
cd ..;
rm -rf ots;

# install fonttools
pip install --upgrade git+https://github.com/behdad/fontTools.git;

# install fontbakery
pip install --upgrade git+https://github.com/googlefonts/fontbakery.git; 
```
