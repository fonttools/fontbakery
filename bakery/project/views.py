# coding: utf-8
import logging

from flask import (Blueprint, render_template, g, flash, request,
    url_for, redirect)
from flask.ext.babel import gettext as _

from ..decorators import login_required
# from ..extensions import db
from ..tasks import *
from .models import Project

project = Blueprint('project', __name__, static_folder='../../data/', url_prefix='/project')

DEFAULT_SUBSET_LIST = ['menu', 'latin', 'latin-ext+latin', 'cyrillic+latin', 'cyrillic-ext+latin',
    'greek+latin', 'greek-ext+latin', 'vietnamese+latin']

@project.before_request
def before_request():
    if g.user:
        g.projects = Project.query.filter_by(login=g.user.login).all()

@login_required
@project.route('/bump', methods=['GET'])
def bump():
    project_id = request.args.get('project_id')
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()
    logging.info('Update for project %s by %s' % (project_id, g.user.login))
    git_clone(login = g.user.login, project_id = project.id, clone=project.clone)
    process_project(login = g.user.login, project_id = project_id)
    flash(_("Git %s was updated" % project.clone))
    return redirect(url_for('project.fonts', project_id = project_id))

@login_required
@project.route('/<int:project_id>/setup', methods=['GET', 'POST'])
def setup(project_id):
    state = project_state_get(login = g.user.login, project_id = project_id, full=True)
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()

    #import ipdb; ipdb.set_trace()
    if request.method == 'GET':
        return render_template('project/setup.html', project = project, state = state)
    else:
        if request.form.get('step') == '2':
            # 1st step
            if request.form.get('license_file') in state['txt_files']:
                state['license_file'] = request.form.get('license_file')
            else:
                flash(_("Wrong license_file value, must be an error"))
                return render_template('setup.html', project = project, state = state)
            ufo_dirs = request.form.getlist('ufo_dirs')
            for i in ufo_dirs:
                if i not in state['ufo_dirs']:
                    flash(_("Wrong ufo_dir value, must be an error"))
                    return render_template('project/setup.html', project = project, state = state)
                if not state['out_ufo'].get(i):
                    # define font name based on ufo folder name.
                    state['out_ufo'][i] = i.split('/')[-1][:-4]
            for i in state['out_ufo'].keys():
                # don't want to delete other properties
                if i not in ufo_dirs:
                    del state['out_ufo'][i]

            subset_list = request.form.getlist('subset')
            for i in subset_list:
                try:
                    assert i in DEFAULT_SUBSET_LIST
                except AssertionError:
                    flash('Subset value is wrong')
                    return render_template('project/setup.html', project = project, state = state)

            state['subset'] = subset_list

            if request.form.get('rename') == 'yes':
                state['rename'] = True
            else:
                state['rename'] = False

            if request.form.get('ttfautohint'):
                state['ttfautohint'] = request.form.get('ttfautohint')

            # setup is done, now you can process files
            state['autoprocess'] = True

            project_state_save(login = g.user.login, project_id = project_id, state = state)

            if request.form.get('rename') == 'yes':
                return render_template('project/setup2.html', project = project, state = state)
            else:
                flash(_("Repository %s has been updated" % project.clone))
                fh = add_logger(login = g.user.login, project_id = project_id)
                process_project(login = g.user.login, project_id = project_id)
                remove_logger(fh)
                return redirect(url_for('project.fonts', project_id=project_id))
        elif request.form.get('step')=='3':
            out_ufo = {}
            for param, value in request.form.items():
                if not param.startswith('ufo-'):
                    continue
                if param[4:] in state['out_ufo']:
                    # XXX: there is no sanity check for value yet
                    out_ufo[param[4:]] = value
                else:
                    flash(_("Wrong parameter provided for ufo folder name"))
            state['out_ufo'] = out_ufo
            project_state_save(login = g.user.login, project_id = project_id, state = state)
            process_project(login = g.user.login, project_id = project_id)
            return redirect(url_for('project.fonts', project_id=project_id))
        else:
            flash(_("Strange behaviour detected"))
            return redirect(url_for('project.fonts', project_id=project_id))

# @project.route('/<int:project_id>', methods=['GET'])
@project.route('/<int:project_id>/', methods=['GET'])
def fonts(project_id):
    state = project_state_get(login = g.user.login, project_id = project_id, full=True)
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()
    if state.get('autoprocess'):
        tree = read_tree(login = g.user.login, project_id = project_id)
        return render_template('project/fonts.html', project = project, state = state, tree = tree)
    else:
        return redirect(url_for('project.setup', project_id = project_id))

@project.route('/<int:project_id>/license', methods=['GET'])
def plicense(project_id):
    state = project_state_get(login = g.user.login, project_id = project_id, full=True)
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()
    license = read_license(login = g.user.login, project_id = project_id)
    return render_template('project/license.html', project = project, state = state, license = license)

@project.route('/<int:project_id>/ace', methods=['GET'])
def ace(project_id):
    state = project_state_get(login = g.user.login, project_id = project_id, full=True)
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()
    metadata, metadata_new = read_metadata(login = g.user.login, project_id = project_id)
    return render_template('project/ace.html', project = project,
        state = state, metadata = metadata, metadata_new = metadata_new)

@project.route('/<int:project_id>/ace', methods=['POST'])
def ace_save(project_id):
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()
    save_metadata(login = g.user.login, project_id = project_id,
        metadata = request.form.get('metadata'),
        del_new = request.form.get('delete', None))
    flash('METADATA.json saved')
    return redirect(url_for('project.ace', project_id=project_id))


@project.route('/<int:project_id>/description_edit', methods=['GET'])
def description_edit(project_id):
    state = project_state_get(login = g.user.login, project_id = project_id, full=True)
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()
    description = read_description(login = g.user.login, project_id = project_id)
    return render_template('project/description.html', project = project,
        state = state, description = description)

@project.route('/<int:project_id>/description_save', methods=['POST'])
def description_save(project_id):
    state = project_state_get(login = g.user.login, project_id = project_id, full=True)
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()
    save_description(login = g.user.login, project_id = project_id,
        description = request.form.get('description'))
    flash('Description saved')
    return redirect(url_for('project.description_edit', project_id=project_id))

@project.route('/<int:project_id>/log', methods=['GET'])
def buildlog(project_id):
    state = project_state_get(login = g.user.login, project_id = project_id, full=True)
    project = Project.query.filter_by(login = g.user.login, id = project_id).first()
    log = read_log(login = g.user.login, project_id = project_id)
    return render_template('project/log.html', project = project,
        state = state, log = log)
