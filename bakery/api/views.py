# coding: utf-8
try:
    import simplejson as json
except ImportError:
    import json

from flask import Blueprint, render_template, Response

api = Blueprint('api', __name__)

@api.route('/webhook')
def splash():
    return render_template('splash.html')

