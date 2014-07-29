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
import os
import shutil

from flask.ext.babel import gettext as _
from flask import (Blueprint, render_template, request, flash, g, redirect,
                   url_for)
from giturlparse import parse

from bakery.app import github, db, app
from bakery.decorators import login_required
from bakery.github import GithubSessionAPI, GithubSessionException
from bakery.models import Project
from bakery.settings.models import ProjectCache


settings = Blueprint('settings', __name__, url_prefix='/settings')


@settings.route('/', methods=['GET'])
@login_required
def repos():
    # pylint:disable-msg=E1101
    cache = ProjectCache.get_user_cache(g.user.login)
    myprojects = Project.query.filter_by(
        login=g.user.login, is_github=True).all()
    mygit = Project.query.filter_by(login=g.user.login, is_github=False).all()

    p = {}
    if myprojects:
        for i in myprojects:
            p[i.full_name] = i
    # import ipdb; ipdb.set_trace()
    return render_template('settings/index.html',
                           cache=cache, projects=p, gitprojects=mygit)


@settings.route('/update', methods=['POST'])
@login_required
def update():
    """Update the list of the user's github repos"""
    if g.user is not None:
        if g.user.login != u'offline':
            _github = GithubSessionAPI(github, g.user.token)
            try:
                _repos = _github.get_repo_list()
                ProjectCache.refresh_repos(_repos, g.user.login)
                if _repos:
                    flash(_('Repositories refreshed.'))
            except GithubSessionException, ex:
                flash(ex.message)
        else:
            flash(_('Offline user has no Github account.'))
    else:
        flash(_('No user found.'))
    return redirect(url_for('settings.repos') + "#tab_massgithub")


@settings.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    auth = github.get_session(token=g.user.token)
    _repos = None
    if g.user is not None:
        resp = auth.get('/user/repos', data={'type': 'public'})
        if resp.status_code == 200:
            _repos = resp.json()
        else:
            flash(_('Unable to load repos list.'))
    return render_template('settings/index.html', repos=_repos)


@settings.route('/addclone', methods=['POST'])
@login_required
def addclone():
    # According url schemes here http://git-scm.com/docs/git-push it is
    # near impossibru to validate url, so just check if its length is > 10
    # (let it be 10)
    #
    # TODO in the future, use http://schacon.github.io/git/git-ls-remote.html to validate the URL string
    # http://stackoverflow.com/questions/9610131/how-to-check-the-validity-of-a-remote-git-repository-url
    #
    # TODO we could do very light validation that the form field is not 0 in JS
    # TODO we could do very light validation of the URL in JS

    clone = request.form.get('clone')
    if len(clone) == 0:
        flash(_('Enter a URL.'))
        return redirect(url_for('frontend.splash'))

    if not clone.lower().endswith('.git'):
        clone += '.git'  # quick fix to validate clone git url

    # pylint:disable-msg=E1101
    # user = ProjectCache.get_user_cache(g.user.login)

    dup = Project.query.filter_by(login=g.user.login,
                                  is_github=False, clone=clone).first()
    if dup:
        flash(_("This repository is a duplicate"))

    if not parse(clone).valid:
        flash(_("Problem parsing git url"))
        return redirect(url_for('settings.repos') + "#tab_massgithub")

    project = Project(login=g.user.login, clone=clone, is_github=False)

    # if (clone in map(lambda x: x['clone_url'], user.data)
    #         or clone in map(lambda x: x['git_url'], user.data)):
    #     pass

    if project:
        db.session.add(project)
        db.session.commit()

    flash(_("Repository successfully added"))
    project.sync()
    return redirect(url_for('frontend.splash'))


@settings.route('/delclone/<int:project_id>', methods=['POST'])
@login_required
def delclone(project_id):
    # pylint:disable-msg=E1101
    project = Project.query.filter_by(login=g.user.login,
                                      id=project_id).first()
    if not project:
        flash(_("Project not found."))
        return redirect(url_for('frontend.splash'))

    if request.form.get('remove-from-disk'):
        source_dir = '%s.in' % project.id
        build_dir = '%s.out' % project.id
        shutil.rmtree(os.path.join(app.config['DATA_ROOT'],
                                   g.user.login, source_dir))
        shutil.rmtree(os.path.join(app.config['DATA_ROOT'],
                                   g.user.login, build_dir))

    db.session.delete(project)
    db.session.commit()
    flash(_(("Repository %(pid)s succesfuly removed (but files remain"
             " on the server)"), pid=project_id))

    return redirect(url_for('frontend.splash'))


@settings.route('/massgit/', methods=['POST'])
@login_required
def massgit():
    git_ids = request.form.getlist('git')
    # pylint:disable-msg=E1101
    projects = Project.query.filter_by(
        login=g.user.login, is_github=True).all()

    pfn = {}
    for p in projects:
        if p.full_name not in git_ids:
            db.session.delete(p)
            flash(_(("Repository %(name)s successfully removed (but files"
                     " remain on the server)"), name=p.full_name))
        pfn[p.full_name] = p

    db.session.commit()
    for gid in git_ids:
        if not pfn.get(gid):
            project = Project(
                login=g.user.login,
                full_name=gid,
                # TODO: Use actual github clone string used by Github
                # clone='git@github.com:%s/%s.git' % (g.user.login, full_name),
                clone='git://github.com/%s.git' % gid,
                is_github=True
            )
            db.session.add(project)
            db.session.commit()
            flash(_("Repository successfully added"))
            project.sync()

    db.session.commit()
    return redirect(url_for('settings.repos') + "#tab_massgithub")


@settings.route('/batch', methods=['POST'])
@login_required
def batch():
    # pylint:disable-msg=E1101
    urls = request.form.get('urls', '') + "\n"  # this makes m
    n = 0
    for l in urls.split("\n"):
        l = l.strip()
        if not l:
            continue
        if not parse(l).valid:
            flash(_("Url %(url)s isn't accepted, parse error", url=l))
        else:
            dup = Project.query.filter_by(login=g.user.login,
                                          is_github=False, clone=l).first()

            if dup:
                flash(_("Url %(url)s is duplicate", url=l))
            else:
                project = Project(login=g.user.login, clone=l, is_github=False)

                if project:
                    db.session.add(project)
                    db.session.commit()
                    db.session.refresh(project)

                project.sync()

                n = n + 1

    flash(_("%(num)s repositories successfuly added", num=n))

    return redirect(url_for('settings.repos'))
