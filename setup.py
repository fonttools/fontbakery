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
    version='0.0.14',
    url='https://github.com/googlefonts/fontbakery/',
    description='Font Bakery is a set of command-line tools for building'
                ' and testing font projects',
    author='Font Bakery Authors',
    author_email='dave@lab6.com',
    packages=["bakery_cli",
              "bakery_cli.pipe",
              "bakery_cli.scripts",
              "bakery_lint",
              "bakery_lint.fonttests",
              "bakery_cli.report"],
    scripts=['tools/collection-management/fontbakery-travis-secure.sh',
             'tools/fontbakery-build-font2ttf.py',
             'tools/fontbakery-build-metadata.py',
             'tools/fontbakery-build.py',
             'tools/fontbakery-check-description.py',
             'tools/fontbakery-check-metadata.py',
             'tools/fontbakery-check-otf.py',
             'tools/fontbakery-check-ttf.py',
             'tools/fontbakery-check-ufo.py',
             'tools/fontbakery-check-upstream.py',
             'tools/fontbakery-crawl.py',
             'tools/fontbakery-fix-ascii-fontmetadata.py',
             'tools/fontbakery-fix-designer.py',
             'tools/fontbakery-fix-dsig.py',
             'tools/fontbakery-fix-familymetadata.py',
             'tools/fontbakery-fix-fsselection.py',
             'tools/fontbakery-fix-fstype.py',
             'tools/fontbakery-fix-gasp.py',
             'tools/fontbakery-fix-glyph-private-encoding.py',
             'tools/fontbakery-fix-italic.py',
             'tools/fontbakery-fix-italicangle.py',
             'tools/fontbakery-fix-macstyle.py',
             'tools/fontbakery-fix-nameids.py',
             'tools/fontbakery-fix-nbsp.py',
             'tools/fontbakery-fix-opentype-names.py',
             'tools/fontbakery-fix-panose.py',
             'tools/fontbakery-fix-version.py',
             'tools/fontbakery-fix-vertical-metrics.py',
             'tools/fontbakery-fix-weightclass.py',
             'tools/fontbakery-fix-widthclass.py',
             'tools/fontbakery-kern.py',
             'tools/fontbakery-metadata-vs-api.py',
             'tools/fontbakery-remove-platformid1.py',
             'tools/fontbakery-report.py',
             'tools/fontbakery-setup.py',
             'tools/fontbakery-stats-deva-per-day.py',
             'tools/fontbakery-travis-deploy.py',
             'tools/fontbakery-travis-init.py'],
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    data_files=[('Data', ['Data/APACHE.url',
                          'Data/APACHE.license',
                          'Data/APACHE.placeholder',
                          'Data/OFL.url',
                          'Data/OFL.license',
                          'Data/OFL.placeholder'])],
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
        'protobuf'
    ],
    setup_requires=['nose', 'mock', 'coverage'],
    test_suite='nose.collector'
)


# check for ttfautohint
found_ttfautohint = False
for p in os.environ.get('PATH').split(':'):
    if os.path.exists(os.path.join(p, 'ttfautohint')):
        found_ttfautohint = True

if not found_ttfautohint:
    print ('WARNING: Command line tool `ttfautohint` is recommended. Install it with'
           ' `apt-get install ttfautohint` or `brew install ttfautohint`')

# check for python fontforge module
try:
    import fontforge
except ImportError:
    print('WARNING: Python module `fontforge` is recommended. Install it with'
          ' `apt-get install python-fontforge`'
          ' or `brew install python; brew install fontforge --HEAD`')
