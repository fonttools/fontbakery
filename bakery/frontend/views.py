# coding: utf-8
try:
    import simplejson as json
except ImportError:
    import json

from flask import Blueprint, render_template, Response, g, flash, request, url_for, redirect
from flask.ext.babel import gettext as _

from ..decorators import login_required
from ..extensions import pages
from ..project.models import Project
from ..tasks import check_yaml, project_state_get

frontend = Blueprint('frontend', __name__)

@frontend.before_request
def before_request():
    if g.user:
        g.projects = Project.query.filter_by(login=g.user.login).all()

@frontend.route('/')
def splash():
    if g.user is None:
        return render_template('splash.html')
    else:
        projects = Project.query.filter_by(login=g.user.login).all()
        repos = []
        for i in projects:
            repos.append({
                'id': i.id,
                'clone': i.clone,
                'yaml': check_yaml(login = g.user.login, project_id = i.id),
                'state': project_state_get(login = g.user.login, project_id = i.id)
                })

        return render_template('dashboard.html', repos = repos)

@frontend.route('/docs/', defaults={'path': 'about'})
@frontend.route('/docs/<path:path>/', endpoint='page')
def page(path):
    _page = pages.get_or_404(path)
    return render_template('page.html', page=_page)

@frontend.route('/quicksearch', methods=['GET', 'POST'])
def quicksearch():
    return Response(json.dumps(['xen/font', 'dave/font', 'xen/font2']))