from __future__ import unicode_literals, print_function


def in_p(msg, cls='error'):
    return '<p><span class="%s">%s</span></p>' % (cls, msg)
