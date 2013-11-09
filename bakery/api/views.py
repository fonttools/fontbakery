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

import logging
from flask import Blueprint, request, json
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

