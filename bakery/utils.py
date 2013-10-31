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
from __future__ import print_function

from datetime import datetime
import os
import glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
DATA_ROOT = os.path.join(ROOT, 'data')

def get_current_time():
    return datetime.utcnow()

def pretty_date(dt, default=None):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    Ref: https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
    """

    if default is None:
        default = 'just now'

    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, 'year', 'years'),
        (diff.days / 30, 'month', 'months'),
        (diff.days / 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
        (diff.seconds / 3600, 'hour', 'hours'),
        (diff.seconds / 60, 'minute', 'minutes'),
        (diff.seconds, 'second', 'seconds'),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if period == 1:
            return u'%d %s ago' % (period, singular)
        else:
            return u'%d %s ago' % (period, plural)

    return default

from flask import current_app
import itsdangerous

def signify(text):
    signer = itsdangerous.Signer(current_app.secret_key)
    return signer.sign(text)


class RedisFd(object):
    """Redis File Descriptor class, publish writen data to redis channel in parallel to file"""
    def __init__(self, name, mode = 'a'):
        self.fd = open(name, mode)
        self.fd.write("Start: Start of log\n") #end of log

    def write(self, data, prefix = ''):
        self.fd.write("%s%s" % (prefix, data))
        self.fd.flush()

    def close(self):
        self.fd.write("End: End of log\n") #end of log
        self.fd.close()


def project_fontaine(project, build):
    from fontaine.font import Font

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)

    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    # Its very likely that _out exists, but just in case:
    if os.path.exists(_out):
        os.chdir(_out)
    else:
        # This is very unlikely, but should it happen, just return
        return

    # Run pyFontaine on all the TTF fonts
    fonts = {}
    for filename in glob.glob("*.ttf"):
        fontaine = Font(filename)
        fonts[filename] = fontaine

    # Make a plain dictionary, unlike the fancy data structures used by pyFontaine :)
    family = {}
    for fontfilename, fontaine in fonts.iteritems():
        # Use the font file name as a key to a dictionary of char sets
        family[fontfilename] = {}
        for charset, coverage, percentcomplete, missingchars in fontaine.get_orthographies():
            # Use each char set name as a key to a dictionary of this font's coverage details
            charsetname = charset.common_name
            family[fontfilename][charsetname] = {}
            family[fontfilename][charsetname]['coverage'] = coverage # unsupport, fragmentary, partial, full
            family[fontfilename][charsetname]['percentcomplete'] = percentcomplete # int
            family[fontfilename][charsetname]['missingchars'] = missingchars # list of ord numbers
            # Use the char set name as a key to a list of the family's average coverage
            if not family.has_key(charsetname):
                family[charsetname] = []
            # Append the char set percentage of each font file to the list
            family[charsetname].append(percentcomplete) # [10, 32, 40, 40] etc
            # And finally, if the list now has all the font files, make it the mean average percentage
            if len(family[charsetname]) == len(fonts.items()):
                family[charsetname] = sum(family[charsetname]) / len(fonts.items())
    # Make a plain dictionary with just the bits we want on the dashboard
    totals = {}
    totals['gwf'] = family[u'GWF latin']
    totals['al3'] = family[u'Adobe Latin 3']
    # Store it in the $(id).state.yaml file
    project.config['local']['charsets'] = totals
    project.save_state()

    # fonts.itervalues() emits <fontaine.font.Font instance at 0x106123c68> objects that we return for the rfiles.html template
    return fonts.itervalues()
