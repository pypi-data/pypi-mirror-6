# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
from dateutil.parser import parse as datetimeparse
from silva.app.news.datetimeutils import local_timezone

def set(content, name, attrs, extract=None, ns=None):
    ns_name = (ns, name)
    if attrs.has_key(ns_name):
        value = attrs[ns_name]
        if len(value):
            # If we got an empty string, we just ignore the value.
            if extract is not None:
                value = extract(value)
            setter = getattr(content, "set_%s" % name)
            setter(value)
            return value

def set_as_list(content, name, attrs, ns=None, sep=","):
    return set(
        content, name, attrs, ns=ns, extract=lambda x: x.split(sep))

def set_as_bool(content, name, attrs, ns=None):
    return set(
        content, name, attrs, ns=ns, extract=lambda x: x == 'True' or x == '1')

def set_as_int(content, name, attrs, ns=None):
    return set(content, name, attrs, ns=ns, extract=lambda x: int(x))

def set_as_datetime(content, name, attrs, ns=None, tz=None):
    def extract(value):
        if value == '':
            return None
        dt = datetimeparse(value)
        if tz:
            dt = dt.astimezone(tz)
        return dt

    return set(content, name, attrs, ns=ns, extract=extract)

def set_as_naive_datetime(content, name, attrs, ns=None):
    def extract(value):
        if value == '':
            return None
        dt = datetimeparse(value).astimezone(
            local_timezone).replace(tzinfo=None)
        return dt
    return set(content, name, attrs, ns=ns, extract=extract)


