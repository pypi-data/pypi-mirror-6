#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from . import config
from .registry import services
from .exceptions import NotRecognizedServiceError

# socket timeout is not exposed at urllib2 level so I had to import the
# module and set a default value for all the sockets (timeout in seconds)
# however this should be done at top level due to strong side effects...
socket.setdefaulttimeout(config.SOCKETS_TIMEOUT)


def query(isbn, service='default'):
    """
    Queries worldcat.org, Google Books (JSON API), ... for metadata
    """
    if service != 'default' and service not in services:
        raise NotRecognizedServiceError(service)
    return services[service](isbn)
