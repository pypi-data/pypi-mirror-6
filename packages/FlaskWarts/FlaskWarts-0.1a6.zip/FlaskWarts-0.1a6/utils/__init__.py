from __future__ import unicode_literals, print_function

import re

from flask import current_app

__all__ = ['import_object', 'decamelize']


CAP_RE = re.compile(r'((?:^[a-z]|[A-Z])[a-z0-9]+)')


def import_object(s):
    """ Import an object from given string """
    import_path, name = s.rsplit('.', 1)
    name = str(name)
    module = __import__(import_path, fromlist=[name])
    try:
        return getattr(module, name)
    except AttributeError:
        raise ImportError('Could not import %s from %s' % (import_path, name))


def decamelize(s):
    """ Decamelizes a string """
    return '_'.join([s.lower() for s in CAP_RE.findall(s)])


def conf(name, default=None):
    return current_app.config.get(name, default)
