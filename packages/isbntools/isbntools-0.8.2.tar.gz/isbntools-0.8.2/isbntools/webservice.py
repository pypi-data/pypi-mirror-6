#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import gzip
from StringIO import StringIO

UA = 'webservice (gzip)'


class WEBQuery(object):
    """
    Class to query web services 
    """

    def __init__(self, url, user_agent=UA):
        """
        Constructor
        """
        headers = {'Accept-Encoding': 'gzip', 'User-Agent': user_agent}
        request = urllib2.Request(url, headers=headers)
        try:
            self.response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            raise Exception('Error:%s' % e.code)
        except urllib2.URLError as e:
            raise Exception('Error:%s' % e.reason)

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


def query(url, user_agent=UA):
        """
        Query to a web service
        """
        service = WEBQuery(url, user_agent=UA)
        return service.data()
