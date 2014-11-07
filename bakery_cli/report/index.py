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
from collections import defaultdict, Counter, namedtuple, OrderedDict
import os
import os.path as op
import yaml

import fontforge
from fontaine.cmap import Library
from fontaine.font import FontFactory

from bakery_cli.scripts.vmet import get_metric_view
from bakery_cli.utils import UpstreamDirectory

from bakery_cli.report import utils as report_utils

from bakery_lint.metadata import Metadata

TAB = 'Index'
TEMPLATE_DIR = op.join(op.dirname(__file__), 'templates')

t = lambda templatefile: op.join(TEMPLATE_DIR, templatefile)


def sort(data):
    a = []
    for grouped_dict in data:
        if 'required' in grouped_dict['tags']:
            a.append(grouped_dict)

    for grouped_dict in data:
        if 'note' in grouped_dict['tags'] and 'required' not in grouped_dict['tags']:
            a.append(grouped_dict)

    for grouped_dict in data:
        if 'note' not in grouped_dict['tags'] and 'required' not in grouped_dict['tags']:
            a.append(grouped_dict)

    return a


def filter_with_tag(fonttestdata, tag):
    tests = fonttestdata['failure'] + fonttestdata['error']
    return [test for test in tests if tag in test['tags']]


def filter_by_results_with_tag(fonttestdata, tag, *results):
    tests = {}
    for res in results:
        tests[res] = [test for test in fonttestdata.get(res) if tag in test.get('tags', [])]
    return tests


def get_fonts_table_sizes(fonts):
    """ Returns tuple with available tables from all fonts and their length """
    from fontTools.ttLib import sfnt
    _fonts = {}
    tables = []
    for font in fonts:
        _fonts[op.basename(font)] = {}
        with open(font) as fp_font:
            sf = sfnt.SFNTReader(fp_font)
            for t in sf.tables:
                if t not in tables:
                    tables.append(t)
                _fonts[op.basename(font)][t] = sf.tables[t].length
    return tables, _fonts


def get_fonts_table_sizes_grouped(fonts_list):
    _, fonts = get_fonts_table_sizes(fonts_list)
    fonts_dict = defaultdict(dict, fonts)

    # Fonts may have different tables!!!

    # across all fonts calculate sum of each table
    table_sizes_sums = sum(
        (Counter(v) for k, v in fonts_dict.iteritems()), Counter()
    )

    # count amount of each table across all fonts
    tables_counts = sum(
        (Counter(v.keys()) for k, v in fonts_dict.iteritems()), Counter()
    )

    # count average for each table, take value from 'table_sizes_sums'
    # and divide by corresponding value from  'tables_counts',
    # eg table_sizes_sums['glyf'] / tables_counts['glyf']
    tables_mean_dict = {
        k: table_sizes_sums[k]/tables_counts[k] for k in table_sizes_sums
    }

    # calculate deviation (delta) from an average
    # for each font and each table in font find delta
    tables_delta_dict = {}
    for font, tables in fonts_dict.iteritems():
        tables_delta_dict[font] = {
            k: tables_mean_dict[k]-v for k, v in tables.iteritems()
        }

    # gather all existent tables from all fonts
    all_possible_tables = set()
    for font, tables in tables_delta_dict.items():
        for table in tables:
            if table not in all_possible_tables:
                all_possible_tables.add(table)

    # if some font does not have a table that others have,
    # just set the deviation to 0
    for font, tables in tables_delta_dict.items():
        for item in all_possible_tables:
            tables.setdefault(item, 0)
        tables_delta_dict[font] = tables

    # make the deviation dict ready for google chart as array
    tables_delta_dict_for_google_array = {}
    for font, props in tables_delta_dict.iteritems():
        tables_delta_dict_for_google_array.setdefault('fonts', []).append(font)
        for k, v in props.iteritems():
            tables_delta_dict_for_google_array.setdefault(k, []).append(v)

    # prepare all tables dict as array for google chart
    tables_dict_for_google_array = {}
    for font, props in fonts.iteritems():
        tables_dict_for_google_array.setdefault('fonts', []).append(font)
        for k, v in props.iteritems():
            tables_dict_for_google_array.setdefault(k, []).append(v)

    grouped_dict = {
        'fonts': tables_dict_for_google_array.pop('fonts'),
        'tables': [
            [k, tables_mean_dict[k]] + v for k, v in tables_dict_for_google_array.items()
        ]
    }

    delta_dict = {
        'fonts': tables_delta_dict_for_google_array.pop('fonts'),
        'tables': [
            [k, ] + v for k, v in tables_delta_dict_for_google_array.items()
        ]
    }

    # make all arrays to have same len
    max_len = len(max(grouped_dict['tables'], key=len))
    new_items = []
    for item in grouped_dict["tables"]:
        new_item = item[:]
        while len(new_item) < max_len:
            new_item.append(0)
        new_items.append(new_item)
    grouped_dict["tables"] = new_items

    ftable = namedtuple('FontTable', ['mean', 'grouped', 'delta'])
    return ftable(tables_mean_dict, grouped_dict, delta_dict)


def get_orthography(fontaineFonts):
    fonts_dict = defaultdict(list)
    library = Library(collections=['subsets'])
    fonts_names = []
    for font, fontaine in fontaineFonts:
        fonts_names.append(font)
        for info in fontaine.get_orthographies(_library=library):
            font_info = dict(name=font, support=info.support_level,
                             coverage=info.coverage,
                             missing_chars=info.missing)
            fonts_dict[info.charmap.common_name].append(font_info)
    averages = {}
    for subset, fonts in fonts_dict.items():
        averages[subset] = sum([font['coverage'] for font in fonts]) / len(fonts)
    return sorted(fonts_names), averages, OrderedDict(sorted(fonts_dict.items()))


def to_google_data_list(tdict, haxis=0):
    return sorted([[x, tdict[x] - haxis] for x in tdict])


def font_table_to_google_data_list(tdict):
    return sorted([list(item) for item in tdict.items()])


def average_table_size(tdict):
    return sum(tdict.values()) / len(tdict)


def _obj_to_dict(instance, exclude_attrs=()):
    # Very simplified, but enough for reports
    return {
        k: getattr(instance, k) for k in dir(instance) \
        if not any([k.startswith('__'), str(k) in exclude_attrs])
    }


def font_factory_instance_to_dict(instance):
    return _obj_to_dict(instance, exclude_attrs=(
        'get_othography_info', 'get_orthographies', 'orthographies',
        'refresh_sfnt_properties', '_fontFace', 'getGlyphNames'
    ))


def get_stem(fontfile, glyph='n'):
    ttf = fontforge.open(fontfile)
    if ttf.italicangle != 0.0:
        return None
    glyph = ttf[glyph]
    if not glyph.vhints:
        glyph.autoHint()
    if not glyph.vhints:
        return None
    v_hints = [item[1] for item in glyph.vhints]
    return sum(v_hints)/len(v_hints)


def generate(config):
    if config.get('failed'):
        return

    directory = UpstreamDirectory(config['path'])
    if op.exists(op.join(config['path'], 'METADATA.new.json')):
        metadata_file = open(op.join(config['path'], 'METADATA.new.json')).read()
    else:
        metadata_file = open(op.join(config['path'], 'METADATA.json')).read()
    family_metadata = Metadata.get_family_metadata(metadata_file)
    faces = []
    for f in family_metadata.fonts:
        faces.append({'name': f.full_name,
                      'basename': f.post_script_name,
                      'path': f.filename,
                      'meta': f})

    metadata = yaml.load(open(op.join(config['path'], 'METADATA.yaml')))
    upstreamdata = {}
    upstreamdatafile = op.join(config['path'], 'upstream.yaml')
    if op.exists(upstreamdatafile):
        upstreamdata = yaml.load(open(upstreamdatafile))

    data = {}
    for fp in directory.BIN:
        path = op.join(config['path'], '{}.yaml'.format(fp[:-4]))
        if op.exists(path):
            data[fp] = yaml.load(open(path))
    data.update(metadata)
    data.update(upstreamdata)

    fontpaths = [op.join(config['path'], path)
                 for path in directory.BIN]
    ttftablesizes = get_fonts_table_sizes(fontpaths)

    ftables_data = get_fonts_table_sizes_grouped(fontpaths)

    buildstate = yaml.load(open(op.join(config['path'], 'build.state.yaml')))
    autohint_sizes = buildstate.get('autohinting_sizes', [])
    vmet = get_metric_view(fontpaths)

    fonts = [(path, FontFactory.openfont(op.join(config['path'], path)))
             for path in directory.BIN]

    stems = []
    for path in directory.BIN:
        stem = get_stem(op.join(config['path'], path))
        if not stem:
            continue
        stems.append(dict(fontname=path, stem=stem))

    new_data = []
    for k in data:
        d = {'name': k}
        d.update(data[k])
        new_data.append(d)

    report_app = report_utils.BuildInfo(config)
    metrics = {'data': vmet._its_metrics, 'headings': vmet._its_metrics_header}
    table_sizes = {'tables': ttftablesizes[0], 'sizes': ttftablesizes[1:]}
    report_app.summary_page.dump_file(metrics, 'metrics.json')
    report_app.summary_page.dump_file(stems, 'stems.json')
    report_app.summary_page.dump_file(table_sizes, 'table_sizes.json')
    report_app.summary_page.dump_file(autohint_sizes, 'autohint_sizes.json')
    report_app.summary_page.dump_file(new_data, 'tests.json')
    report_app.summary_page.dump_file({'mean': ftables_data.mean,
                                       'grouped': ftables_data.grouped,
                                       'delta': ftables_data.delta},
                                      'fonts_tables_grouped.json')
    for face in family_metadata.fonts:
        face_template = "@font-face {{ font-family: {}; src: url(fonts/{});}}\n".format(face.metadata_object['postScriptName'], face.metadata_object['filename'])
        report_app.write_file(face_template, op.join(report_app.css_dir, 'faces.css'), mode='a')

    fonts_serialized = dict([(str(path), font_factory_instance_to_dict(fontaine)) for path, fontaine in fonts])
    report_app.summary_page.dump_file(fonts_serialized, 'fontaine_fonts.json')
    fonts_orthography = get_orthography(fonts)
    report_app.summary_page.dump_file({'fonts_list': fonts_orthography[0],
                                       'coverage_averages': fonts_orthography[1],
                                       'fonts_info': fonts_orthography[2]},
                                      'fonts_orthography.json')
