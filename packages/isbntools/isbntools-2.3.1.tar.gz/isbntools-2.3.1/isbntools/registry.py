#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .dev import wcat
from .dev import goob
from .dev import merge
from .dev import isbndb
from .dev import openl


"""
Config file for metadata services
"""
services = {'default': merge.query,      # <-- mandatory
            'wcat': wcat.query,
            'goob': goob.query,
            'merge': merge.query,
            'isbndb': isbndb.query,
            'openl': openl.query,
            }


def setdefaultservice(service_name):
    """
    Sets the default service
    """
    global services
    services['default'] = services[service_name]
