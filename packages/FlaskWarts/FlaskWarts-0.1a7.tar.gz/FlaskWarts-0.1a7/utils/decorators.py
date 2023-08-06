from __future__ import unicode_literals, print_function

from functools import wraps

from flask import request, abort, make_response


def xhr_only(f):
    """ Abort handling if request is not made using XHR """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_xhr:
            return abort(400)
        return f(*args, **kwargs)
    return decorated_function


def nocache(f):
    """ Responds with no-cache cache-control header

    Original code by Armin Ronacher taken from:

    http://flask.pocoo.org/mailinglist/archive/2011/8/8/add-no-cache-to-response/#952cc027cf22800312168250e59bade4
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.cache_control.no_cache = True
        return response
    return decorated_function
