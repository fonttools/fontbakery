title: Documentation

Project in development mode, for more information please go to [project page](https://github.com/xen/fontbakery/)

## About the Font Bakery Project

Font Bakery is a font build service. The vision is to bring the [Continuous Integration](http://en.wikipedia.org/wiki/Continuous_integration) best practices of software development to [type design](http://en.wikipedia.org/wiki/Type_design).

You give it a font project git repository, tell it which license the project is under, which font source files you wish to build into binaries, and set some build options. It then runs tests on the sources, and if they pass, builds the fonts and runs further tests on the binaries.

For more information (and to report any issues, make feature requests, or even contribute code) please see the [project page on GitHub](https://github.com/xen/fontbakery/).

### Adding Checks

To add a new set of checks, open /checker/base_suite/fontforge_suite/ and copy and paste an existing set of checks (eg, fftest.py) and give it a new filename. For example, my_checks.py. Then open __init__.py in that same folder and append a new import line, to run the tests in that file. For example, `from .my_checks import *`. Add your tests to that file. Restart Bakery. 

TODO: Explain the new property `target = 'result'` or `target = 'upstream'`

### bakery.yml 

For documentation of the bakery.yml file, please see the files [/bakery/bakery.defaults.yaml](https://github.com/xen/fontbakery/blob/master/bakery/bakery.defaults.yaml) and [/bakery/bakery.example.yaml](https://github.com/xen/fontbakery/blob/master/bakery/bakery.example.yaml)
