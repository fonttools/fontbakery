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
                   url_for, redirect)
from flask.ext.babel import gettext as _

from ..decorators import login_required
from ..tasks import (project_tests, sync_and_process)
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
    if g.debug:
        # pylint:disable-msg=E1101
        p = Project.query.filter_by(
            login=g.user.login, id=project_id).first_or_404()
        sync_and_process.delay(p, process = False, sync = True)
        flash(_("Git %s was updated" % p.clone))
    return redirect(url_for('project.buildlog', project_id=project_id))


@project.route('/<int:project_id>/setup', methods=['GET', 'POST'])
@login_required
def setup(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    config = p.config

    if request.method == 'GET':
        return render_template('project/setup.html', project=p,
                               subsetvals=DEFAULT_SUBSET_LIST)
    # else:
    error = False

    if not request.form.get('license_file') in config['local']['txt_files']:
        error = True
        flash(_("Wrong license_file value, must be an error"))

    config['state']['license_file'] = request.form.get('license_file')

    if request.form.get('familyname'):
        if len(request.form.get('familyname')) > 0:
            config['state']['familyname'] = request.form.get('familyname')
    # else:
    #    config['state'].pop('familyname')

    ufo_dirs = request.form.getlist('ufo')
    for i in ufo_dirs:
        if i not in config['local']['ufo_dirs']:
            error = True
            flash(_("Wrong value for UFO folder, must be an error"))

    if len(ufo_dirs)<0:
        error = True
        flash(_("Select at least one UFO folder"))

    # TODO: check that all ufo have same font familyname

    config['state']['ufo'] = ufo_dirs

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
        config['state'].pop('ttfautohint')

    if error:
        return render_template('project/setup.html', project=p,
                               subsetvals=DEFAULT_SUBSET_LIST)

    config['local']['setup'] = True
    flash(_("Repository %s has been updated" % p.clone))
    p.save_state()

    sync_and_process.delay(p, process = True, sync = False)
    return redirect(url_for('project.buildlog', project_id=p.id))


@project.route('/<int:project_id>/', methods=['GET'])
@login_required
def fonts(project_id):
    # this page can be visible by others, not only by owner
    p = Project.query.get_or_404(project_id)
    return render_template('project/fonts.html', project=p)

@project.route('/<int:project_id>/license', methods=['GET'])
@login_required
def plicense(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    data = p.read_asset('license')
    return render_template('project/license.html', project=p, license=data)


@project.route('/<int:project_id>/ace', methods=['GET'])
@login_required
def ace(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    metadata = p.read_asset('metadata')
    metadata_new = p.read_asset('metadata_new')
    return render_template('project/ace.html', project=p,
                           metadata=metadata, metadata_new=metadata_new)


@project.route('/<int:project_id>/ace', methods=['POST'])
@login_required
def ace_save(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    p.save_asset('metadata', request.form.get('metadata'),
                 del_new=request.form.get('delete', None))
    flash(_('METADATA.json saved'))
    return redirect(url_for('project.ace', project_id=p.id))


@project.route('/<int:project_id>/description_edit', methods=['GET'])
@login_required
def description_edit(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    data = p.read_asset('description')
    return render_template('project/description.html', project = p, description = data)


@project.route('/<int:project_id>/description_save', methods=['POST'])
@login_required
def description_save(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    p.save_asset('description', request.form.get('description'))
    flash(_('Description saved'))
    return redirect(url_for('project.description_edit', project_id=p.id))


@project.route('/<int:project_id>/log', methods=['GET'])
@login_required
def buildlog(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    data = p.read_asset('log')
    return render_template('project/log.html', project=p, log=data)


@project.route('/<int:project_id>/yaml', methods=['GET'])
@login_required
def bakeryyaml(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    data = p.read_asset('yaml')
    return render_template('project/yaml.html', project=p, yaml=data)


@project.route('/<int:project_id>/tests', methods=['GET'])
@login_required
def tests(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    test_result = project_tests(project=p)
    return render_template('project/tests.html', project=p,
                           tests=test_result)

@project.route('/<int:project_id>/dashboard', methods=['GET'])
@login_required
def dashboard(project_id):
   p = Project.query.filter_by(
       login=g.user.login, id=project_id).first_or_404()
   return render_template('project/dashboard.html', project=p)

@project.route('/<int:project_id>/dashboard_save', methods=['POST'])
@login_required
def dashboard_save(project_id):
    p = Project.query.filter_by(
        login=g.user.login, id=project_id).first_or_404()
    if request.form.get('source_drawing_filetype'):
        if len(request.form.get('source_drawing_filetype')) > 0:
            p.config['state']['source_drawing_filetype'] = request.form.get('source_drawing_filetype')
    p.save_state()
    flash(_('source_drawing_filetype saved'))
    return redirect(url_for('project.dashboard', project_id=p.id))
