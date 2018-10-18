# Product Requirements

The Font Bakery project develops tools for font production.

This document sets out the product's requirements and design principles, what designers call a 'brief.'

**Note: The command examples below set out how tools ought to work, and are not examples for use.**

## 1. Purpose

The primary purpose of the project is to accelerate the on-boarding of font families into font distribution systems, both adding new ones and updating exisiting ones.

To achieve this we develop tools to sanity-check the files that comprise a font project: OpenType font files, a metadata files, and description files. 

By making these tools available publicly to all type designers and font engineers, we hope to empower (a) everyone to keep their font projects in a complete, valid and checked state; and (b) to make the live of on-boarding teams at all major font distributors easier. 

These tools were initially made for use by the Google Fonts team to onboard into Google Fonts library, and for the font developers contributing there. One reason Google Fonts invests in this project
is because the earlier that font designers "do the right thing," the less work there is at project delivery time for both them and the Google Fonts team. 

We expect this is true for all type designers and font distributors, so Font Bakery is designed to be modular and vendor-neutral so that it can be widely used.

We hope Font Bakery will be an educational resource for learning more about technical aspects of type design. Everyone is invited to try the tools and share their experience and feedback.

A long term vision is for the tools to be precise enough that contracts can be agreed which specify that projects must pass certain sets of checks to be considered complete.

#### 1.1 Technical Aims

The tools are command-line based, and work on GNU+Linux, macOS and Windows in a consistent and reproducible way.

##### 1.1.1 Wrap Existing Checkers

Existing font checking tools from other projects and companies are integrated to avoid duplication, including:

* [OpenType Sanitizer](https://github.com/khaledhosny/ots)
* Apple's `ftxvalidator` tool, when available
* [HinTak Font Validator](https://github.com/HinTak/Font-Validator)
* [FontForge](https://fontforge.github.io)

##### 1.1.2 Python

Each tool is as simple as possible, and everything is written in Python. 

The use of Python allows direct access to internal font tables using the [fonttools](https://github.com/fonttools/fonttools) package, already popular in the professional font development community. 

For Python code style, we conform to [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

##### 1.1.3 No Distractions

While developing Font Bakery, we aim to avoid development distractions. 
For example, to access internet resources we may use our own native Python utility methods for simple cases, and [GNU wget](https://en.wikipedia.org/wiki/Wget) or other common system utilities for more complex cases (such as resuming large files.)

#### 1.2 Terminology

An individual user-ready font file is normally referred to as a 'TTF' file, because it uses the `.ttf` extension and is in the TrueType flavour of the OpenType font standard.

A font family consists of 1 to 18 font files that belong together because they are designed to work together and share common visual traits. 
Familiar examples are Regular, Bold, Italic, and Bold Italic files.
The Google Fonts API presents these with the same family name. 
Some typeface projects are developed with other platforms in mind (such as Adobe CC Suite tools) that support many more than 18 styles in a family, and in those cases we must adjust the files to work as a set of families of 1–18 styles. 
Some Font Bakery tools process a set of files that make up a family that include both font files as well as metadata files. 


Check operations validate fonts with read-only processes and only output diagnostic information, which in verbose mode includes confirmations; without passing a verbose argument to a tool, if everything is correct then there will be no output. 

Check operations do not modify the input font files in any way, because they are intended to provide feedback to font designers and engineers to decide how to resolve them, such as making corrections to source files and rebuilding the fonts.

## 2. Onboarding New and Updated Families

#### 2.1 checking TTFs individually

A single TTF can be validated using:

    ~/fonts/ofl/family $ fontbakery-check-ttf.py *.ttf ;

In addition to the checks specifically provided by FontBakery, this script also invokes other validation software such as ot-sanitize, nototools, Microsoft Font Validator, Apple Font Validator, FontForge, GlyphNanny, etc.

#### 2.2 checking TTFs as a family

If a set of TTFs is provided, it will be validated as a single family:

    ~/fonts/ofl/family$ fontbakery-check-ttf.py *.ttf ;

Some of these checks specifically target up to 18 font files in a family in order to conclude that their data is correct and coherent. Also the contents of METADATA.pb files are validated against the entries in the OpenType tables of the font binaries. If this checking is not needed it can be disabled by using the --skip command-line switch.

#### 2.4 generating other required files

The `METADATA.pb` and `DESCRIPTION.en_us.html` files can be generated by using the add_font.py script which is available at the https://github.com/google/fonts repo:

    ~/fonts/tools $ ./add_font.py ../ofl/family ;

This file can not be generated completely and must be manually edited. 

#### 2.5 comparing new versions to the ones in production to avoid regressions

_To review fonts technically,_ that could be done by comparing the TTX versions of the 2 sets of fonts:

    ~/fonts/ofl $ ttx -s family-old/*ttf family/*ttf ;
    $ meld family-old/ family/ ;
    $ rm family-old/*ttx family/*ttx ;

This is now possible by comparing the fonttools font objects automatically, with [fontdiffenator](https://github.com/googlefonts/fontdiffenator). 

_To review fonts visually,_ compare with the [gfregression](https://github.com/googlefonts/gfregression) web application.
This will eventually be integrated into the [fontbakery-dashboard](https://github.com/googlefonts/fontbakery-dashboard).

## 3. Collection Management

#### 3.1 Check the entire collection

The ultimate aim is a single master check script that all families pass.

    ~/fonts $ fontbakery-check-collection . ;
    $ 

#### 3.2 Web Checker

In order to make it as easy as possible for font designers to check their fonts with Font Bakery, we developed a web based interface that allows users to drop fonts on a web page and see a report page with all the check result details: 

<http://fontbakery.com>

<https://github.com/googlefonts/fontbakery-dashboard>

#### 3.3 Web Dashboard

A live report about the quality of a font project encourages "test-driven-development" for fonts. 

Project Managers can specify that Developers must demonstrate their projects pass certain sets of checks to consider a milestone completed.

In order to develop the collection to the point all families and fonts pass all checks, we developed a web dashboard that shows their progress against this goal, with a table with rows for families, and columns for check results. 

As of June 2018, the dashboard table shows each row with a set of columns for each stage of development, with inner columns for check result details, that can be expanded to show all check types. Each set has a link to drill down to a report page. 

During the summer of 2017, the dashboard table will be refined to offer both a more high-level overview, and more specific views of a distibutor's library. 

The high-level overview will indicate the aggregate progress of the collection towards being without any issues at all stages; such as with 'burn down' charts.

It will also allow for upcoming projects to measure their quality and progress towards launching, and for tracking which projects are launched but do not have checked upstreams.

The dashboard will check 6 stages that a project passes through:

1. the font developer's workstation, using the drag-and-drop UI;
2. the font developer's Github repo, using Github Web Hooks;
3. the font developer's Github repo's release page (often a hand-crafted ZIP);
4. the github.com/google/fonts repo;
5. the Google Fonts staging server;
6. the Google Fonts production servers;

The dashboard will integrate with the Github API, to make it convenient to create and track issues based on the reports, and pull requests when a font project release is ready to move forwards a stage.

## 4. Source Management

Our ultimate aim is that all fonts in the Google Fonts catalog have source repositories in [github.com/googlefonts](https://github.com/googlefonts) that are error-free. 
This can be achieved with a [Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration) service (like [Travis](https://www.travis-ci.org)) that alerts designers about issues and regressions as they happen.

To support this way of developing fonts, we will develop tools for checking font source files.
These source-file focused tools supplement the TTF tools. 
Some font project upstreams do not provide binaries, or only provide OTF fonts, so we will also develop example "build scripts" that automate the compilation of TTF fonts from source files.

#### 4.1 Checking source files individually

These scripts likely need to be run inside font editors, and thus should be packaged as extension for the editors in the normal way. 
However, should it be possible to run them similar to the above TTF check tools, they would work like this:

    ~/fonts/ofl/family $ fontbakery-check-source [*.glyphs, .ufo, .sfd, .vfb, .xfo]

#### 4.2 Building source files into binaries

This will be done with [fontmake](https://github.com/googlei18n/fontmake) or [afdko](https://github.com/adobe-type-tools/afdko).

#### 4.3 Continuous Integration

We will support two C.I. systems: Our own, and Travis.

##### 4.3.1 Travis

Travis setup is complicated. 
Deployment typically requires the user to copy/paste/tweak a rather complex setup file. 
It could be made simpler by providing scripts to set it up, and we have 3 already:

    ~/fonts/ofl/family $ fontbakery-travis-deploy.py
    ~/fonts/ofl/family $ fontbakery-travis-init.py
    ~/fonts/ofl/family $ fontbakery-travis-secure.sh

We will add a `fontbakery-travis-check.py` script that checks that it is configured correctly, a build badge is in README, etc.

##### 4.3.2 Font Bakery Cloud

The Font Bakery Dashboard can be run on any [Kubernetes](https://kubernetes.io) container provider, such as Google Cloud Platform, Amazon Web Services, Microsoft Azure, Digital Ocean, DreamCompute, etc.
