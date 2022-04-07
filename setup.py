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
              'fontbakery.profiles',
              'fontbakery.commands',
              'fontbakery.sphinx_extensions'
              ],
    package_data={'fontbakery': ['data/*.cache']},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
    python_requires='>=3.7',
    setup_requires=['setuptools_scm'],
    install_requires=[
        'axisregistry',
        'beautifulsoup4',
        'beziers',
        'cmarkgfm',
        'collidoscope>=0.4.1', # 0.4.0 had a bug that failed to detect
                               # an ïï collision on Nunito Black.
                               # (see https://github.com/googlefonts/fontbakery/issues/3554)
        'defcon',
        'dehinter>=3.1.0', # 3.1.0 added dehinter.font.hint function
        'fontTools[ufo,lxml,unicode]>=3.34',  # 3.34 fixed some CFF2 issues, including calcBounds
        'font-v',
        'gflanguages>=0.3.0', # there was an api simplification/update on v0.3.0 (see https://github.com/googlefonts/gflanguages/pull/7)
        'glyphsets',
        'lxml',
        'opentype-sanitizer>=7.1.9',  # 7.1.9 fixes caret value format = 3 bug
                                      # (see https://github.com/khaledhosny/ots/pull/182)
        'opentypespec',
        'pip-api',
        'protobuf>=3.7.0',  # 3.7.0 fixed a bug on parsing some METADATA.pb files
                            # (see https://github.com/googlefonts/fontbakery/issues/2200)
        'PyYAML',
        'requests',
        'rich',
        'stringbrewer',
        'toml',
        'ufolint',
        'ufo2ft>=2.25.2',  # 2.25.2 updated the script lists for Unicode 14.0
        'unicodedata2',
        'vharfbuzz',
    ],
    extras_require={
        'docs': [
            'recommonmark',
            'sphinx >= 1.4',
            'sphinx_rtd_theme',
        ],
    },
    entry_points={
        'console_scripts': ['fontbakery=fontbakery.cli:main'],
    },
# TODO: review this and make it cross-platform:
#    data_files=[
#        ('/etc/bash_completion.d', ['snippets/fontbakery.bash-completion']),
#    ]
)
