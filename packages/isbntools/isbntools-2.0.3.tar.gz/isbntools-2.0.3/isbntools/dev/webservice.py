#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import urllib
import urllib2
import gzip
from StringIO import StringIO
from .exceptions import WSHTTPError, WSURLError

UA = 'webservice (gzip)'

logger = logging.getLogger(__name__)


class WEBQuery(object):
    """
    Class to query web services
    """

    def __init__(self, url, user_agent=UA, values=None):
        """
        Initializer (KISS without subclassing urllib2.BaseHandler!)
        """
        # headers to accept gzipped content
        headers = {'Accept-Encoding': 'gzip', 'User-Agent': user_agent}
        # if 'data' it does a PUT request (data must be urlencoded)
        if values:
            data = urllib.urlencode(values)
        else:
            data = None
        request = urllib2.Request(url, data, headers=headers)
        try:
            self.response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            logger.critical('WSHTTPError for %s with code %s' %
                            (url, e.code))
            raise WSHTTPError(e.code)
        except urllib2.URLError as e:
            logger.critical('WSURLError for %s with  reason %s' %
                            (url, e.reason))
            raise WSURLError(e.reason)

    def data(self):
        """
        Returns the uncompressed data
        """
        if self.response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(self.response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            data = self.response.read()
        return data


def query(url, user_agent=UA, values=None):
        """
        Query to a web service
        """
        service = WEBQuery(url, user_agent, values)
        return service.data()
