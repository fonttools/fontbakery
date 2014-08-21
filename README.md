<img src="https://raw.github.com/googlefonts/fontbakery/master/docs/image.png">

[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![Coveralls.io Test Coverage Status](https://img.shields.io/coveralls/googlefonts/fontbakery.svg)](https://coveralls.io/r/googlefonts/fontbakery)
[![Drone.io Build Status](https://drone.io/github.com/googlefonts/fontbakery/status.png)](https://drone.io/github.com/googlefonts/fontbakery/latest)

## Introduction

Font Bakery is a font build service. The vision is to bring the [Continuous Integration](http://en.wikipedia.org/wiki/Continuous_integration) best practices of software development to [type design](http://en.wikipedia.org/wiki/Type_design).

You give it a font project in a git repository, tell it which license the project is under, which font source files you wish to build into binaries, and set some build options. It then runs tests on the sources, and if they pass, builds the fonts and runs further tests on the binaries. Finally it prepares the fonts for distribution in the Google Fonts API.

You can publish your git repository conveniently with [Github](http://github.com). If you wish to host your own repository, [GitLab HQ](https://github.com/gitlabhq/gitlabhq) is a good web interface that provides similar functionality to Github.

Throughout 2014 this project is under active development by [Vitaly Volkhov](http://github.com/hash3g). The first year of development over 2013, including the code architecture and design, was done by [Mikhail Kashkin](http://github.com/xen). The project is organised by [Dave Crossland](http://github.com/davelab6)

### Disclaimer

This project was given financial support by [Google Fonts](http://github.com/googlefonts). The copyright to contributions done with that financial support is owned by Google, Inc. but Font Bakery is not an official Google product.

## Installation

The installation process is easy, and full instructions are maintained in the [INSTALL](https://github.com/xen/fontbakery/blob/master/INSTALL.md) file.

## Usage

After installation, this command will update the dashboard stats:

    $ make stats;

This command will start the worker:

    $ make worker;

Then this command will start the web service on a localhost web server:

    $ make run;

Then open [http://localhost:5000](http://localhost:5000) in your browser.

Font Bakery gives a visual indication if the worker is not running.

You may with to clear out all user data:

    $ make clean;

During the development process you may wish to run a fake mail server:

    $ make mail;


### Run bake from console

    $ python fontbakery.py --config /path/to/bakery.yaml /path/to/source.ufo

Supported sources - UFO, TTX, SFD, TTF, OTF, TTX

### Font Tests

Tests are in the `/checker` directory.

The test page shows tests that fail, with the cause of failure. This message is auto generated, but also you can specify them. For example, if this test fails then the message will contain the first and second `assertEqual` arguments:


```py
    def test_metadata_family(self):

        """ Font and METADATA.json have the same name """
        self.assertEqual(self.font.familyname, self.metadata.get('name', None))
```

If this test fails then an error messages will contain the string `msg`:

```py
    def test_em_is_1000(self):

        """ Font em should be equal 1000 """
        self.assertEqual(self.font.em, 1000,

            msg="Font em value is %s, required 1000" % self.font.em)
```

This can help Font Bakery users understand what may be incorrect in their fonts, and tell them what actions they can take to correct their fonts.

### Back Up

Given a default installation, backup `data` directory and `data.sqlite` file. That’s it!

To restore Font Bakery, reinstall it so that files like `local.cfg` are recreated with different Github keys, then copy the `data` directory and `data.sqlite` file into the root directory. That's it!

## Contribution

Please see [CONTRIBUTING.md](./CONTRIBUTING.md)

### Software License

Licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

This software has many dependencies under other, compatible, licenses.
