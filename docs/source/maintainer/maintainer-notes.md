# Project Maintainer Notes

## Code Testing

`tox` and `coverage` are used to execute the Font Bakery test suite and line coverage assessment, respectively.  

Use the following command to run all tests:

```
$ tox
```

The coverage report can be found at the end of the test results that are printed to the standard output/error stream.

Continuous integration testing is performed on GitHub Actions. Test jobs can be found at [https://github.com/googlefonts/fontbakery/actions](https://github.com/googlefonts/fontbakery/actions).

## Updating the distribution package

Releases to PyPI are performed by running the following commands (with the proper version number and date):

```sh
# Update the local copy
git checkout main
git fetch upstream
git rebase upstream/main

# Be sure that there's no leftover code-changes in the local copy
git status

# Create a branch for the final tweaks prior to release:
git checkout -b preparing_v0_8_2

# Update the cached list of vendor IDs:
wget https://docs.microsoft.com/en-us/typography/vendors/ --output-document=Lib/fontbakery/data/fontbakery-microsoft-vendorlist.cache
git add -p

# If something changed, commit it:
git commit -m "Updating cache of vendor IDs list from Microsoft's website"

# Check for updates on the Google Fonts Axis Registry textproto files at https://github.com/google/fonts/tree/main/axisregistry
# Newest files must be copied and committed at Lib/fontbakery/data/*.textproto

# Check whether ttfautohint has a newer version available and
# manually update the LATEST_TTFAUTOHINT_VERSION number, if needed:
vim Lib/fontbakery/constants.py
git add -p
git commit -m "Updating LATEST_TTFAUTOHINT_VERSION"

# update the docs so that https://font-bakery.readthedocs.io/
# displays the correct version number
vim docs/source/conf.py
git add -p
git commit -m "update version on docs/source/conf.py"

# send these changes to the public GitHub repo
git push upstream preparing_v0_8_2

# Open a pull request and wait for all code-tests to pass
# or make additional commits until the build is finally green

# Update the local copy
git checkout main
git fetch upstream
git rebase upstream/main

# cleanup
rm build/ -rf
rm dist/ -rf
rm venv/ -rf

# create a fresh python virtual env
virtualenv venv -ppython3
. venv/bin/activate

# Install tox so that we can also run our code tests locally
pip install tox
tox

# If all is good, then make the actual release:
# Register a git tag for this release and publish it
git tag -a v0.8.2 -m "Font Bakery version 0.8.2 (2021-Sep-01)"
git push upstream --tags

# create the package
python setup.py bdist_wheel --universal

# and finally upload the new package to PyPI
pip install twine
twine upload dist/*
```

## Cached Vendor ID data

This project hosts a copy of the Microsoft's Vendor ID list at Lib/fontbakery/Lib/data/fontbakery-microsoft-vendorlist.cache

This is meant only as a caching mechanism. The latest data can always be fetched from Microsoft's website directly at: <https://www.microsoft.com/typography/links/vendorlist.aspx>
