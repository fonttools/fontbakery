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
    version='0.2.1',
    url='https://github.com/googlefonts/fontbakery/',
    description='Font Bakery is a set of command-line tools'
                ' for testing font projects',
    author='Font Bakery Authors: Dave Crossland, Felipe Sanches, Lasse Fister, Marc Foley, Vitaly Volkov',
    author_email='googlefonts-discuss@googlegroups.com',
    package_dir={'': 'Lib'},
    packages=['fontbakery'],
    scripts=['bin/fontbakery',
             'bin/fontbakery-check-collection.sh',
             'bin/fontbakery-build-contributors.py',
             'bin/fontbakery-build-font2ttf.py',
             'bin/fontbakery-build-fontmetadata.py',
             'bin/fontbakery-build-ofl.py',
             'bin/fontbakery-check-bbox.py',
             'bin/fontbakery-check-description.py',
             'bin/fontbakery-check-gf-github.py',
             'bin/fontbakery-check-name.py',
             'bin/fontbakery-check-ttf.py',
             'bin/fontbakery-check-upstream.py',
             'bin/fontbakery-check-vtt-compatibility.py',
             'bin/fontbakery-fix-ascii-fontmetadata.py',
             'bin/fontbakery-fix-cmap.py',
             'bin/fontbakery-fix-dsig.py',
             'bin/fontbakery-fix-familymetadata.py',
             'bin/fontbakery-fix-fsselection.py',
             'bin/fontbakery-fix-fstype.py',
             'bin/fontbakery-fix-gasp.py',
             'bin/fontbakery-fix-glyph-private-encoding.py',
             'bin/fontbakery-fix-glyphs.py',
             'bin/fontbakery-fix-nameids.py',
             'bin/fontbakery-fix-nonhinting.py',
             'bin/fontbakery-fix-ttfautohint.py',
             'bin/fontbakery-fix-vendorid.py',
             'bin/fontbakery-fix-vertical-metrics.py',
             'bin/fontbakery-list-panose.py',
             # 'bin/fontbakery-list-variable-source.py', # Not included in the 0.2.1 release.
                                                         # See https://github.com/googlefonts/fontbakery/issues/1414
             'bin/fontbakery-list-weightclass.py',
             'bin/fontbakery-list-widthclass.py',
             'bin/fontbakery-metadata-vs-api.py',
             'bin/fontbakery-nametable-from-filename.py',
             'bin/fontbakery-update-families.py',
             'bin/fontbakery-update-nameids.py',
             'bin/fontbakery-update-version.py'],
             'bin/fontbakery-dev-testrunner.py',
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
    data_files=[('data/test/cousine/',
                ['data/test/cousine/Cousine-Regular.ttf',
                 'data/test/cousine/Cousine-Bold.ttf',
                 'data/test/cousine/METADATA.pb',
                 'data/test/cousine/DESCRIPTION.en_us.html',
                 'data/test/cousine/LICENSE.txt']),
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
                 'data/test/merriweather/OFL.txt'])],
    install_requires=[
        'lxml',
        'requests',
        'pyyaml',
        'robofab',
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
