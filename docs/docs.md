title: Documentation

Project in development mode, for more information please go to [project page](https://github.com/xen/fontbakery/)

### Adding Checks

To add a new set of checks, open /checker/base_suite/fontforge_suite/ and copy and paste an existing set of checks (eg, fftest.py) and give it a new filename. For example, my_checks.py. Then open __init__.py in that same folder and append a new import line, to run the tests in that file. For example, `from .vertical_metrics import *`. Add your tests to that file. Restart Bakery. 