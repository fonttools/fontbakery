#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
from __future__ import print_function

import os
import re
import sys
import yaml

from fontaine.font import FontFactory
from fontaine.cmap import Library

from bakery_cli.system import prun
from bakery_cli.utils import UpstreamDirectory


class Widgets(object):

    def __init__(self, app):
        self.app = app
        self.commit = urwid.Edit(edit_text=app.commit)
        self.ttfautohint = urwid.Edit(edit_text=app.ttfautohint)
        self.newfamily = urwid.Edit(edit_text=app.newfamily)
        self.pyftsubset = urwid.Edit(edit_text=app.pyftsubset)
        self.notes = urwid.Edit(edit_text=app.notes)
        self.afdko_parameters = urwid.Edit(edit_text=app.afdko)

        self.compiler = []
        self.licenses = []
        self.process_files = []
        self.subset = []

    def on_checkbox_state_change(self, widget, state, user_data):
        self.app.config[user_data['name']] = state

    def create_checkbox(self, title, name, state=False):
        return urwid.CheckBox(title, user_data={'name': name}, state=state,
                              on_state_change=self.on_checkbox_state_change)

    def create_process_file(self, filepath):
        try:
            state = self.app.process_files.index(filepath) >= 0
        except ValueError:
            state = False

        widget = urwid.CheckBox(filepath, state=state)
        self.process_files.append(widget)
        return widget

    def create_subset_widget(self, subsetname, coverage):
        widget = urwid.CheckBox('{0} ({1})'.format(subsetname, coverage),
                                state=bool(subsetname in app.subset),
                                user_data={'name': subsetname})
        self.subset.append(widget)
        return widget


class App(object):

    commit = 'HEAD'
    process_files = []
    subset = []
    compiler = 'fontforge'
    ttfautohint = '-l 7 -r 28 -G 50 -x 13 -w "G"'
    afdko = ''
    downstream = True
    optimize = True
    license = ''
    pyftsubset = '--notdef-outline --name-IDs=* --hinting'
    notes = ''
    newfamily = ''
    fontcrunch = False
    config = {}
    configfile = 'bakery.yaml'

    def __init__(self):

        if os.path.exists('bakery.yaml'):
            self.configfile = 'bakery.yaml'
            self.config = yaml.load(open('bakery.yaml'))
        elif os.path.exists('bakery.yml'):
            self.config = yaml.load(open('bakery.yml'))
            self.configfile = 'bakery.yml'

        self.commit = self.config.get('commit', 'HEAD')
        self.process_files = self.config.get('process_files', [])
        self.subset = self.config.get('subset', [])
        self.compiler = self.config.get('compiler', 'fontforge')
        self.ttfautohint = self.config.get('ttfautohint', '-l 7 -r 28 -G 50 -x 13 -w "G"')
        self.afdko = self.config.get('afdko', '')

        self.license = self.config.get('license', '')
        self.pyftsubset = self.config.get('pyftsubset',
                                     '--notdef-outline --name-IDs=* --hinting')
        self.notes = self.config.get('notes', '')
        self.newfamily = self.config.get('newfamily', '')

        self.widgets = Widgets(self)

    def save(self, *args, **kwargs):
        if os.path.exists(self.configfile):
            print('{} exists...'.format(self.configfile))

            self.configfile = '{}.new'.format(self.configfile)
            while os.path.exists('{}.new'.format(self.configfile)):
                self.configfile = '{}.new'.format(self.configfile)

        self.config['commit'] = self.widgets.commit.get_edit_text()
        if not self.config['commit']:
            del self.config['commit']

        self.config['ttfautohint'] = self.widgets.ttfautohint.get_edit_text()
        self.config['newfamily'] = self.widgets.newfamily.get_edit_text()
        if not self.config['newfamily']:
            del self.config['newfamily']

        self.config['pyftsubset'] = self.widgets.pyftsubset.get_edit_text()

        self.config['process_files'] = [w.get_label()
                                        for w in self.widgets.process_files
                                        if w.get_state()]

        self.config['compiler'] = ', '.join([w.get_label()
                                             for w in self.widgets.compiler
                                             if w.get_state()])

        self.config['license'] = ', '.join([w.get_label()
                                            for w in self.widgets.licenses
                                            if w.get_state()])

        self.config['notes'] = self.widgets.notes.get_edit_text()
        if not self.config['notes']:
            del self.config['notes']

        regex = re.compile(r'\s*\(\d+%\)')
        self.config['subset'] = [regex.sub('', w.get_label())
                                 for w in self.widgets.subset
                                 if w.get_state()]

        self.config['afdko'] = self.widgets.afdko_parameters.get_edit_text()
        if not self.config['afdko']:
            del self.config['afdko']

        yaml.safe_dump(self.config, open(self.configfile, 'w'))
        print('Wrote {}'.format(self.configfile))
        sys.exit(0)


def get_subsets_coverage_data(source_fonts_paths):
    """ Return dict mapping key to the corresponding subsets coverage

        {'subsetname':
            {'fontname-light': 13, 'fontname-bold': 45},
         'subsetname':
            {'fontname-light': 9, 'fontname-bold': 100}
        }
    """
    library = Library(collections=['subsets'])
    subsets = {}
    for fontpath in source_fonts_paths:
        try:
            font = FontFactory.openfont(fontpath)
        except AssertionError:
            continue
        for info in font.get_orthographies(_library=library):

            subsetname = info.charmap.common_name.replace('Subset ', '')
            if subsetname not in subsets:
                subsets[subsetname] = {}

            subsets[subsetname][fontpath] = info.coverage
    return subsets


def generate_subsets_coverage_list():
    directory = UpstreamDirectory('.')

    source_fonts_paths = []
    # `get_sources_list` returns list of paths relative to root.
    # To complete to absolute paths use python os.path.join method
    # on root and path
    for p in directory.ALL_FONTS:
        source_fonts_paths.append(p)
    return get_subsets_coverage_data(source_fonts_paths)


process_files = []

extensions = ['.sfd', '.ufo', '.ttx', '.ttf']

for path, dirs, files in os.walk('.'):

    for f in files:
        for ext in extensions:
            if not f.endswith(ext):
                continue
            process_files.append('/'.join([path, f]))

    for d in dirs:
        for ext in extensions:
            if not d.endswith(ext):
                continue
            process_files.append('/'.join([path, d]))

import urwid.curses_display
import urwid.raw_display
import urwid.web_display
import urwid

def show_or_exit(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()

header = urwid.Text("Fontbakery Setup. Q exits.")


app = App()


widgets = []
if os.path.exists('.git/config'):
    githead = urwid.Text(u"Build a specific git commit, or HEAD? ")
    widgets.append(urwid.AttrMap(githead, 'key'))
    widgets.append(urwid.LineBox(app.widgets.commit))
    widgets.append(urwid.Divider())


widgets.append(urwid.AttrMap(urwid.Text('Which files to process?'), 'key'))
for f in process_files:
    widgets.append(app.widgets.create_process_file(f))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('License filename?'), 'key'))

for f in ['OFL.txt', 'LICENSE.txt', 'LICENSE']:
    if os.path.exists(f):
        widgets.append(urwid.RadioButton(app.widgets.licenses, f + ' (exists)',
                    state=bool(f == app.license)))
    else:
        widgets.append(urwid.RadioButton(app.widgets.licenses, f,
                    state=bool(f == app.license)))

widgets.append(urwid.Divider())
widgets.append(
    urwid.AttrMap(
        urwid.Text('What subsets do you want to create?'), 'key'))

subsets = generate_subsets_coverage_list()
for s in sorted(subsets):
    ll = ', '.join(set(['{}%'.format(subsets[s][k])
                        for k in subsets[s] if subsets[s][k]]))
    if ll:
        widgets.append(app.widgets.create_subset_widget(s, ll))


widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('ttfautohint command line parameters?'), 'key'))

widgets.append(urwid.LineBox(app.widgets.ttfautohint))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text(('New font family name (ie, replacing repo'
                ' codename with RFN)?')), 'key'))

widgets.append(urwid.LineBox(app.widgets.newfamily))


widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(app.widgets.create_checkbox('Use FontCrunch?', 'fontcrunch', app.fontcrunch), 'key'))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(app.widgets.create_checkbox('Run tests?', 'downstream', app.downstream), 'key'))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(app.widgets.create_checkbox('Run optimize?', 'optimize', app.optimize), 'key'))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('pyftsubset defaults parameters?'), 'key'))

widgets.append(urwid.LineBox(app.widgets.pyftsubset))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('Which compiler to use?'), 'key'))

widgets.append(urwid.Divider())
quote = ('By default, bakery uses fontforge to build fonts from ufo.'
         ' But some projects use automake, or their own build system'
         ' and perhaps the AFDKO.')
widgets.append(urwid.Padding(urwid.Text(quote), left=4))
widgets.append(urwid.Divider())

choices = ['fontforge', 'afdko', 'make', 'build.py']
for choice in choices:
    widgets.append(urwid.RadioButton(app.widgets.compiler, choice,
        state=bool(choice == app.compiler)))

widgets.append(urwid.Divider())

widgets.append(urwid.AttrMap(
    urwid.Text('afdko default command line parameters?'), 'key'))

widgets.append(urwid.LineBox(app.widgets.afdko_parameters))

widgets.append(urwid.Divider())
widgets.append(urwid.AttrMap(
    urwid.Text('Notes to display on Summary page?'), 'key'))

widgets.append(urwid.LineBox(app.widgets.notes))

widgets.append(urwid.Button(u'Save and Exit', on_press=app.save))

header = urwid.AttrWrap(header, 'header')
lw = urwid.SimpleListWalker(widgets)

listbox = urwid.ListBox(lw)
listbox = urwid.AttrWrap(listbox, 'listbox')
top = urwid.Frame(listbox, header)

palette = [('header', 'black', 'dark cyan', 'standout'),
           ('key', 'white', 'dark blue', 'bold'),
           ('listbox', 'light gray', 'black')]
loop = urwid.MainLoop(top, palette, unhandled_input=show_or_exit)
loop.run()
