# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash, g

from ..extensions import github
from ..decorators import login_required

settings = Blueprint('settings', __name__, url_prefix='/settings')

@login_required
@settings.route('/', methods=['GET', 'POST'])
def repos():
    _repos = None
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            _repos = resp.data
        else:
            flash('Unable to load repos list.')
    return render_template('settings/repos.html', repos=_repos)

