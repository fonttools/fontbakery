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

from setuptools import setup

try:
    readme = open('README.md').read()
except IOError:
    readme = ''


FONTTOOLS_VERSION = '>=4.39.0'  # Python 3.8+ required
UFO2FT_VERSION = '>=2.25.2'

# Profile-specific dependencies:
ufo_sources_extras = [
    'defcon',
    f'fontTools[ufo]{FONTTOOLS_VERSION}',
    f'ufo2ft{UFO2FT_VERSION}',
    'ufolint',
]

googlefonts_extras = [
    'axisregistry>=0.3.0',
    'beautifulsoup4',  # For parsing registered vendor IDs from Microsoft's webpage
    'dehinter>=3.1.0',  # 3.1.0 added dehinter.font.hint function
    'font-v',
    f'fontTools[lxml,unicode]{FONTTOOLS_VERSION}',
    'gflanguages>=0.3.0',  # There was an api simplification/update on v0.3.0
                           # (see https://github.com/googlefonts/gflanguages/pull/7)
    'glyphsets>=0.5.0',
    'protobuf>=3.7.0, <4',  # 3.7.0 fixed a bug on parsing some METADATA.pb files.
                            # We cannot use v4 because our protobuf files have been compiled with v3.
                            # (see https://github.com/googlefonts/fontbakery/issues/2200)
] + ufo_sources_extras

fontval_extras = [
    'lxml',
]

docs_extras = [
    'recommonmark',
    'sphinx >= 1.4',
    'sphinx_rtd_theme',
]

all_extras = set(
    docs_extras
    + googlefonts_extras
    + fontval_extras
    + ufo_sources_extras
)

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
    package_data={'fontbakery': ['data/*.cache',
                                 'data/googlefonts/*_exceptions.txt']},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    python_requires='>=3.8',
    setup_requires=[
        'setuptools>=61.2',
        'setuptools_scm[toml]>=6.2',
    ],
    install_requires=[
        # --- core dependencies
        f'fontTools{FONTTOOLS_VERSION}',
        'freetype-py!=2.4.0',  # Avoiding 2.4.0 due to seg-fault described at
                               # https://github.com/googlefonts/fontbakery/issues/4143
        'munkres',  # For interpolation compatibility checking (fontTools dependency)
        'opentypespec',
        'opentype-sanitizer>=7.1.9',  # 7.1.9 fixes caret value format = 3 bug
                                      # (see https://github.com/khaledhosny/ots/pull/182)

        # --- for parsing Configuration files
        'PyYAML',
        'toml',

        # --- used by Reporters
        'cmarkgfm',
        'rich',

        # --- for checking Font Bakery's version
        'packaging',  # Universal profile
        'pip-api',    # Universal profile
        'requests',   # Universal & googlefonts profiles


        # TODO: Try to split the packages below into feature-specific extras.
        'beziers>=0.5.0',  # Opentype, iso15008, Shaping (& Universal) profiles
                           # Uses new fontTools glyph outline access
        'collidoscope>=0.5.2',  # Shaping (& Universal) profiles
                                # 0.5.1 did not yet support python 3.11
                                # (see https://github.com/googlefonts/fontbakery/issues/3970)
        'stringbrewer',  # Shaping (& Universal) profiles
        f'ufo2ft{UFO2FT_VERSION}',  # Shaping
                           # 2.25.2 updated the script lists for Unicode 14.0
        'vharfbuzz>=0.2.0',  # Googlefonts, Shaping (& Universal) profiles
                             # v0.2.0 had an API update
    ],
    extras_require={
        'all': all_extras,
        'docs': docs_extras,
        'googlefonts': googlefonts_extras,
        'fontval': fontval_extras,
        'ufo-sources': ufo_sources_extras,
    },
    entry_points={
        'console_scripts': ['fontbakery=fontbakery.cli:main'],
    },
# TODO: review this and make it cross-platform:
#    data_files=[
#        ('/etc/bash_completion.d', ['snippets/fontbakery.bash-completion']),
#    ]
)
