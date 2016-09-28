[![Latest PyPI Version](https://img.shields.io/pypi/v/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Python](https://img.shields.io/pypi/pyversions/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)

# ![Font Bakery](data/logo.png)

Font Bakery is a command-line tool for testing font projects.
It runs checks on TrueType files.

If you are developing a font project publicly with Github (or a similar host) you can set up a Continuous Integration service (like [Travis](https://www.travis-ci.org)) to run FontBakery on each commit, so that with each update your files are tested.

Font Bakery is not an official Google project, and Google provides no support for it.

## Usage

    cd ~/path/to/fontproject/
    fontbakery-check-ttf.py *.ttf

For more detailed output, run in verbose mode:

    fontbakery-check-ttf.py --verbose *.ttf

It may fix some problems, and save `*.ttf.fix` files in the same directory as the original `.ttf` files.

The check results will be saved to a file called fontbakery-check-results.json.

For check results in GitHub Markdown syntax you can use --ghm:

    fontbakery-check-ttf.py --verbose *.ttf --ghm

Optionaly, a web-based visualization of the summary report can be viewed by running:

    python -m SimpleHTTPServer

And then opening http://0.0.0.0:8000/ in a web-browser.

But beware that in order to run the webserver the command above must be executed from the fontbakery project folder and the json file must be available in that same root folder.

### Automated testing of all Google Fonts

If you need to generate a list of all issues in the Google Fonts, you have to have a full checkout of the Google Fonts git repo, and then you can run:

```
sh test_all_gfonts.sh
```

(you'll probably have to edit the first 3 lines in the test_all_gfonts.sh script though, as for now the gfonts repo path is hardcoded in there. I may later make it into a command line parameter)

This will create a folder called check_results and it will run fontbakery on every family from the gfonts git repo, thus generating individual per-font-file reports both in json and in ghmarkdown format. The reports are saved in subdirectories that have names of the families.

It took me 80 minutes to run the full test on the repo. And the resulting check_results folder has got 105Mbytes of json & markdown files. To squeeze it all into a unified report you can run:

```
./fb_summary_report.py
```

and it will write to stdout.

If you rather prefer to save it to a file you can do something like:

```
./fb_summary_report.py > gfonts_check_summary.md
```

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

# install python dependencies
pip install -r requirements.txt

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

# install python dependencies
pip install -r requirements.txt

# install fontbakery
pip install --upgrade git+https://github.com/googlefonts/fontbakery.git; 
```
