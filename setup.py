# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import glob
import os

# require libmagic
import ctypes
import ctypes.util
libmagic = None
# Let's try to find magic or magic1
dll = ctypes.util.find_library('magic') or ctypes.util.find_library('magic1')

# This is necessary because find_library returns None if it doesn't find the library
if dll:
    libmagic = ctypes.CDLL(dll)

if not libmagic or not libmagic._name:
    import sys
    platform_to_lib = {'darwin': ['/opt/local/lib/libmagic.dylib',
                                  '/usr/local/lib/libmagic.dylib'] +
                       # Assumes there will only be one version installed
                       glob.glob('/usr/local/Cellar/libmagic/*/lib/libmagic.dylib'),
                       'win32':  ['magic1.dll']}
    for dll in platform_to_lib.get(sys.platform, []):
        try:
            libmagic = ctypes.CDLL(dll)
            break
        except OSError:
            pass

msg = """Failed to find libmagic. Please install it, such as with
    brew install libmagic;
or
    apt-get install libmagic;
"""
if not libmagic or not libmagic._name:
    # It is better to raise an ImportError since we are importing magic module
    raise ImportError(msg)

# now installation can begin!
from setuptools import setup

def normalize_path(path, seperator='/'):
    """Normalise any path to be system independent"""
    return os.path.join(*path.split(seperator))

setup(
    name="fontbakery",
    version='0.3.1',
    url='https://github.com/googlefonts/fontbakery/',
    description='Font Bakery is a set of command-line tools'
                ' for testing font projects',
    author='Font Bakery Authors: Dave Crossland, Felipe Sanches, Lasse Fister, Marc Foley, Vitaly Volkov',
    author_email='dave@lab6.com',
    package_dir={'': 'Lib'},
    packages=['fontbakery',
              'fontbakery.reporters',
              'fontbakery.specifications',
              'fontbakery.testadapters',
              'fontbakery.commands'
              ],
    scripts=[normalize_path('bin/fontbakery'),
             normalize_path('bin/fontbakery-build-font2ttf.py'),
             normalize_path('bin/fontbakery-build-fontmetadata.py'),
             normalize_path('bin/fontbakery-check-font-version.py'),
             normalize_path('bin/fontbakery-check-noto-version.sh'),
             normalize_path('bin/fontbakery-check-googlefonts.py'),
             normalize_path('bin/fontbakery-dev-testrunner.py'),
             normalize_path('bin/fontbakery-family-html-snippet.py'),
             normalize_path('bin/fontbakery-fix-ascii-fontmetadata.py'),
             normalize_path('bin/fontbakery-fix-cmap.py'),
             normalize_path('bin/fontbakery-fix-familymetadata.py'),
             normalize_path('bin/fontbakery-fix-gasp.py'),
             normalize_path('bin/fontbakery-fix-glyph-private-encoding.py'),
             normalize_path('bin/fontbakery-fix-nameids.py'),
             normalize_path('bin/fontbakery-fix-nonhinting.py'),
             normalize_path('bin/fontbakery-fix-ttfautohint.py'),
             normalize_path('bin/fontbakery-list-panose.py'),
             normalize_path('bin/fontbakery-list-weightclass.py'),
             normalize_path('bin/fontbakery-list-widthclass.py'),
             normalize_path('bin/fontbakery-metadata-vs-api.py'),
             normalize_path('bin/fontbakery-update-families.py')],
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    data_files=[(normalize_path('data/test'),
                [normalize_path('data/test/README.txt')]),
                (normalize_path('data/test/cabin'),
                [normalize_path('data/test/cabin/Cabin-BoldItalic.ttf'),
                 normalize_path('data/test/cabin/Cabin-Bold.ttf'),
                 normalize_path('data/test/cabin/CabinCondensed-Bold.ttf'),
                 normalize_path('data/test/cabin/CabinCondensed-Medium.ttf'),
                 normalize_path('data/test/cabin/CabinCondensed-Regular.ttf'),
                 normalize_path('data/test/cabin/CabinCondensed-SemiBold.ttf'),
                 normalize_path('data/test/cabin/Cabin-Italic.ttf'),
                 normalize_path('data/test/cabin/Cabin-MediumItalic.ttf'),
                 normalize_path('data/test/cabin/Cabin-Medium.ttf'),
                 normalize_path('data/test/cabin/Cabin-Regular.ttf'),
                 normalize_path('data/test/cabin/Cabin-SemiBoldItalic.ttf'),
                 normalize_path('data/test/cabin/Cabin-SemiBold.ttf'),
                 normalize_path('data/test/cabin/DESCRIPTION.en_us.html'),
                 normalize_path('data/test/cabin/FONTLOG.txt'),
                 normalize_path('data/test/cabin/METADATA.pb'),
                 normalize_path('data/test/cabin/OFL.txt')]),
                (normalize_path('data/test/cousine'),
                [normalize_path('data/test/cousine/Cousine-Regular.ttf'),
                 normalize_path('data/test/cousine/Cousine-Bold.ttf'),
                 normalize_path('data/test/cousine/METADATA.pb'),
                 normalize_path('data/test/cousine/DESCRIPTION.en_us.html'),
                 normalize_path('data/test/cousine/LICENSE.txt')]),
                (normalize_path('data/test/familysans'),
                [normalize_path('data/test/familysans/FamilySans-BlackItalic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-Black.ttf'),
                 normalize_path('data/test/familysans/FamilySans-BoldItalic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-Bold.ttf'),
                 normalize_path('data/test/familysans/FamilySans-ExtraBoldItalic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-ExtraBold.ttf'),
                 normalize_path('data/test/familysans/FamilySans-ExtraLightItalic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-ExtraLight.ttf'),
                 normalize_path('data/test/familysans/FamilySans-Italic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-LightItalic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-Light.ttf'),
                 normalize_path('data/test/familysans/FamilySans-MediumItalic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-Medium.ttf'),
                 normalize_path('data/test/familysans/FamilySans-Regular.ttf'),
                 normalize_path('data/test/familysans/FamilySans-SemiBoldItalic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-SemiBold.ttf'),
                 normalize_path('data/test/familysans/FamilySans-ThinItalic.ttf'),
                 normalize_path('data/test/familysans/FamilySans-Thin.ttf')]),
                (normalize_path('data/test/mada'),
                [normalize_path('data/test/mada/Mada-Black.ttf'),
                 normalize_path('data/test/mada/Mada-Bold.ttf'),
                 normalize_path('data/test/mada/Mada-ExtraLight.ttf'),
                 normalize_path('data/test/mada/Mada-Light.ttf'),
                 normalize_path('data/test/mada/Mada-Medium.ttf'),
                 normalize_path('data/test/mada/Mada-Regular.ttf'),
                 normalize_path('data/test/mada/Mada-SemiBold.ttf'),
                 normalize_path('data/test/mada/OFL.txt'),
                 normalize_path('data/test/mada/README.txt')]),
                (normalize_path('data/test/merriweather'),
                [normalize_path('data/test/merriweather/DESCRIPTION.en_us.html'),
                 normalize_path('data/test/merriweather/FONTLOG.txt'),
                 normalize_path('data/test/merriweather/Merriweather-BlackItalic.ttf'),
                 normalize_path('data/test/merriweather/Merriweather-Black.ttf'),
                 normalize_path('data/test/merriweather/Merriweather-BoldItalic.ttf'),
                 normalize_path('data/test/merriweather/Merriweather-Bold.ttf'),
                 normalize_path('data/test/merriweather/Merriweather-Italic.ttf'),
                 normalize_path('data/test/merriweather/Merriweather-LightItalic.ttf'),
                 normalize_path('data/test/merriweather/Merriweather-Light.ttf'),
                 normalize_path('data/test/merriweather/Merriweather-Regular.ttf'),
                 normalize_path('data/test/merriweather/METADATA.pb'),
                 normalize_path('data/test/merriweather/OFL.txt')]),
                (normalize_path('data/test/montserrat'),
                [normalize_path('data/test/montserrat/DESCRIPTION.en_us.html'),
                 normalize_path('data/test/montserrat/METADATA.pb'),
                 normalize_path('data/test/montserrat/Montserrat-BlackItalic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-Black.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-BoldItalic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-Bold.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-ExtraBoldItalic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-ExtraBold.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-ExtraLightItalic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-ExtraLight.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-Italic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-LightItalic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-Light.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-MediumItalic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-Medium.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-Regular.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-SemiBoldItalic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-SemiBold.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-ThinItalic.ttf'),
                 normalize_path('data/test/montserrat/Montserrat-Thin.ttf'),
                 normalize_path('data/test/montserrat/OFL.txt')]),
                (normalize_path('data/test/nunito'),
                [normalize_path('data/test/nunito/DESCRIPTION.en_us.html'),
                 normalize_path('data/test/nunito/METADATA.pb'),
                 normalize_path('data/test/nunito/Nunito-BlackItalic.ttf'),
                 normalize_path('data/test/nunito/Nunito-Black.ttf'),
                 normalize_path('data/test/nunito/Nunito-BoldItalic.ttf'),
                 normalize_path('data/test/nunito/Nunito-Bold.ttf'),
                 normalize_path('data/test/nunito/Nunito-ExtraBoldItalic.ttf'),
                 normalize_path('data/test/nunito/Nunito-ExtraBold.ttf'),
                 normalize_path('data/test/nunito/Nunito-ExtraLightItalic.ttf'),
                 normalize_path('data/test/nunito/Nunito-ExtraLight.ttf'),
                 normalize_path('data/test/nunito/Nunito-Italic.ttf'),
                 normalize_path('data/test/nunito/Nunito-LightItalic.ttf'),
                 normalize_path('data/test/nunito/Nunito-Light.ttf'),
                 normalize_path('data/test/nunito/Nunito-Regular.ttf'),
                 normalize_path('data/test/nunito/Nunito-SemiBoldItalic.ttf'),
                 normalize_path('data/test/nunito/Nunito-SemiBold.ttf'),
                 normalize_path('data/test/nunito/OFL.txt')]),
                (normalize_path('data/test/regression/cabin'),
                [normalize_path('data/test/regression/cabin/Cabin-BoldItalic.ttf'),
                 normalize_path('data/test/regression/cabin/Cabin-Bold.ttf'),
                 normalize_path('data/test/regression/cabin/CabinCondensed-Bold.ttf'),
                 normalize_path('data/test/regression/cabin/CabinCondensed-Medium.ttf'),
                 normalize_path('data/test/regression/cabin/CabinCondensed-Regular.ttf'),
                 normalize_path('data/test/regression/cabin/CabinCondensed-SemiBold.ttf'),
                 normalize_path('data/test/regression/cabin/Cabin-Italic.ttf'),
                 normalize_path('data/test/regression/cabin/Cabin-MediumItalic.ttf'),
                 normalize_path('data/test/regression/cabin/Cabin-Medium.ttf'),
                 normalize_path('data/test/regression/cabin/Cabin-Regular.ttf'),
                 normalize_path('data/test/regression/cabin/Cabin-SemiBoldItalic.ttf'),
                 normalize_path('data/test/regression/cabin/Cabin-SemiBold.ttf'),
                 normalize_path('data/test/regression/cabin/DESCRIPTION.en_us.html'),
                 normalize_path('data/test/regression/cabin/FONTLOG.txt'),
                 normalize_path('data/test/regression/cabin/METADATA.pb'),
                 normalize_path('data/test/regression/cabin/OFL.txt')]),
                (normalize_path('data/test/028/multiple'),
                [normalize_path('data/test/028/multiple/LICENSE.txt'),
                 normalize_path('data/test/028/multiple/OFL.txt')]),
                (normalize_path('data/test/028/none'),
                [normalize_path('data/test/028/none/NoLicenseHere.txt')]),
                (normalize_path('data/test/028/pass_apache'),
                [normalize_path('data/test/028/pass_apache/LICENSE.txt')]),
                (normalize_path('data/test/028/pass_ofl'),
                [normalize_path('data/test/028/pass_ofl/OFL.txt')])],
    install_requires=[
        'lxml',
        'requests',
        'pyyaml',
        'html5lib',
        'python-magic',
        'markdown',
        'scrapy',
        'urwid',
        'GitPython==0.3.2.RC1',
        'defusedxml',
        'unidecode',
        'tabulate',
        'pyasn1',
        'protobuf',
        'flake8',
        'coveralls'
    ]
)


# check for ttfautohint
found_ttfautohint = False
for p in os.environ.get('PATH').split(':'):
    if os.path.exists(os.path.join(p, 'ttfautohint')):
        found_ttfautohint = True

if not found_ttfautohint:
    print ('WARNING: Command line tool `ttfautohint` is recommended. Install it with'
           ' `apt-get install ttfautohint` or `brew install ttfautohint`')
