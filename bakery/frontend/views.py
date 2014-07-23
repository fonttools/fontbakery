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

from flask import (Blueprint, render_template, g, request,
                   current_app, send_from_directory, redirect)

from bakery.app import app, pages
from bakery.project.models import Project
from bakery.settings.models import FontStats, ProjectCache
from bakery.utils import get_directory_sizes


frontend = Blueprint('frontend', __name__)


@frontend.before_request
def before_request():
    # Add to global vars list of the projects owned by current user
    if g.user:
        g.projects = Project.query.filter_by(login=g.user.login).all()


def unique(ar, key):
    r = []
    ar2 = []
    for item in ar:
        if item[key] not in r:
            r.append(item[key])
            ar2.append(item)
    return ar2


@frontend.route('/')
def splash():
    # Splash page, if user is logged in then show dashboard
    if g.user is None:
        return render_template('splash.html')
    else:
        projects = Project.query.order_by(Project.id.desc())
        cache = ProjectCache.get_user_cache(g.user.login)
        if cache:
            import json
            _func = lambda x: {"url": x['git_url'], "name": x['full_name']}
            cache = json.dumps(unique(map(_func, cache.data), 'name'))
        else:
            cache = []

        datadir_sizes = get_directory_sizes(app.config['DATA_ROOT'])
        datadir_sizes = [{"key": item[0], "value": item[1]}
                         for item in datadir_sizes]
        return render_template('dashboard.html', repos=projects, cache=cache,
                               datadir_sizes=datadir_sizes)


@frontend.route('/docs/', defaults={'path': 'index'})
@frontend.route('/docs/<path:path>/', endpoint='page')
def page(path):
    # Documentation views
    _page = pages.get_or_404(path)
    return render_template('page.html', page=_page)


@frontend.route('/robots.txt')
def static_from_root():
    # Static items
    return send_from_directory(current_app.static_folder, request.path[1:])


@frontend.route('/data/<path:path>')
def data_from_root(path):
    return send_from_directory(current_app.config['DATA_ROOT'], path)


@frontend.route('/favicon.ico')
def favicon():
    # Static items
    return redirect('/static/favicons/favicon.ico')


@frontend.route('/stats')
def stats():
    # ensure user logged in
    if g.user is None:
        return render_template('splash.html')
    else:
        stats = FontStats.query.all()
        return render_template('stats.html', stats=stats)
