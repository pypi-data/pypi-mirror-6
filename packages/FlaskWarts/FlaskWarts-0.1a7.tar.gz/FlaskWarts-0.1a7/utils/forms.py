from __future__ import unicode_literals, print_function

from formencode import htmlfill
from formencode.api import Invalid
from formencode.schema import Schema
from formencode.variabledecode import variable_decode
from flask import render_template, request, g
from werkzeug.datastructures import MultiDict

from .schemabuilder import parse_schema

__all__ = ['Form']


class Form(Schema):
    """ Class for handling form validation and rendering

    Note that this class is not a form *generator*. It's a wrapper around HTML
    templates that handle such tasks as validating user input and filling in
    form with data and error messages.

    This class is a subclass of ``formencode.schema.Schema``, and can be used
    as such. However, (by default) it can also obtain a valid schema from
    rendered template if it is marked up with ``schemabuilder``-compatible
    markup. This is the default behavior.
    """

    # Template associated with instance
    template_name = None

    # Whether we should automatically generate schema from the form or this
    # instance is already a shcema that can be used for validation
    auto_schema = True

    # Class to add to inputs on error
    form_error_class = 'field-error'

    # Parameter passed to the  template as `form_url`
    url = None

    # Parameter passeed to the template as `form_method`
    method = 'POST'

    # Parameter destructured and passed to the template as extra variables
    extras = {}

    def __init__(self, data={}, url=None, method=None, extras=None):
        self.url = url or self.url
        self.method = method or self.method
        self.extras = extras or self.extras
        self.errors = {}
        self.valid_data = {}
        if isinstance(data, MultiDict):
            data = variable_decode(data)
        self.data = data

    def get_form_url(self):
        if hasattr(self.url, '__call__'):
            return self.url()
        return self.url

    def get_form_method(self):
        if hasattr(self.method, '__call__'):
            return self.method()
        return self.method

    def get_extras(self):
        if hasattr(self.extras, '__call__'):
            return self.extras()
        return self.extras

    def render_base(self):
        return render_template(self.template_name,
                               form_url=self.get_form_url(),
                               form_method=self.get_form_method(),
                               **self.get_extras())

    def render(self):
        form = self.render_base()
        self.data['_csrf_token'] = g.csrf_token
        return htmlfill.render(form, defaults=self.data, errors=self.errors,
                               force_defaults=False,
                               error_class=self.form_error_class)

    def __str__(self):
        return self.render()

    def get_schema(self):
        form = self.render_base()
        schema = parse_schema(form)
        if hasattr(schema, '_csrf_token'):
            del schema._csrf_token
        return schema

    @property
    def is_valid(self):
        is_valid = False

        if self.auto_schema:
            schema = self.get_schema()
        else:
            schema = self

        try:
            self.valid_data = schema.to_python(self.data)
            is_valid = True
        except Invalid, err:
            self.errors = {k: v.encode('utf-8')
                           for k, v in err.unpack_errors().items()}
            self.valid_data = {}

        return is_valid

