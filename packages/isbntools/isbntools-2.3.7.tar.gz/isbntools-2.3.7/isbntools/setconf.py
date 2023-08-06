#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ConfigParser
import socket
from . import config
from . import registry

# NOTE: THIS CODE RUNS ON IMPORT!

# defaults parameters are in config.py they can be overwritten in
# isbntools.conf at users's $HOME/.isbntools directory (UNIX)

# get defaults
SOCKETS_TIMEOUT = float(config.SOCKETS_TIMEOUT)
THREADS_TIMEOUT = float(config.THREADS_TIMEOUT)

try:
    # read conf file
    conf = ConfigParser.ConfigParser()
    if os.name == 'nt':
        conf.read([os.abortpath.join(os.getenv('APPDATA'),
                                     'isbntools/isbntools.conf')])
    else:
        conf.read(['/etc/isbntools/.isbntools.conf',
                   '/usr/local/.isbntools.conf',
                   '/usr/local/bin/.isbntools.conf',
                  os.path.expanduser('~/.isbntools.conf'),
                  os.path.expanduser('~/.isbntools/isbntools.conf')])

    if conf.has_section('SYS'):
        # get user defined values for timeouts
        SOCKETS_TIMEOUT = float(conf.get('SYS', 'SOCKETS_TIMEOUT'))
        THREADS_TIMEOUT = float(conf.get('SYS', 'THREADS_TIMEOUT'))

    if conf.has_section('SERVICES'):
        for o, v in conf.items('SERVICES'):
            if o.upper() == 'DEFAULT_SERVICE':
                registry.setdefaultservice(v)
                continue
            if 'api_key' in o:
                name = o[:-8]
                config.add_apikey(name, v)
            else:
                config.set_options(o.upper(), v)

    if conf.has_section('PLUGINS'):
        for o, v in conf.items('PLUGINS'):
            plugin = registry.load_plugin(o, v)
            if plugin:
                registry.add_service(o, plugin.query)

except:
    pass

# socket timeout is not exposed at urllib2 level so I had to import the
# module and set a default value for all the sockets (timeout in seconds)
# however this should be done at top level due to strong side effects...
socket.setdefaulttimeout(SOCKETS_TIMEOUT)
config.setthreadstimeout(THREADS_TIMEOUT)
