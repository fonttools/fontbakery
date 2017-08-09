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
setup(
    name="fontbakery",
    version='0.3.1-RC1',
    url='https://github.com/googlefonts/fontbakery/',
    description='Font Bakery is a set of command-line tools'
                ' for testing font projects',
    author='Font Bakery Authors: Dave Crossland, Felipe Sanches, Lasse Fister, Marc Foley, Vitaly Volkov',
    author_email='dave@lab6.com',
    package_dir={'': 'Lib'},
    packages=['fontbakery',
              'fontbakery.reporters',
              'fontbakery.specifications',
              'fontbakery.testadapters'],
    scripts=['bin/fontbakery',
             'bin/fontbakery-build-font2ttf.py',
             'bin/fontbakery-build-fontmetadata.py',
             'bin/fontbakery-family-html-snippet.py',
             'bin/fontbakery-fix-ascii-fontmetadata.py',
             'bin/fontbakery-fix-familymetadata.py',
             'bin/fontbakery-fix-gasp.py',
             'bin/fontbakery-fix-glyph-private-encoding.py',
             'bin/fontbakery-fix-nameids.py',
             'bin/fontbakery-fix-nonhinting.py',
             'bin/fontbakery-fix-ttfautohint.py',
             'bin/fontbakery-list-panose.py',
             'bin/fontbakery-list-weightclass.py',
             'bin/fontbakery-list-widthclass.py',
             'bin/fontbakery-metadata-vs-api.py',
             'bin/fontbakery-dev-testrunner.py',
             'bin/fontbakery-check-googlefonts.py',
             'bin/fontbakery-update-families.py'],
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    data_files=[('data/test/',
                ['data/test/README.txt']),
                ('data/test/cabin/',
                ['data/test/cabin/Cabin-BoldItalic.ttf',
                 'data/test/cabin/Cabin-Bold.ttf',
                 'data/test/cabin/CabinCondensed-Bold.ttf',
                 'data/test/cabin/CabinCondensed-Medium.ttf',
                 'data/test/cabin/CabinCondensed-Regular.ttf',
                 'data/test/cabin/CabinCondensed-SemiBold.ttf',
                 'data/test/cabin/Cabin-Italic.ttf',
                 'data/test/cabin/Cabin-MediumItalic.ttf',
                 'data/test/cabin/Cabin-Medium.ttf',
                 'data/test/cabin/Cabin-Regular.ttf',
                 'data/test/cabin/Cabin-SemiBoldItalic.ttf',
                 'data/test/cabin/Cabin-SemiBold.ttf',
                 'data/test/cabin/DESCRIPTION.en_us.html',
                 'data/test/cabin/FONTLOG.txt',
                 'data/test/cabin/METADATA.pb',
                 'data/test/cabin/OFL.txt']),
                ('data/test/cousine/',
                ['data/test/cousine/Cousine-Regular.ttf',
                 'data/test/cousine/Cousine-Bold.ttf',
                 'data/test/cousine/METADATA.pb',
                 'data/test/cousine/DESCRIPTION.en_us.html',
                 'data/test/cousine/LICENSE.txt']),
                ('data/test/familysans/',
                ['data/test/familysans/FamilySans-BlackItalic.ttf',
                 'data/test/familysans/FamilySans-Black.ttf',
                 'data/test/familysans/FamilySans-BoldItalic.ttf',
                 'data/test/familysans/FamilySans-Bold.ttf',
                 'data/test/familysans/FamilySans-ExtraBoldItalic.ttf',
                 'data/test/familysans/FamilySans-ExtraBold.ttf',
                 'data/test/familysans/FamilySans-ExtraLightItalic.ttf',
                 'data/test/familysans/FamilySans-ExtraLight.ttf',
                 'data/test/familysans/FamilySans-Italic.ttf',
                 'data/test/familysans/FamilySans-LightItalic.ttf',
                 'data/test/familysans/FamilySans-Light.ttf',
                 'data/test/familysans/FamilySans-MediumItalic.ttf',
                 'data/test/familysans/FamilySans-Medium.ttf',
                 'data/test/familysans/FamilySans-Regular.ttf',
                 'data/test/familysans/FamilySans-SemiBoldItalic.ttf',
                 'data/test/familysans/FamilySans-SemiBold.ttf',
                 'data/test/familysans/FamilySans-ThinItalic.ttf',
                 'data/test/familysans/FamilySans-Thin.ttf']),
                ('data/test/mada/',
                ['data/test/mada/Mada-Black.ttf',
                 'data/test/mada/Mada-Bold.ttf',
                 'data/test/mada/Mada-ExtraLight.ttf',
                 'data/test/mada/Mada-Light.ttf',
                 'data/test/mada/Mada-Medium.ttf',
                 'data/test/mada/Mada-Regular.ttf',
                 'data/test/mada/Mada-SemiBold.ttf',
                 'data/test/mada/OFL.txt',
                 'data/test/mada/README.txt']),
                ('data/test/merriweather/',
                ['data/test/merriweather/DESCRIPTION.en_us.html',
                 'data/test/merriweather/FONTLOG.txt',
                 'data/test/merriweather/Merriweather-BlackItalic.ttf',
                 'data/test/merriweather/Merriweather-Black.ttf',
                 'data/test/merriweather/Merriweather-BoldItalic.ttf',
                 'data/test/merriweather/Merriweather-Bold.ttf',
                 'data/test/merriweather/Merriweather-Italic.ttf',
                 'data/test/merriweather/Merriweather-LightItalic.ttf',
                 'data/test/merriweather/Merriweather-Light.ttf',
                 'data/test/merriweather/Merriweather-Regular.ttf',
                 'data/test/merriweather/METADATA.pb',
                 'data/test/merriweather/OFL.txt']),
                ('data/test/montserrat/',
                ['data/test/montserrat/DESCRIPTION.en_us.html',
                 'data/test/montserrat/METADATA.pb',
                 'data/test/montserrat/Montserrat-BlackItalic.ttf',
                 'data/test/montserrat/Montserrat-Black.ttf',
                 'data/test/montserrat/Montserrat-BoldItalic.ttf',
                 'data/test/montserrat/Montserrat-Bold.ttf',
                 'data/test/montserrat/Montserrat-ExtraBoldItalic.ttf',
                 'data/test/montserrat/Montserrat-ExtraBold.ttf',
                 'data/test/montserrat/Montserrat-ExtraLightItalic.ttf',
                 'data/test/montserrat/Montserrat-ExtraLight.ttf',
                 'data/test/montserrat/Montserrat-Italic.ttf',
                 'data/test/montserrat/Montserrat-LightItalic.ttf',
                 'data/test/montserrat/Montserrat-Light.ttf',
                 'data/test/montserrat/Montserrat-MediumItalic.ttf',
                 'data/test/montserrat/Montserrat-Medium.ttf',
                 'data/test/montserrat/Montserrat-Regular.ttf',
                 'data/test/montserrat/Montserrat-SemiBoldItalic.ttf',
                 'data/test/montserrat/Montserrat-SemiBold.ttf',
                 'data/test/montserrat/Montserrat-ThinItalic.ttf',
                 'data/test/montserrat/Montserrat-Thin.ttf',
                 'data/test/montserrat/OFL.txt']),
                ('data/test/nunito/',
                ['data/test/nunito/DESCRIPTION.en_us.html',
                 'data/test/nunito/METADATA.pb',
                 'data/test/nunito/Nunito-BlackItalic.ttf',
                 'data/test/nunito/Nunito-Black.ttf',
                 'data/test/nunito/Nunito-BoldItalic.ttf',
                 'data/test/nunito/Nunito-Bold.ttf',
                 'data/test/nunito/Nunito-ExtraBoldItalic.ttf',
                 'data/test/nunito/Nunito-ExtraBold.ttf',
                 'data/test/nunito/Nunito-ExtraLightItalic.ttf',
                 'data/test/nunito/Nunito-ExtraLight.ttf',
                 'data/test/nunito/Nunito-Italic.ttf',
                 'data/test/nunito/Nunito-LightItalic.ttf',
                 'data/test/nunito/Nunito-Light.ttf',
                 'data/test/nunito/Nunito-Regular.ttf',
                 'data/test/nunito/Nunito-SemiBoldItalic.ttf',
                 'data/test/nunito/Nunito-SemiBold.ttf',
                 'data/test/nunito/OFL.txt']),
                ('data/test/regression/cabin/',
                ['data/test/regression/cabin/Cabin-BoldItalic.ttf',
                 'data/test/regression/cabin/Cabin-Bold.ttf',
                 'data/test/regression/cabin/CabinCondensed-Bold.ttf',
                 'data/test/regression/cabin/CabinCondensed-Medium.ttf',
                 'data/test/regression/cabin/CabinCondensed-Regular.ttf',
                 'data/test/regression/cabin/CabinCondensed-SemiBold.ttf',
                 'data/test/regression/cabin/Cabin-Italic.ttf',
                 'data/test/regression/cabin/Cabin-MediumItalic.ttf',
                 'data/test/regression/cabin/Cabin-Medium.ttf',
                 'data/test/regression/cabin/Cabin-Regular.ttf',
                 'data/test/regression/cabin/Cabin-SemiBoldItalic.ttf',
                 'data/test/regression/cabin/Cabin-SemiBold.ttf',
                 'data/test/regression/cabin/DESCRIPTION.en_us.html',
                 'data/test/regression/cabin/FONTLOG.txt',
                 'data/test/regression/cabin/METADATA.pb',
                 'data/test/regression/cabin/OFL.txt']),
                ('data/test/028/multiple/',
                ['data/test/028/multiple/LICENSE.txt',
                 'data/test/028/multiple/OFL.txt']),
                ('data/test/028/none/',
                ['data/test/028/none/NoLicenseHere.txt']),
                ('data/test/028/pass_apache',
                ['data/test/028/pass_apache/LICENSE.txt']),
                ('data/test/028/pass_ofl',
                ['data/test/028/pass_ofl/OFL.txt'])],
    install_requires=[
        'lxml',
        'requests',
        'pyyaml',
        'fontaine',
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
