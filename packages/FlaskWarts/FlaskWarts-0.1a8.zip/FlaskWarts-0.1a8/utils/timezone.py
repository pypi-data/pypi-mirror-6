from __future__ import unicode_literals, print_function

import datetime

import pytz


def in_zone(dt, zone_name='US/Eastern'):
    """ Give ``dt`` ``datetime`` instance in given zone """
    return pytz.timezone(zone_name).localize(dt)


def in_utc(dt):
    """ Returns ``datetime`` instance localized to UTC """
    return pytz.utc.localize(dt)


def utc_now():
    """ Return ``datetime`` instance for current time in UTC """
    return in_utc(datetime.datetime.now())


