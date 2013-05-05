# coding: utf-8
try:
    import simplejson as json
except ImportError:
    import json

import logging
from flask import Blueprint, request
from ..extensions import db

api = Blueprint('api', __name__)

from .models import Task

@api.route('/webhook')
def splash():
    try:
        payload = json.loads(request.args.get('payload'))
    except ValueError:
        logging.warn('Error reciving webhook, cannt parse payload')

    task = Task(
        full_name = payload['repository']['url'][19:], # skip 'https://github.com/' part
        payload = payload,
        status = 0
        )
    db.session.add(task)
    db.session.commit()
    return "Ok"

