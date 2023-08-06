#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
from . import webservice
from .exceptions import DataNotFoundAtServiceError, ServiceIsDownError

UA = 'isbntools (gzip)'

OUT_OF_SERVICE = 'Temporarily out of service'
BOOK_NOT_FOUND = 'No results match your search'

logger = logging.getLogger(__name__)


class WEBQuery(object):
    """
    Base class to query a webservice and parse the result to py objects
    """

    def __init__(self, service_url, ua=UA):
        """
        Initializer & call webservice
        """
        self.url = service_url
        self.data = webservice.query(service_url, ua)

    def check_data(self, data_checker=None):
        """
        Checks the data & handle errors
        """
        if data_checker:
            return data_checker(self.data)
        if self.data == '{}':
            logger.warning('DataNotFoundAtServiceError for %s' % self.url)
            raise DataNotFoundAtServiceError(self.url)
        if BOOK_NOT_FOUND in self.data:
            logger.warning('DataNotFoundAtServiceError for %s' % self.url)
            raise DataNotFoundAtServiceError(self.url)
        if OUT_OF_SERVICE in self.data:
            logger.critical('ServiceIsDownError for %s' % self.url)
            raise ServiceIsDownError(self.url)

    def parse_data(self, parser=json.loads):
        """
        Parse the data (default JSON -> PY)
        """
        return parser(self.data)   # <-- data is now unicode
