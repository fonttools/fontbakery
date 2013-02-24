from flask import Blueprint, render_template

from ..extensions import db, mail

frontend = Blueprint('frontend', __name__, url_prefix='/')

@frontend.route('/')
def splash():
    return render_template('splash.html')


@frontend.route('/about')
def about():
    return render_template('splash.html')
