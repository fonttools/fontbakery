# Font Bakery Product Requirements Document

The Font Bakery project develops tools for font production.

This document sets out the product's requirements and design principles, what designers call a "brief."

**Note: The command examples below set out how tools ought to work, and are not examples for use, just yet.**

## 1. Purpose

The primary purpose of the project is to accelerate the on-boarding of font families into the Google Fonts library, both new families and updates to exisiting ones. 

To achieve this we develop tools to sanity-check and fix the files that comprise a single Google Fonts family: TTF fonts, an API metadata file, and a description file. 

These tools are used by @davelab6 to onboard both new families and updates to existing families. 
By making them available to all type designers and font engineers, we hope to empower everyone to get their font projects into a complete and tested state and ready to onboard into Google Fonts. 
The tools will act as an educational resource for type designers to learn about technical quality issues, because if font designers do the right thing early on that reduces the amount of work at project delivery time. 

The tools are command-line based to allow work on various platforms in a consistent and reproducible way.
They reflect the [Unix Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy):

* Do one thing and do it well, 
* work together, and
* work in similar/uniform way.

A suite of small command-line tools is preferable to a large object oriented application with a graphical user interface.
The tools are individually simple, on the level of shell scripting, and written in Python. 
The use of Python allows direct access to internal font tables using the fonttools package, already popular with the professional font development community. 

Existing font checking tools from other projects and companies are integrated to avoid duplication, such as Apple's `ftxvalidator` tool and Microsoft's Font Validator.

While developing font bakery, we aim to avoid development distractions. 
For example, to access internet resources we may use our own native Python utility methods for simple cases, and [GNU wget](https://en.wikipedia.org/wiki/Wget) or other common system utilities for more complex cases (such as resuming large files.)

For Python code style, we conform to [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

#### 1.1 terminology

An individual user-ready font file is normally referred to as a 'TTF' file, because it uses the `.ttf` extension and is in the TrueType flavour of the OpenType font standard.

A font family consists of 1 to 18 font files that belong together because they are designed to work together and share common visual traits. 
Familiar examples are Regular, Bold, Italic, and Bold Italic files.
The Google Fonts API presents these with the same family name. 
Some typeface projects are developed with other platforms in mind (such as Adobe CC Suite tools) that support many more than 18 styles in a family, and in those cases we must adjust the files to work as a set of families of 1–18 styles. 
Some Font Bakery tools process a set of files that make up a family that include both font files as well as metadata files. 

Font Bakery tools provide two main actions:

1. 'check' operations
2. 'hotfix' operations

Check operations validate fonts with read-only processes and only output diagnostic information, which in verbose mode includes confirmations; without passing a verbose argument to a tool, if everything is correct then there will be no output. 

Check operations do not modify the input font files in any way, because they are intended to provide feedback to font designers and engineers to decide how to resolve them, such as making corrections to source files and rebuilding the fonts.
Hotfix operations do create new font files, by copying the file and modifying that copy, which is saved on disk with the same filename plus `.fix` appended. 

## 2. Onboarding New and Updated Families

#### 2.1 checking TTFs individually

A single TTF can be validated using:

    ~/fonts/ofl/family $ fontbakery-check-ttf.py *.ttf ;

In addition to the checks specifically provided by FontBakery, this script also invokes other validation software such as ot-sanitize, nototools, Microsoft Font Validator, Apple Font Validator, FontForge, GlyphNanny, etc.

#### 2.2 checking TTFs as a family

If a set of TTFs is provided, it will be validated as a single family:

    ~/fonts/ofl/family$ fontbakery-check-ttf.py *.ttf ;

Some of these checks specifically target up to 18 font files in a family in order to conclude that their data is correct and coherent. Also the contents of METADATA.pb files are validated against the entries in the OpenType tables of the font binaries. If this checking is not needed it can be disabled by using the --skip command-line switch.

#### 2.3 hot-fixing TTFs

Many common issues can be 'hot fixed.'
A hotfix is a modification to a TTF file itself, a last-minute change, or useful to compare against when fixing the source files and compiling a new font without the issue.

    ~/fonts/ofl/family $ fontbakery-check-ttf.py *.ttf --autofix ;
    $ rm *.ttf ;
    $ rename s/ttf.fix/ttf/g ;

    ~/fonts/ofl/family $ fontbakery-check-ttf.py *.ttf --autofix ;
    $ rm *.ttf ;
    $ rename s/ttf.fix/ttf/g ;

#### 2.4 generating other required files

The `METADATA.pb` and `DESCRIPTION.en_us.html` files can be generated by using the add_font.py script which is available at the https://github.com/google/fonts repo:

    ~/fonts/tools $ ./add_font.py ../ofl/family ;

This file can not be generated completely and must be manually edited. 

#### 2.5 comparing new versions to the ones in production to avoid regressions

To review fonts technically, compare the TTX versions of the 2 sets of fonts.

    ~/fonts/ofl $ ttx -s family-old/*ttf family/*ttf ;
    $ meld family-old/ family/ ;
    $ rm family-old/*ttx family/*ttx ;

To review fonts visually, compare with Marc Foley's [gfregression](https://github.com/m4rc1e/gfregression) web application.

## 3. Collection Management

#### 3.1 Check the entire collection

The ultimate aim is a single master check script that all families pass.

    ~/fonts $ fontbakery-check-collection . ;
    $ 

#### 3.1 Web Checker

In order to make it as easy as possible for font designers to check their fonts with Font Bakery (see parts 2.1 and 2.2 above) we will develop a web checker that allows users to drop fonts on a web page and see the results of the checking. 

A live report about the quality of a font project encourages test-driven-development for fonts. 
Contracts can specify that projects must pass to be considered complete.

A prototype for this is available at <https://fontbakery.appspot.com>

#### 3.3 Web Dashboard

In order to develop the collection to the point all families and fonts pass all tests, we will develop a web dashboard that shows their progress against this goal with a table with rows for families and columns for stages of development with relevant information. 

Those stage cells may pop-up or link to more detailed information about that stage, such as 'burn down' charts showing the family's status towards being without any issues.
Those stage cells will also indicate the aggregate progress of the collection towards being without any issues. 

It will also allow a set of upcoming projects to measure their quality, and a 'burn down' chart towards their launch in the directory. 

There are 6 stages of progress for a set of TTF files:

1. the font developer's workstation
2. the font developer's Github repo
3. the font developer's Github repo's release page (often a hand-crafted ZIP)
4. the github.com/google/fonts repo
5. the Google Fonts staging server
6. the Google Fonts production servers

The current command-line and web applications are suitable for (1) and Marc Foley's "gfregression" web application (<https://github.com/m4rc1e/gfregression>) can compare fonts in (1) with fonts in (5). 

The dashboard will integrate with the Github Issues API, to make it convenient to create and track issues based on our reports.

A prototype for this is available at <https://googlefonts.github.io/fontbakery>

## 4. Source Management

Last minute hotfixing of TTFs is ideally unnecessary. 
Our ultimate aim is that all fonts in the Google Fonts catalog have source repositories in [github.com/googlefonts](https://github.com/googlefonts) that are error-free. 
This can be achieved with [Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration) services (like [Travis](https://www.travis-ci.org)) that alert designers about issues and regressions as they happen.

To support this way of developing fonts, we will develop tools for checking font source files.
These source-file focused tools supplement the TTF tools. 
Some font project upstreams do not provide binaries, or only provide OTF fonts, so we will also develop example "build scripts" that automate the compilation of TTF fonts from source files.

#### 4.1 Checking source files individually

These scripts likely need to be run inside font editors, and thus should be packaged as extension for the editors in the normal way. 
However, should it be possible to run them similar to the above TTF check tools, they would work like this:

    ~/fonts/ofl/family $ fontbakery-check-source [*.glyphs, .ufo, .sfd, .vfb, .xfo]

#### 4.2 Building source files into binaries

TODO: Link to SFNTMAKE discussion on fonttools issue tracker

#### 4.3 Setting up Travis

Travis setup is complicated. 
Deployment typically requires the user to copy/paste/tweak a rather complex setup file. 
It could be made simpler by providing scripts to set it up, and we have 3 already:

    ~/fonts/ofl/family $ fontbakery-travis-deploy.py
    ~/fonts/ofl/family $ fontbakery-travis-init.py
    ~/fonts/ofl/family $ fontbakery-travis-secure.sh

We could also add a `fontbakery-travis-check.py` script that checks that it is configured correctly, a build badge is in README, etc.

# v0.1.0 Planning

The most simple form for each tool is a linear, imperative programming style (done)

Each tool should only interact with TTF or OTF files with fontTools, or call external tools via shells (done)

Each tool should be structured table by table (not followed this)

Each tool should operate on a single ttLib font object for each file (done)

Each tool should use the Python standard library logging module (done)

Each test should only have a single log entry (done)

Each tool should only interact with UFOs using defcon, specifically the version of defcon that TruFont uses

Each tool should only interact with `.glyphs` files using glyphsLib parser.
