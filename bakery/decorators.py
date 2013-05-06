# -*- coding: utf-8 -*-

import collections
from functools import wraps, partial
from flask import g, request, redirect, url_for

def login_required(f):
    """ Decorator allow to access route only logged in user """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
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