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

from flask import (Blueprint, render_template, g, flash, request,
                   url_for, redirect, json, Markup)
from flask.ext.babel import gettext as _

from ..decorators import login_required
from ..tasks import sync_and_process
from ..utils import (project_result_tests, project_upstream_tests, project_fontaine)
from .models import Project

project = Blueprint('project', __name__, url_prefix='/project')

DEFAULT_SUBSET_LIST = [
    'menu', 'latin', 'latin-ext+latin', 'cyrillic+latin', 'cyrillic-ext+latin',
    'greek+latin', 'greek-ext+latin', 'vietnamese+latin']


@project.before_request
def before_request():
    if g.user:
        g.projects = Project.query.filter_by(login=g.user.login).all()


@project.route('/<int:project_id>/bump', methods=['GET'])
@login_required
def bump(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    sync_and_process.delay(p, process = False, sync = True)
    flash(Markup(_("Updated repository (<a href='%s'>see files</a>) Next step: <a href='%s'>set it up</a>" % (url_for('project.ufiles', project_id=project_id), url_for('project.setup', project_id=project_id)))))
    return redirect(url_for('project.log', project_id=project_id))

@project.route('/<int:project_id>/', methods=['GET', 'POST'])
@login_required
def setup(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    config = p.config
    originalConfig = p.config
    error = False

    if request.method == 'GET':
        return render_template('project/index.html', project=p,
                               subsetvals=DEFAULT_SUBSET_LIST)

    if not request.form.get('license_file') in config['local']['txt_files']:
        error = True
        flash(_("Please select the license file"))
    config['state']['license_file'] = request.form.get('license_file')

    if request.form.get('familyname'):
        if len(request.form.get('familyname')) > 0:
            config['state']['familyname'] = request.form.get('familyname')
    else:
        if config['state'].has_key('familyname'):
            config['state'].pop('familyname')

    ufo_dirs = request.form.getlist('ufo')
    for i in ufo_dirs:
        if i not in config['local']['ufo_dirs']:
            error = True
            flash(_("Please select at least one UFO"))
    if len(ufo_dirs) < 0:
        error = True
        flash(_("Select at least one UFO"))
    config['state']['ufo'] = ufo_dirs

    txt_files_to_copy = request.form.getlist('txt_files')
    config['state']['txt_files_copied'] = txt_files_to_copy

    subset_list = request.form.getlist('subset')
    for i in subset_list:
        if i not in DEFAULT_SUBSET_LIST:
            error = True
            flash(_('Subset value is wrong'))
    if len(subset_list)<0:
        error = True
        flash(_("Select at least one subset from list"))
    config['state']['subset'] = subset_list

    if request.form.get('ttfautohint'):
        if len(request.form.get('ttfautohint')) > 0:
            config['state']['ttfautohint'] = request.form.get('ttfautohint')
    else:
        if config['state'].has_key('ttfautohint'):
            config['state'].pop('ttfautohint')

    if error:
        return render_template('project/index.html', project=p,
                               subsetvals=DEFAULT_SUBSET_LIST)

    if originalConfig != config:
        flash(_("Setup updated"))

    p.save_state()
    if request.form.get('bake'):
        # This marks that the setup is ready enough to bake the project
        # When it is set, the user is not asked again, 'Do you have permission to use the fonts names as presented to the user in modified versions?'
        config['local']['setup'] = True
        p.save_state()
        sync_and_process.ctx_delay(p, process = True, sync = False)
        return redirect(url_for('project.log', project_id=p.id))
    else:
        flash(_("Setup saved"))
        return redirect(url_for('project.setup', project_id=p.id))


@project.route('/<int:project_id>/ufiles', methods=['GET'])
@login_required
def ufiles(project_id):
    # this page can be visible by others, not only by owner
    # TODO consider all pages for that
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    license = p.read_asset('license')
    textfiles = p.textFiles()
    return render_template('project/ufiles.html', project=p, license=license, textfiles=textfiles)

@project.route('/<int:project_id>/metadatajson', methods=['GET'])
@login_required
def metadatajson(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    metadata = p.read_asset('metadata')
    metadata_new = p.read_asset('metadata_new')
    return render_template('project/metadatajson.html', project=p,
                           metadata=metadata, metadata_new=metadata_new)


@project.route('/<int:project_id>/metadatajson', methods=['POST'])
@login_required
def metadatajson_save(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    try:
        # this line trying to parse json
        json.loads(request.form.get('metadata'))
        p.save_asset('metadata', request.form.get('metadata'),
                     del_new=request.form.get('delete', None))
        flash(_('METADATA.json saved'))
        return redirect(url_for('project.metadatajson', project_id=p.id))
    except ValueError:
        flash(_('Wrong format for METADATA.json file'))
        metadata_new = p.read_asset('metadata_new')
        return render_template('project/metadatajson.html', project=p,
                           metadata=request.form.get('metadata'), metadata_new=metadata_new)


@project.route('/<int:project_id>/description', methods=['GET'])
@login_required
def description(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    data = p.read_asset('description')
    return render_template('project/description.html', project = p, description = data)


@project.route('/<int:project_id>/description_save', methods=['POST'])
@login_required
def description_save(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    p.save_asset('description', request.form.get('description'))
    flash(_('Description saved'))
    return redirect(url_for('project.description', project_id=p.id))


@project.route('/<int:project_id>/log', methods=['GET'])
@login_required
def log(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    data = p.read_asset('log')
    return render_template('project/log.html', project=p, log=data)


@project.route('/<int:project_id>/rfiles', methods=['GET'])
@login_required
def rfiles(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    data = p.read_asset('yaml')
    return render_template('project/rfiles.html', project=p, yaml=data)


@project.route('/<int:project_id>/utests', methods=['GET'])
@login_required
def utests(project_id):
    """ Results of processing tests, for ufo files """
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    test_result = project_upstream_tests(project=p)
    return render_template('project/utests.html', project=p,
                           tests=test_result)


@project.route('/<int:project_id>/rtests', methods=['GET'])
@login_required
def rtests(project_id):
    """ Results of processing tests, for ttf files """
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    test_result = project_result_tests(project=p)
    return render_template('project/rtests.html', project=p,
                           tests=test_result)

@project.route('/<int:project_id>/dashboard_save', methods=['POST'])
@login_required
def dashboard_save(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    for item in request.form:
        if request.form.get(item):
            if len(request.form.get(item)) > 0:
                p.config['state'][item] = request.form.get(item)
                flash(_('Set ' + item))
        else:
            if item in p.config['state']:
                del p.config['state'][item]
                flash(_('Unset ' + item))

    p.save_state()
    return redirect(url_for('project.setup', project_id=p.id))

@project.route('/<int:project_id>/fontaine', methods=['GET'])
@login_required
def fontaine(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()

    if not p.is_ready:
        return redirect(url_for('project.log', project_id=p.id))

    f = project_fontaine(project=p)

    return render_template('project/fontaine.html', project=p,
                            fontaineFonts=f)
