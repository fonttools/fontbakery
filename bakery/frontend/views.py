# coding: utf-8
from flask import Blueprint, render_template

from ..extensions import db, mail

frontend = Blueprint('frontend', __name__, url_prefix='/')

@frontend.route('/')
def splash():
    return render_template('splash.html')

@frontend.route('/about')
def about():
    return render_template('splash.html')

@frontend.route('/docs')
def docs():
    return render_template('splash.html')
