# Font Bakery Product Requirements Document

This document sets out the product's requirements and design principles, what designers call a "brief."

## 1. Sanity Checking

The primary purpose of the project is to accelerate the on-boarding of font families into the Google Fonts library. 

The project achieves this by developing tools for use 'at the coalface,' that sanity-check TTF and related files needed to onboard a single family into Google Fonts.

This set of command-line programs should reflect some [Unix Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy):

* Do one thing and do it well, 
* work together, and
* work in similar/uniform way.

They are simple, on the level of shell scripting done with in Python in order to access font internals via fonttools, rather than a large object oriented application.

They avoid crafting custom pure-Python solutions to side-problems and rely on commonly installed utilities, such as using [GNU wget](https://en.wikipedia.org/wiki/Wget) to fetch files from the internet. 

#### 1.1 checking TTFs individually

In addition to our own checks, this will check the TTFs with other projects such as ots, nototools, Microsoft Font Validator, Apple Font Validator, FontForge, GlyphNanny, and others.

    ~/fonts/ofl/family $ fontbakery-check-ttf.py *ttf

#### 1.2 checking TTFs as a family

#### 1.3 hot-fixing TTFs

Many common issues can be hot-fixed using fontTools.

    ~/fonts/ofl/family $ fontbakery-check-ttf.py *ttf --autofix
    $ rm *ttf;
    $ rename s/ttf.fix/ttf/g;

#### 1.4 generating others required files

    ~/fonts/tools $ ./add_font.py ../ofl/family;

#### 1.5 checking everything is in sync and correct

    ~/fonts/tools $ ./sanity_check.py ../ofl/family;

#### 1.6 comparing new versions to the ones in production to avoid regressions

    ~/fonts/ofl $ ttx -s family-old/*ttf family/*ttf;
    $ meld family-old/ family/;
    $ rm family-old/*ttx family/*ttx;

#### 1.7 sanity-check the entire collection

The ultimate aim is a single master check script that all families pass.

    ~/fonts $ fontbakery-check.py .
    $ 

## 2. Font Building (with Continuous Integration)

Last minute hotfixing of TTFs is ideally unnecessary, so to accelerate the on-boarding of updates made by upstream font developers, we also develop tools for checking source files.

Some font project upstreams do not provide binaries, or only provide OTF binaries, so we develop tools to build fonts from sources.

These source file build and checking tools supplement and feed the first set of tools, and can be used for Continuous Integration of font sources kept in a version control repository (such as Travis and Github.) 

The ultimate aim is that all fonts in the Google Fonts catalog have source repositories in [github.com/googlefonts](https://github.com/googlefonts) that are under continuous version control, so new errors or regressions are prevented at source.

## 3. Web Dashboard

To reach the ultimate aims of the project, a dashboard that measures progress would be great.
