from __future__ import unicode_literals, print_function

import re

from formencode.htmlfill_schemabuilder import (
    SchemaBuilder, to_bool, get_messages, force_list)
from formencode import validators
from formencode import compound
from formencode import htmlfill

integer_re = re.compile(r'^\d+?$')
float_re = re.compile(r'^\d+\.\d+$')


class ArgumentCleaningSchemaBuilder(SchemaBuilder):
    arg_separator = ':'
    v_separator = ';'

    def clean_arg(self, arg):
        """ Cleans argument values """
        if integer_re.match(arg):
            return int(arg)
        if float_re.match(arg):
            return float(arg)
        if arg in ('true', 'false', 'True', 'False'):
            return arg in ('true', 'True')
        if arg == 'None':
            return None
        return arg

    def parse_args(self, args_str):
        """ Parses the arguments string and builds args and kwargs """
        args = []
        kwargs = {}
        for a in args_str.split(self.arg_separator):
            if '=' in a:
                # If there's an exception in the next line, we just let that
                # propagate up to the caller since it's invalid to have more
                # than one '=' here.
                key, val = a.split('=')
                kwargs[key] = self.clean_arg(val)
            else:
                args.append(self.clean_arg(a))
        return args, kwargs

    def listen_input(self, parser, tag, attrs):
        get_attr = parser.get_attr
        name = get_attr(attrs, 'name')
        if not name:
            # @@: should warn if you try to validate unnamed fields
            return
        v = compound.All(validators.Identity())
        add_to_end = None
        # for checkboxes, we must set if_missing = False
        if tag.lower() == "input":
            type_attr = get_attr(attrs, "type").lower().strip()
            if type_attr == "submit":
                v.validators.append(validators.Bool())
            elif type_attr == "checkbox":
                v.validators.append(validators.Wrapper(to_python=force_list))
            elif type_attr == "file":
                add_to_end = validators.FieldStorageUploadConverter()
        message = get_attr(attrs, 'form:message')
        required = to_bool(get_attr(attrs, 'form:required', 'false'))
        if required:
            v.validators.append(
                validators.NotEmpty(
                messages=get_messages(validators.NotEmpty, message)))
        else:
            v.validators[0].if_missing = False
        if add_to_end:
            v.validators.append(add_to_end)
        v_types = get_attr(attrs, 'form:validate', None)
        if v_type:
            if self.arg_separator in v_type:
                parts = v_type.split(self.arg_separator)
                v_type = parts[0]
                v_args, v_kwargs = self.parse_args(parts[1:])
            else:
                v_args = []
                v_kwargs = {}
            v_type = v_type.lower()
            v_class = self.validators.get(v_type)
            if not v_class:
                raise ValueError("Invalid validation type: %r" % v_type)
            v_kwargs.update({'messages': get_messages(v_class, message)})
            v_inst = v_class(*v_args, **v_kwargs)
            v.validators.append(v_inst)
        self._schema.add_field(name, v)


def parse_schema(form):
    """
    Given an HTML form, parse out the schema defined in it and return
    that schema.
    """
    listener = ArgumentCleaningSchemaBuilder()
    p = htmlfill.FillingParser(
        defaults={}, listener=listener)
    p.feed(form)
    p.close()
    return listener.schema()
