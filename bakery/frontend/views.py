# coding: utf-8
try:
    import simplejson as json
except ImportError:
    import json

from flask import Blueprint, render_template, Response

from ..extensions import db, mail

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def splash():
    return render_template('splash.html')

@frontend.route('/about')
def about():
    return render_template('splash.html')

@frontend.route('/docs')
def docs():
    return render_template('splash.html')

@frontend.route('/quicksearch', methods=['GET', 'POST'])
def quicksearch():
    return Response(json.dumps(['xen/font', 'dave/font', 'xen/font2']))