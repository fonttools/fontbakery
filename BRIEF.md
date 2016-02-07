# Font Bakery Product Requirements Document

The Font Bakery project develops tools for font production.

This document sets out the product's requirements and design principles, what designers call a "brief."

**Note: The command examples below set out how tools ought to work, and are not examples for use, just yet.**

## 1. Purpose

The primary purpose of the project is to accelerate the on-boarding of new font families into the Google Fonts library. 

To achieve this we develop tools to sanity-check and fix the files that comprise a single Google Fonts family: TTF fonts, an API metadata file, and a description file. 

These tools are used by @davelab6 to onboard both new families and updates to existing families. 
By making them available to all type designers and font engineers, we hope to empower everyone to get their font projects into a complete and tested state and ready to onboard into Google Fonts. 
The tools are command-line based to allow work on various platforms in a consistent and reproducible way.

This set of command-line programs reflect the [Unix Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy):

* Do one thing and do it well, 
* work together, and
* work in similar/uniform way.

A suite of small command-line tools is preferable to a large object oriented application with a graphical user interface.
The tools are individually simple, on the level of shell scripting, and written in Python. 
The use of Python allows direct access to internal font tables using the fonttools package, already popular with the professional font development community. 

We hope that these tool will be useful for font developers who are contributing to the Google Fonts collection, and can avoid them individually duplicating their own technical QA solutions. 
Existing font checking tools from other projects and companies are integrated to avoid duplication. 
We also aim to avoid development distractions. 
For example, to access internet resources we use [GNU wget](https://en.wikipedia.org/wiki/Wget) and other common utilities.

#### 1.1 terminology

An individual user-ready font file is normally referred to as a 'TTF' file, because it uses the `.ttf` extension and is in the TrueType flavour of the OpenType font standard.

A font family consists of 1 to 18 font files that belong together because they are designed to work together and share common visual traits. 
Familiar examples are Regular, Bold, Italic, and Bold Italic files.
The Google Fonts API presents these with the same family name, and some Font Bakery tools process the files as a single family group. 

Font Bakery tools provide two main actions:

1. 'check' operations
2. 'hotfix' operations

Check operations validate fonts with read-only processes and only output diagnostic information, which in verbose mode includes confirmations.
They do not modify the input font files in any way because they are intended to provide feedback to font designers and engineers to decide how to resolve them, such as making corrections to source files and rebuilding the fonts.

Autofix operations create new font files, by appending `.fix` to the filename. 

## 2. Onboarding New and Updated Families

#### 2.1 checking TTFs individually

A single TTF can be validated using:

    ~/fonts/ofl/family $ fontbakery-check-ttf *.ttf ;

In addition to the checks written for Font Bakery, other validation software will also be run to validate the file (such as ots, nototools, Microsoft Font Validator, Apple Font Validator, FontForge, GlyphNanny, etc.)

For example:

    ~/fonts/ofl/family $ for font in `ls -1 *ttf` ; do \
                           echo $font ; ot-sanitise $font ; 
                         done ;

#### 2.2 checking TTFs as a family

A family of TTFs can be validated using:

  ~/fonts/ofl/family$ fontbakery-check-ttf-family *.ttf ;

Some checks must be done by comparing all 1 to 18 font files in a family in order to conclude that their data is correct.

#### 2.3 hot-fixing TTFs

Many common issues can be 'hot fixed.'
A hotfix is a modification to a TTF file itself, a last-minute change, or useful to compare against when fixing the source files and compiling a new font without the issue.

    ~/fonts/ofl/family $ fontbakery-check-ttf *.ttf --autofix ;
    $ rm *.ttf ;
    $ rename s/ttf.fix/ttf/g ;

    ~/fonts/ofl/family $ fontbakery-check-ttf-family *.ttf --autofix ;
    $ rm *.ttf ;
    $ rename s/ttf.fix/ttf/g ;

#### 2.4 generating others required files

A `METADATA.pb` file and `DESCRIPTION.en_us.html` file must be generated:

    ~/fonts/tools $ ./add_font.py ../ofl/family ;

This file can not be generated completely and must be manually edited. 

#### 2.5 checking everything is in sync and correct

    ~/fonts/ofl $ mv family family-old ;
    ~/fonts/ofl $ mv /path/to/new/version family ;
    ~/fonts/tools $ fontbakery-check-family ../ofl/family ;
    ~/fonts/tools $ ./sanity_check.py ../ofl/family ;

#### 2.6 comparing new versions to the ones in production to avoid regressions

    ~/fonts/ofl $ ttx -s family-old/*ttf family/*ttf ;
    $ meld family-old/ family/ ;
    $ rm family-old/*ttx family/*ttx ;

## 3. Collection Management

#### 3.1 Check the entire collection

The ultimate aim is a single master check script that all families pass.

    ~/fonts $ fontbakery-check-collection . ;
    $ 

#### 3.2 Web dashboard

In order to develop the collection to the point all families and fonts pass all tests, we will develop a web dashboard that shows their progress against this goal.

## 4. Source Management

Last minute hotfixing of TTFs is ideally unnecessary. 
Our ultimate aim is that all fonts in the Google Fonts catalog have source repositories in [github.com/googlefonts](https://github.com/googlefonts) that are error-free. 
This can be achieved with [Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration) services like [Travis](https://www.travis-ci.org)) that alert designers about issues and regressions as they happen.

To support this way of developing fonts, we will develop tools for checking font source files.

Some font project upstreams do not provide binaries, or only provide OTF fonts, so we will also develop example "build scripts" that automate the compilation of TTF fonts from source files.

These source-file focused tools supplement the TTF tools. 
