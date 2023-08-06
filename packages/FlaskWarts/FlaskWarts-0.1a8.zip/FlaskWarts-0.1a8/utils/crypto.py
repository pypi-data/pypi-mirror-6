from __future__ import unicode_literals, print_function

import os
import hashlib
import re
from urlparse import urlparse

from . import conf


TOKEN_BYTES = 8
TOKEN_RE = re.compile(r'^[a-f0-9]{128}$')


class CsrfError(Exception):
    MISSING = 1
    NO_REFERER = 2
    WRONG_REFERER = 3
    MISMATCH = 4

    """ Raised on CSRF error """
    def __init__(self, msg, reason, *args, **kwargs):
        self.reason = reason
        super(CsrfError, self).__init__(msg, *args, **kwargs)


def random_hash(random_bytes=8):
    """ Returns a hexdigest of random number of bytes """
    sha512 = hashlib.sha512()
    sha512.update(os.urandom(random_bytes))
    return sha512.hexdigest()


def clean_csrf_token(token):
    """ Checks the CSRF token and returns a new one if dirty """
    try:
        token = unicode(token)
    except Exception:
        return random_hash(TOKEN_BYTES)
    if not TOKEN_RE.match(token):
        return random_hash(TOKEN_BYTES)
    return token


def same_origin(url1, url2):
    """ Checks two URLs for same origin

    This code is take from Django
    """
    p1, p2 = urlparse(url1), urlparse(url2)

    try:
        return (p1.scheme, p1.hostname, p1.port) == (p2.scheme, p2.hostname, p2.port)
    except ValueError:
        return False


def check_csrf_token(request, token, skip_same_origin=False):
    """ Checks token against the one stored in cookie """

    if request.method in ('GET', 'HEAD', 'OPTION', 'TRACE'):
        return

    referer = request.environ.get('HTTP_REFERER')

    if (not referer) and (not skip_same_origin):
        raise CsrfError('Missing HTTP_REFERER header',
                        reason=CsrfError.NO_REFERER)

    if (not same_origin(referer, request.url)) and (not skip_same_origin):
        raise CsrfError('Not same origin',
                        reason=CsrfError.WRONG_REFERER)

    if conf('CSRF_COOKIE_NAME', '_csrf_token') not in request.cookies:
        raise CsrfError('Missing CSRF token',
                        reason=CsrfError.MISSING)

    cookie_token = request.cookies.get(conf('CSRF_COOKIE_NAME', '_csrf_token'),
                                       '')

    # Stripping of the '=' character came about during testing using Werkzeug's
    # test client. Pretty sure we don't need to do this (and probably
    # shouldn't), but the way test client sets cookies in the jar is weird and
    # tests don't pass without this hack. It shouldn't matter under normal
    # circumstances.
    if cookie_token:
        cookie_token = cookie_token.strip('=')

    if clean_csrf_token(cookie_token) != clean_csrf_token(token):
        raise CsrfError('CSRF token mismatch', reason=CsrfError.MISMATCH)

    return True
