# Copyright 2017 The Font Bakery Authors. All Rights Reserved.
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
import os
from setuptools import setup

try:
  readme = open('README.md').read()
except IOError:
  readme = ''

setup(
    name="fontbakery",
    use_scm_version={"write_to": "Lib/fontbakery/_version.py"},
    url='https://github.com/googlefonts/fontbakery/',
    description='Well designed Font QA tool, written in Python 3',
    long_description=readme,
    long_description_content_type='text/markdown',
    author=('Font Bakery authors and contributors:'
            ' Dave Crossland,'
            ' Felipe Sanches,'
            ' Lasse Fister,'
            ' Marc Foley,'
            ' Nikolaus Waxweiler,'
            ' Chris Simpkins,'
            ' Jens Kutilek,'
            ' Vitaly Volkov'),
    author_email='dave@lab6.com',
    package_dir={'': 'Lib'},
    packages=['fontbakery',
              'fontbakery.reporters',
              'fontbakery.specifications',
              'fontbakery.commands'
              ],
    package_data={'fontbakery': ['data/*.cache']},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    python_requires='>=3.6',
    setup_requires=['setuptools_scm'],
    install_requires=[
        'beautifulsoup4',
        'defcon',
        'defusedxml',
        'font-v',
        'fontTools[ufo,lxml]>=3.34',  # 3.34 fixed some CFF2 issues, including calcBounds
        'lxml',
        'opentype-sanitizer',
        'protobuf',
        'requests',
        'ttfautohint-py',
        'ufolint',
        'Unidecode'
    ],
    extras_require={
        'docs': [
            'sphinx >= 1.4',
            'sphinx_rtd_theme',
            'recommonmark',
        ]
    },
    entry_points={
        'console_scripts': ['fontbakery=fontbakery.cli:main'],
    }
)
