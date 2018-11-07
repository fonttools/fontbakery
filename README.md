[![Latest PyPI Version](https://img.shields.io/pypi/v/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Python](https://img.shields.io/pypi/pyversions/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://github.com/googlefonts/fontbakery/blob/master/LICENSE.txt)

# [![Font Bakery](data/logo.png)](https://fontbakery.com)

Font Bakery is a command-line tool for checking the quality of font projects. 
It currently comes with checks for OpenType files, at 3 levels: 
Format specifications, distributor requirements, and custom checks.

For a full introduction, [check out the Typecon 2018 presentation deck](https://docs.google.com/presentation/d/14dU3cUXelwvpVokhKYmJ6jT51AASDaOFyEUSdxb0RAg/)

For full developer documentation, check out [font-bakery.readthedocs.io](https://font-bakery.readthedocs.io)

Font Bakery has an active community of contributors from foundries around the world, including Adobe Typekit, Dalton Maag, Type Network, and Google Fonts.

Font Bakery is not an official Google project, and Google provides no support for it.
However, throughout 2018 the project maintainers Felipe Corrêa da Silva Sanches <juca@members.fsf.org> and Lasse Fister <commander@graphicore.de> were funded by the Google Fonts team.

Font Bakery is available under the Apache 2.0 license.

## Install

See the Font Bakery Installation Guide for your platform:

- [GNU + Linux](https://font-bakery.readthedocs.io/en/latest/user/installation/install-gnu-linux.html)
- [macOS](https://font-bakery.readthedocs.io/en/latest/user/installation/install-macos.html)
- [Windows](https://font-bakery.readthedocs.io/en/latest/user/installation/install-windows.html)

## Usage

See the [Font Bakery Command Line Usage Guide](https://font-bakery.readthedocs.io/en/latest/user/USAGE.html).

## Web Dashboard

A web dashboard for monitoring check-results of project collections is at <https://github.com/googlefonts/fontbakery-dashboard>

## History

The project was initiated by Dave Crossland in 2013 to accelerate the onboarding process for Google Fonts. 
In 2017 Lasse Fister and Felipe Sanches rewrote it into a modern, modular architecture suitable for both individuals and large distributors. Felipe has maintained the check contents since 2016.

Lasse also began a sister project, [Font Bakery Dashboard](https://GitHub.com/GoogleFonts/Fontbakery-Dashboard):
A UI and a cloud system that scales up for checking 1,000s of font files super fast and in parallel, by using 1,000s of "container" virtual machines. See his [TypoLabs 2018 talk on YouTube](https://www.youtube.com/watch?v=Kqhzg89zKYw).

Most of the checks are for OpenType binary files, and project metadata files. 
(Currently, the Google Fonts `METADATA.pb` files are supported.)

To learn more about writing custom checks, see [docs/source/developer/writing-specifications.md](https://font-bakery.readthedocs.io/en/latest/developer/writing-specifications.html)

If you are developing a font project publicly with Github (or a similar host) you can set up a Continuous Integration service (like [Travis](https://www.travis-ci.org)) to run Font Bakery on each commit, so that with each update all checks will be run on your files.

## Contributing

See the [Font Bakery developer documentation](https://font-bakery.readthedocs.io/en/latest/developer/contrib-getting-started.html).
