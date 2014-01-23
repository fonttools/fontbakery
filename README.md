<img src="https://raw.github.com/xen/fontbakery/master/docs/image.png">

## Introduction

Font Bakery is a font build service. The vision is to bring the [Continuous Integration](http://en.wikipedia.org/wiki/Continuous_integration) best practices of software development to [type design](http://en.wikipedia.org/wiki/Type_design).

You give it a font project git repository, tell it which license the project is under, which font source files you wish to build into binaries, and set some build options. It then runs tests on the sources, and if they pass, builds the fonts and runs further tests on the binaries.

This project is under active development by Mikhail Kashkin and Dave Crossland.

### Disclaimer

This project was given financial support by Google Fonts team within Google, Inc. The copyright to contributions done with that financial support is owned by Google, Inc. but Font Bakery is not an official Google product.

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

## Contribute

The project is run on Github, in the [typical](http://producingoss.com) free software way - your issues and pull requests are welcome!

### Contributor License Agreement

However, all contributors must agree to the appropriate Google Contributor License Agreement, found here:

http://code.google.com/legal/individual-cla-v1.0.html
http://code.google.com/legal/corporate-cla-v1.0.html

After your contribution is included, you will be listed in CONTRIBUTORS.txt and/or AUTHORS.txt: CONTRIBUTORS is the official list of people who can contribute (and typically have contributed) code to this repository, while the AUTHORS file lists the copyright holders.

A series of videos explaining the project are posting on the [Font Bakery tumblr](http://fontbakery.tumblr.com) and the [first video](http://www.youtube.com/watch?v=paKa_Kok2EA) covers basic functionality and the overall codebase.

### Software License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this work except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

This software has many dependencies under other, compatible, licenses.
