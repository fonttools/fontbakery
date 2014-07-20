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
# pylint:disable-msg=E1101
import os

from datetime import datetime, timedelta
from flask import (Blueprint, render_template, g, flash, request,
                   url_for, redirect, Markup, current_app,
                   abort, make_response)
from flask.ext.babel import gettext as _
from functools import wraps
from yaml import YAMLError

from bakery.app import app
from bakery.decorators import login_required
from bakery.project.models import Project, ProjectBuild
from bakery.tasks import process_description_404
from bakery.utils import project_fontaine

import itsdangerous

project = Blueprint('project', __name__, url_prefix='/project')

DEFAULT_SUBSET_LIST = [
    'menu', 'latin', 'latin-ext+latin', 'cyrillic+latin', 'cyrillic-ext+latin',
    'greek+latin', 'greek-ext+latin', 'vietnamese+latin']


def chkhash(hashstr):
    try:
        int(hashstr, 16)
    except ValueError:
        flash(_('Error in provided data'))
        abort(500)


@project.before_request
def before_request():
    if g.user:
        g.projects = Project.query.filter_by(login=g.user.login).all()


# project resolve decorator
def project_required(f):
    """ Decorator reads project_id from arguments list and resolve it
        into project object.

        In parallel it check if project object is ready Usage:

        @project.route('/test', methods=['GET'])
        @project_required
        def test(p):
            # p is Project model instance
            return "Project is available"

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'project_id' in kwargs:
            project_id = kwargs.pop('project_id')
        else:
            project_id = args.pop(0)

        args = list(args)

        p = Project.query.filter_by(
            login=g.user.login, id=project_id).first_or_404()

        # Here can be located ownership access checks in the future.

        if p.is_ready:
            args.insert(0, p)
            return f(*args, **kwargs)
        else:
            flash(_('Project is being synchronized, wait until it is done'))
            return redirect(url_for('project.queue', project_id=p.id))

    return decorated_function


@project.route('/<int:project_id>', methods=['GET'])
@login_required
@project_required
def home(p):
    if not p.latest_build():
        return redirect(url_for('project.setup', project_id=p.id))
    return redirect(url_for('project.history', project_id=p.id))


@project.route('/api/<int:project_id>/checkout', methods=['GET'])
@login_required
@project_required
def checkout(p):
    if not p.config['local'].get('setup'):
        flash(_("Complete setup first"))
        return redirect(url_for('project.setup', project_id=p.id))

    from git import Repo
    path = os.path.join(app.config['DATA_ROOT'], p.login, '%s.in' % p.id)
    repo = Repo(path)
    revision = 'HEAD'
    if request.args.get('revision'):
        signer = itsdangerous.Signer(current_app.secret_key)
        revision = signer.unsign(request.args.get('revision'))
    repo.git.checkout(revision)
    return redirect(url_for('project.ufiles', project_id=p.id))


# API methods

@project.route('/api/<int:project_id>/build', methods=['GET'])
@login_required
@project_required
def build(p):
    """ Revision id is dangerous parameter, because it added to command line to
    git call. That is why it always should be signed with hash.
    """
    if not p.config['local'].get('setup'):
        flash(_("Complete setup first"))
        return redirect(url_for('project.setup', project_id=p.id))

    if request.args.get('revision'):
        signer = itsdangerous.Signer(current_app.secret_key)
        revision = signer.unsign(request.args.get('revision'))

        build = ProjectBuild.make_build(p, revision)
    else:
        build = ProjectBuild.make_build(p, 'HEAD')

    flash(Markup(_(("Updated repository (<a href='%(repo)s'>see files</a>)"
                    " Next step: <a href='%(step)s'>set it up</a>"),
                   repo=url_for('project.ufiles', project_id=p.id),
                   step=url_for('project.setup', project_id=p.id))))
    return redirect(url_for('project.log', project_id=p.id, build_id=build.id))


@project.route('/api/<int:project_id>/pull', methods=['GET'])
@login_required
# this is only exception where decorator @project_required is not needed
def pull(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    p.sync()

    flash(_("Pulling latest version from upstream"))
    return redirect(url_for('project.queue', project_id=p.id))


# Setup views


@project.route('/<int:project_id>/queue')
@login_required
def queue(project_id):
    p = Project.query.filter_by(login=g.user.login, id=project_id)
    p = p.first_or_404()
    param = {'login': p.login, 'id': p.id}
    log_file = "%(login)s/%(id)s.out/upstream.log" % param
    return render_template('project/queue.html', project=p, log_file=log_file)


@project.route('/<int:project_id>/setup', methods=['GET', 'POST'])
@login_required
@project_required
def setup(p):

    config = p.config
    originalConfig = p.config
    error = False

    if request.method == 'GET':
        return render_template('project/setup.html', project=p)

    if not request.form.get('license_file') in config['local']['txt_files']:
        error = True
        flash(_("Please select the license file"))
    config['state']['license_file'] = request.form.get('license_file')

    if request.form.get('familyname'):
        if len(request.form.get('familyname')) > 0:
            config['state']['familyname'] = request.form.get('familyname')
    else:
        if 'familyname' in config['state']:
            config['state'].pop('familyname')

    txt_files_to_copy = request.form.getlist('txt_files')
    config['state']['txt_files_copied'] = txt_files_to_copy

    # XXX: unsure should it be local or state property
    process_files = request.form.getlist('process_files')
    config['state']['process_files'] = process_files

    subset_list = request.form.getlist('subset')
    subsets = dict(p.get_subsets()).keys()
    for i in subset_list:
        if i not in subsets:
            error = True
            flash(_('Subset value is wrong'))

    for subset in subsets:
        if request.form.get('pyftsubset.%s' % subset):
            value = request.form.get('pyftsubset.%s' % subset, '')
            config['state']['pyftsubset.%s' % subset] = value

    if len(subset_list) < 0:
        error = True
        flash(_("Select at least one subset from list"))
    config['state']['subset'] = subset_list

    if request.form.get('ttfautohint'):
        if len(request.form.get('ttfautohint')) > 0:
            config['state']['ttfautohint'] = request.form.get('ttfautohint')
    else:
        if 'ttfautohint' in config['state']:
            config['state'].pop('ttfautohint')

    if error:
        return render_template('project/setup.html', project=p)

    if originalConfig != config:
        flash(_("Setup updated"))

    config['local']['setup'] = True
    p.save_state()
    if request.form.get('bake'):
        return redirect(url_for('project.build', project_id=p.id))
    else:
        flash(_("Setup saved"))
        return redirect(url_for('project.setup', project_id=p.id))


@project.route('/<int:project_id>/setup/dashboard_save', methods=['POST'])
@login_required
@project_required
def dashboard_save(p):
    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    for item in request.form:
        if request.form.get(item):
            if len(request.form.get(item)) > 0:
                p.config['state'][item] = request.form.get(item)
                flash(_('Set %(item)s', item=item))
        else:
            if item in p.config['state']:
                del p.config['state'][item]
                flash(_('Unset %(item)s', item=item))

    p.save_state()
    return redirect(url_for('project.setup', project_id=p.id))


# File browser views

@project.route('/<int:project_id>/files/', methods=['GET'])
@project.route('/<int:project_id>/files/<revision>/', methods=['GET'])
@login_required
@project_required
def ufiles(p, revision=None, name=None):
    # this page can be visible by others, not only by owner
    # TODO consider all pages for that
    if revision and revision != 'HEAD':
        chkhash(revision)
    else:
        revision = 'HEAD'

    return render_template('project/ufiles.html', project=p,
                           revision=revision)


@project.route('/<int:project_id>/files/<revision>/<path:name>')
@login_required
@project_required
def ufile(p, revision=None, name=None):
    # this page can be visible by others, not only by owner
    # TODO consider all pages for that
    if revision and revision != 'HEAD':
        chkhash(revision)
    else:
        revision = 'HEAD'

    mime, data = p.revision_file(revision, name)

    return render_template('project/ufile.html', project=p,
                           revision=revision, name=name, mime=mime, data=data)


@project.route('/<int:project_id>/files/<revision>/blob', methods=['GET'])
@login_required
@project_required
def ufileblob(p, revision=None):
    """ Mandatory parameter is `name` signed by cypher hash on server side.
    This view is pretty much "heavy", each request spawn additional process and
    read its output.
    """
    if revision and revision != 'HEAD':
        chkhash(revision)
    else:
        revision = 'HEAD'

    signer = itsdangerous.Signer(current_app.secret_key)
    name = signer.unsign(request.args.get('name'))

    mime, data = p.revision_file(revision, name)

    if mime.startswith('image'):
        response = make_response(data)
        response.headers['Content-Type'] = mime
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % name
        return response
    else:
        abort(500)


@project.route('/<int:project_id>/zip/<int:build_id>')
@login_required
@project_required
def zip(p, build_id):
    build = ProjectBuild.query.filter_by(project_id=p.id, id=build_id)
    build = build.first_or_404()

    param = build.get_path_params()
    zip_file = "%(login)s/%(id)s.out/%(build)s.%(revision)s.zip"

    try:
        path = os.path.join(current_app.config['DATA_ROOT'], zip_file % param)
        data = open(path).read()
    except (OSError, IOError):
        abort(404)

    response = make_response(data)
    response.headers['Content-Type'] = 'application/octet-stream'
    disposition = 'attachment; filename=%s' % os.path.basename(path)
    response.headers['Content-Disposition'] = disposition
    return response


# Builds views

@project.route('/<int:project_id>/build', methods=['GET'])
@login_required
@project_required
def history(p):
    """ Results of processing tests, for ttf files """
    b = ProjectBuild.query.filter_by(project=p).order_by("id desc").all()
    if not len(b):
        return redirect(url_for('project.setup', project_id=p.id))
    return render_template('project/history.html', project=p, builds=b)


@project.route('/<int:project_id>/build/<int:build_id>/log', methods=['GET'])
@login_required
@project_required
def log(p, build_id):
    b = ProjectBuild.query.filter_by(id=build_id, project=p).first_or_404()
    param = {'login': p.login, 'id': p.id,
             'revision': b.revision, 'build': b.id}
    log_file = "%(login)s/%(id)s.out/%(build)s.%(revision)s.process.log"

    return render_template('project/log.html', project=p, build=b,
                           log_file=log_file % param)


def get_fonts_table_sizes(fonts):
    """ Returns list of dictionary data for SFNT table sizes of fonts

        .. note:: Each dictionary has a format defined below

        name: <example com>
        tables:
          -
            name: <example sfnt name>
            size: <example sfnt size>
    """
    from bakery.app import app
    from fontTools.ttLib import sfnt
    sfntdata = []
    for font in fonts:
        tables = []
        with open(os.path.join(app.config['DATA_ROOT'], font)) as fp_font:
            sf = sfnt.SFNTReader(fp_font)
            for t in sf.tables:
                tables.append({'name': t, 'size': sf.tables[t].length})
        sfntdata.append({'name': os.path.basename(font), 'tables': tables})
    return sfntdata


def get_orthography(fontaine):
    from fontaine.cmap import Library
    library = Library(collections=['subsets'])
    return fontaine.get_orthographies(_library=library)


@project.route('/<int:project_id>/build/<int:build_id>/rfiles')
@login_required
@project_required
def rfiles(p, build_id):
    b = ProjectBuild.query.filter_by(id=build_id, project=p).first_or_404()

    if not b.is_done:
        return redirect(url_for('project.log', project_id=p.id, build_id=b.id))

    yaml = p.read_asset('yaml')
    f = project_fontaine(p, b)
    tree = b.files()

    fonts = []
    for k, v in tree.items():
        if k.endswith('.ttf'):
            fonts.append(os.path.join(b.path, k))

    ttftablesizes = get_fonts_table_sizes(fonts)

    from scripts.vmet import metricview
    return render_template('project/rfiles.html', project=p, yaml=yaml,
                           fontaineFonts=f, build=b, tree=tree,
                           ttftablesizes=ttftablesizes,
                           get_orthography=get_orthography,
                           vmettable=metricview(fonts))


@project.route('/<int:project_id>/build/<int:build_id>/tests', methods=['GET'])
@login_required
@project_required
def rtests(p, build_id):
    """ Results of processing tests, for ttf files """
    b = ProjectBuild.query.filter_by(id=build_id, project=p).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    test_result = b.result_tests()
    if not test_result:
        abort(404)

    fix_asap_summary = []
    for y, x in test_result.items():
        for t in x['failure']:
            if 'required' in t.get('tags', ''):
                fix_asap_summary.append(dict(font=y, **t))

    summary = {
        'all_tests': sum([int(y.get('sum', 0)) for x, y in test_result.items()]),
        'fonts': test_result.keys(),
        'all_error': sum([len(x.get('error', [])) for x in test_result.values()]),
        'all_failure': sum([len(x.get('failure', [])) for x in test_result.values()]),
        'all_fixed': sum([len(x.get('fixed', [])) for x in test_result.values()]),
        'all_success': sum([len(x.get('success', [])) for x in test_result.values()]),
        'fix_asap': fix_asap_summary,
    }
    return render_template('project/rtests.html', project=p,
                           tests=test_result, build=b, summary=summary)


@project.route('/<int:project_id>/build/<int:build_id>/', methods=['GET'])
@login_required
@project_required
def summary(p, build_id):
    """ Results of processing tests, for ttf files """
    b = ProjectBuild.query.filter_by(id=build_id, project=p).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    test_result = b.result_tests()

    if not test_result:
        abort(404)

    fix_asap_summary = []
    for y, x in test_result.items():
        for t in x['failure']:
            if 'required' in t.get('tags', ''):
                fix_asap_summary.append(dict(font=y, **t))

    summary = {
        'all_tests': sum([int(y.get('sum', 0)) for x, y in test_result.items()]),
        'fonts': test_result.keys(),
        'all_error': sum([len(x.get('error', [])) for x in test_result.values()]),
        'all_failure': sum([len(x.get('failure', [])) for x in test_result.values()]),
        'all_fixed': sum([len(x.get('fixed', [])) for x in test_result.values()]),
        'all_success': sum([len(x.get('success', [])) for x in test_result.values()]),
        'fix_asap': fix_asap_summary
    }
    return render_template('project/summary.html', project=p,
                           tests=test_result, build=b, summary=summary)


@project.route('/<int:project_id>/build/<int:build_id>/description', methods=['GET', 'POST'])
@login_required
@project_required
def description(p, build_id):
    """ Description file management """

    b = ProjectBuild.query.filter_by(id=build_id, project=p).first_or_404()

    if request.method == 'GET':
        try:
            test_data = b.read_links404_test_data()
            if test_data['updated'] < datetime.now() - timedelta(days=1):
                # rerun background to check description 404 links
                process_description_404.delay(p, b)
            parsed_results = test_data.get('failure', [])
        except (IOError, YAMLError, KeyError):
            # possibly file does not exist, start background task if that so
            process_description_404.delay(p, b)
            parsed_results = []

        data = b.read_asset('description')
        return render_template('project/description.html', project=p, build=b,
                               description=data, failures=parsed_results)

    # POST
    b.save_asset('description', request.form.get('description'))
    flash(_('Description saved'))

    return redirect(url_for('project.description', build_id=b.id,
                            project_id=p.id))


@project.route('/<int:project_id>/build/<int:build_id>/metadatajson', methods=['GET', 'POST'])
@login_required
@project_required
def metadatajson(p, build_id):
    b = ProjectBuild.query.filter_by(id=build_id, project=p).first_or_404()

    if request.method == 'POST':
        metadatajson = request.form.get('metadatajson')
        try:
            import json
            from bakery.tasks import execute_metadata_tests
            json.loads(metadatajson)
            b.save_asset('metadata', metadatajson)
            execute_metadata_tests.delay(p.login, p.id, b.id, b.revision)
            flash('METADATA.json has been saved')
        except Exception, ex:
            flash('Unable to save METADATA.json for build %s' % ex)
        return redirect(url_for('project.metadatajson', project_id=p.id,
                                build_id=b.id))

    metadata = b.read_asset('metadata')
    metadata_new = b.read_asset('metadata_new')
    return render_template('project/metadatajson.html', project=p, build=b,
                           metadata=metadata, metadata_new=metadata_new)


# Base views

@project.route('/<int:project_id>/tests/<revision>', methods=['GET'])
@login_required
@project_required
def utests(p, revision):
    """ Results of processing tests, for ufo files """
    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    test_result = p.revision_tests(revision)
    return render_template('project/utests.html', project=p, revision=revision,
                           tests=test_result)


@project.route('/<int:project_id>/git', methods=['GET'])
@login_required
@project_required
def git(p):
    """ Results of processing tests, for ttf files """
    gitlog = p.gitlog()

    return render_template('project/gitlog.html', project=p, log=gitlog)


@project.route('/<int:project_id>/diff', methods=['GET'])
@login_required
@project_required
def diff(p):
    """ Show diff between different revisions, since we want to make this view
    more user friendly we can't signify left and right revision. And this mean
    that we should check input data"""

    if not all([request.args.get('left'), request.args.get('right')]):
        flash(_("Left and right hash for comparsion should be provided"))

    try:
        left = request.args.get('left')
        right = request.args.get('right')
        # let python try to parse strings, if it fails then there can be
        # something evil
        int(left, 16)
        int(right, 16)
    except ValueError:
        flash(_('Error in provided data'))
        return redirect(url_for('project.git', project_id=p.id))

    diffdata = p.diff_files(left, right)

    return render_template('project/diff.html', project=p,
                            diff=diffdata, left=left, right=right)
