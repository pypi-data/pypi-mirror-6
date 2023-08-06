import logging
import re

from flask import (request, make_response, render_template, redirect, sessions,
                   abort, g, url_for)

from . import decamelize


__all__ = ['Route', 'METHODS', 'decamelize', 'RouteError', 'RouteConfigError']

METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
POST_ALIASES = ['PUT', 'PATCH', 'DELETE']



class RouteError(Exception):
    pass


class RouteConfigError(RouteError):
    pass


class Route(object):
    """ Generic REST route handler """

    path = '/'
    name = None
    decorators = []

    # A few objects attached as attributes for convenience
    request = request
    sessions = sessions
    g = g
    log = logging
    allow_overrides = True

    def __init__(self, app, args, kwargs):
        self.app = app
        self.args = args
        self.kwargs = kwargs

    def url_for(self, *args, **kwargs):
        return url_for(*args, **kwargs)

    def redirect(self, *args, **kwargs):
        return redirect(*args, **kwargs)

    def abort(self, *args, **kwargs):
        return abort(*args, **kwargs)

    def respond(self, *args, **kwargs):
        return make_response(*args, **kwargs)

    def method_not_allowed(self):
        resp = make_response('%s not allowed' % request.method)
        resp.status = '405'
        return resp

    def get_route_name(self):
        return self.name or decamelize(self.__class__.__name__)

    def on_dispatch(self):
        pass

    @classmethod
    def register(cls, app):
        endpoint_name = cls.name or decamelize(cls.__name__)
        methods = [v for v in METHODS if hasattr(cls, v)]

        logging.debug(
            'Registering route %s using name %s and methods %s' % (
                cls.path, endpoint_name, ', '.join(methods)))

        if cls.allow_overrides:
            make_post = lambda m: m in POST_ALIASES and 'POST' or m
            methods = list(set(map(make_post, methods)))

        def view_func(*args, **kwargs):
            logging.debug('View function called for %s' % endpoint_name)
            route = cls(app, args, kwargs)
            method_name = cls.get_method_name(request)
            method = getattr(route, method_name, None)
            if method is None:
                logging.debug(
                    'No suitable view method found for %s' % method_name)
                return route.method_not_allowed()
            route.on_dispatch()
            logging.debug('Calling %s with args %s and keyword args %s' % (
                method, args, kwargs))
            return method(*args, **kwargs)

        for decorator in cls.decorators:
            view_func = decorator(view_func)

        app.add_url_rule(cls.path, endpoint_name, view_func, methods=methods)

    @classmethod
    def get_method_name(cls, request):
        if cls.allow_overrides and request.method == 'POST':
            return request.form.get('_method', 'POST').upper()
        return request.method


class HtmlResponseMixin(object):
    """ Route handler that returns HTML response """

    template_name = None

    def get_template_name(self):
        """ Returns the name of the template to render """
        return self.template_name

    def get_context(self):
        """ Returns template context """
        return {}

    def render(self, context={}):
        """ Renders the template with provided context """
        ctx = self.get_context()
        ctx.update(context)
        return render_template(self.get_template_name(), **ctx)


class RedirectMixin(object):
    """ Mixin that handles redirects """

    redirect_url = None

    def get_redirect_url(self):
        if not self.redirect_url:
            raise RouteConfigError('No redirect url defined for '
                                   '%s' % self.get_route_name())
        return self.redirect_url

    def redirect(self, url=None):
        url = url or self.get_redirect_url()
        return redirect(url)


class FormMixin(object):
    """ Route handler mixin for handling forms """

    form_class = None
    form_defaults = {}
    form_url = None
    form_method = None
    form_extras = None

    def get_form_defaults(self):
        return self.form_defaults

    def get_form_url(self):
        return self.form_url

    def get_form_method(self):
        return self.form_method

    def get_form_extras(self):
        return self.form_extras

    def get_form_args(self):
        return dict(url=self.get_form_url(),
                    method=self.get_form_method(),
                    extras=self.get_form_extras())

    def get_form_class(self):
        if self.form_class is None:
            raise RouteConfigError('No form class defined for '
                                   '%s' % self.get_route_name())
        return self.form_class

    def get_form(self):
        form_class = self.get_form_class()
        if request.method == 'GET':
            return form_class(self.get_form_defaults(), **self.get_form_args())
        return form_class(request.form, **self.get_form_args())


class HtmlRoute(HtmlResponseMixin, Route):
    """ Route that returns a rendered template on GET request """

    def GET(self, *args, **kwargs):
        return self.render()


class FormRoute(HtmlResponseMixin, RedirectMixin, FormMixin, Route):
    """ Route handler that deals with forms """

    def GET(self, *args, **kwargs):
        self.form = self.get_form()
        return self.render()

    def POST(self, *args, **kwargs):
        self.form = form = self.get_form()
        if not form.is_valid:
            return self.form_invalid()
        return self.form_valid()

    def form_valid(self):
        return self.redirect()

    def form_invalid(self):
        return self.render()

    def get_context(self):
        return {'form': self.form}


class RedirectRoute(RedirectMixin, Route):
    """ Simple route that redirects """

    def before_redirect(self):
        pass

    def GET(self, *args, **kwargs):
        self.before_redirect()
        return self.redirect()
