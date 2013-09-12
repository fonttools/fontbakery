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

def project_upstream_tests(project):
    import checker.upstream_runner
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    result = {}
    os.chdir(_in)
    for font in project.config['local']['ufo_dirs']:
        result[font] = checker.upstream_runner.run_set(os.path.join(_in, font))
    return result

def project_result_tests(project):
    import checker.result_runner
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    result = {}
    os.chdir(_out_src)
    for font in glob.glob("*.ttf"):
        result[font] = checker.result_runner.run_set(os.path.join(_out_src, font))
    return result
    
def project_fontaine(project):
    from fontaine.font import Font
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    fontaineFonts = {}
    os.chdir(_out_src)
    for font in glob.glob("*.ttf"):
#        import ipdb; ipdb.set_trace()
        fontaineFont = Font(os.path.join(_out_src, font))
        fontaineFonts[font] = fontaineFont
#        for fontfilename, aFontaineFont in fontaineFonts.iteritems():
#           fontaineFonts[font][o[0].common_name] = o[0].glyphs
#    for n, f in fontaineFonts.iteritems():
#        for o in Font.get_orthographies(f):
#            print(o)
    return fontaineFonts