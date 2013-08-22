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

from functools import wraps
from flask import g, request, redirect, url_for, flash
from flask.ext.babel import gettext as _

def login_required(f):
    """ Decorator allow to access route only logged in user. Usage:

        @project.route('/test', methods=['GET'])
        @login_required
        def test():
            return "You are logged in"

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash(_('Login required'))
            return redirect(url_for('gitauth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def cached(obj):
    cache = obj.cache = {}

    @wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer

class lazy_property(object):
    """
    lazy descriptor. Compute value of the propery on the first call. Usage:

    class Demo:

        @lazy_property
        def slow_method(self):
            import time
            time.sleep(5)
            return "I can be fast"


    c = Demo()
    # on 1st call will wait 5 seconds
    print(c.slow_method)
    # this loop will be very fast
    for i in range(1, 100):
        len(c.slow_method)

    """

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value
