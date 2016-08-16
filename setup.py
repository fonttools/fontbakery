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
    version='git-0.1.0',
    url='https://github.com/googlefonts/fontbakery/',
    description='Font Bakery is a set of command-line tools'
                ' for testing font projects',
    author='Font Bakery Authors',
    author_email='dave@lab6.com',
    scripts=['fontbakery-build-font2ttf.py',
             'fontbakery-build-fontmetadata.py',
#             'fontbakery-build-metadata.py',
             'fontbakery-check-description.py',
             'fontbakery-check-ttf.py',
             'fontbakery-check-upstream.py',
             'fontbakery-crawl.py',
             'fontbakery-fix-ascii-fontmetadata.py',
             'fontbakery-fix-familymetadata.py',
             'fontbakery-fix-gasp.py',
             'fontbakery-fix-glyph-private-encoding.py',
             'fontbakery-fix-nameids.py',
             'fontbakery-fix-nonhinting.py',
             'fontbakery-fix-ttfautohint.py',
             'fontbakery-list-panose.py',
             'fontbakery-list-weightclass.py',
             'fontbakery-list-widthclass.py',
             'fontbakery-metadata-vs-api.py',
             'fontbakery-stats-deva-per-day.py',
#             'fontbakery-travis-deploy.py',
#             'fontbakery-travis-init.py',
#             'fontbakery-travis-secure.sh',
             'fontbakery-update-families.py',
             'fonts_public_pb2.py'],
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
                 'data/test/cousine/LICENSE.txt'])],
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
