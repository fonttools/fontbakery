# Font Bakery Miscellaneous Developer Notes

## Code Testing

See [docs/code-testing.md](https://github.com/googlefonts/fontbakery/blob/master/docs/code-testing.md)

## Updating the distribution package

Releases to PyPI are performed by running the following commands (with the proper version number and date):

```sh
# cleanup
rm build/ -rf
rm dist/ -rf
rm venv/ -rf

# create a fresh python virtual env
virtualenv venv -ppython3
. venv/bin/activate

# Install tox and run our code tests
pip install tox
tox

# Register a git tag for this release and publish it
git tag -a v0.4.0 -m "Font Bakery version 0.4.0 (2018-May-16)"
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
