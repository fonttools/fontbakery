# coding: utf-8
try:
    import simplejson as json
except ImportError:
    import json

from flask import Blueprint, render_template, Response

from ..extensions import db, mail, pages

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def splash():
    return render_template('splash.html')

@frontend.route('/docs/<path:path>/', endpoint='page')
def page(path):
    _page = pages.get_or_404(path)
    return render_template('page.html', page=_page)

@frontend.route('/quicksearch', methods=['GET', 'POST'])
def quicksearch():
    return Response(json.dumps(['xen/font', 'dave/font', 'xen/font2']))