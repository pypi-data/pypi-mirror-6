from __future__ import unicode_literals, print_function

from functools import wraps

from flask import request, abort


def xhr_only(f):
    """ Abort handling if request is not made using XHR """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_xhr:
            return abort(400)
        return f(*args, **kwargs)
    return decorated_function
