from __future__ import unicode_literals, print_function

import logging

from flask import make_response, g, request, abort
from jinja2.filters import do_mark_safe

from . import crypto


EXCLUDED_METHODS = ['GET', 'OPTION', 'HEAD', 'TRACE']
MAXAGE = 24 * 60 * 60  # 24 hours


def set_cookie(response, token, token_cookie_name='_csrf_token',
               max_age=MAXAGE):
    """ Adds token cookie to response """
    response.set_cookie(token_cookie_name, token, max_age=max_age)


def token_tag(token, token_arg_name='_csrf_token'):
    """ Returns a HTML fragment for token input tag """
    return do_mark_safe(
        '<input type="hidden" name="%(name)s" value="%(token)s">' % {
            'name': token_arg_name,
            'token': token
        })


def check_token(arg_name='_csrf_token'):
    """ Extracts token from form and checks against token in the cookie

    This function does *not* trap any exceptions on its own.
    """
    form_token = request.form.get(arg_name)
    crypto.check_csrf_token(request, form_token)


def csrf(app, excluded_paths=[], abort_status=403):
    """ Add CSRF protection to app via before- and after-request hooks """

    token_name = app.config.get('CSRF_TOKEN_NAME', 'CSRF_TOKEN')
    token_arg_name = app.config.get('CSRF_ARG_NAME', '_csrf_token')
    token_maxage = app.config.get('CSRF_TOKEN_MAXAGE', 24 * 60 * 60)
    token_cookie_name = app.config.get('CSRF_COOKIE_NAME', '_csrf_token')

    @app.before_request
    def process_token():
        method_ok = request.method not in EXCLUDED_METHODS
        path_ok = request.path not in excluded_paths

        if method_ok and path_ok:
            try:
                check_token()
            except crypto.CsrfError, err:
                logging.error('CSRF verification failed: %s' % err)
                abort(abort_status)

        # Generate new token
        token = crypto.random_hash()
        g.csrf_token = app.jinja_env.globals['csrf_token'] = token
        g.csrf_tag = app.jinja_env.globals['csrf_tag'] = token_tag(
            token, token_arg_name)

    @app.after_request
    def set_token(response):
        if hasattr(g, 'csrf_token'):
            response.set_cookie(token_cookie_name, g.csrf_token,
                                max_age=token_maxage)
        return response

    return app


def formats(app):
    @app.before_request
    def add_formatting_tokens():
        g.date_format = app.config['DATE_FORMAT']

