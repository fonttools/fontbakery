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
from setuptools import setup

def normalize_path(path, seperator='/'):
    """Normalise any path to be system independent"""
    return os.path.join(*path.split(seperator))

def fontbakery_scripts():
  scripts = [os.path.join('bin', f) for f in os.listdir('bin') if f.startswith('fontbakery-')]
  scripts.append(os.path.join('bin', 'fontbakery'))
  return scripts

setup(
    name="fontbakery",
    version='0.3.2-git',
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
    scripts=fontbakery_scripts(),
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
        'defusedxml',
        'requests',
        'unidecode',
        'protobuf',
        'bs4',
        'fontTools'
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
