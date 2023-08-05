#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
#                                                                              
# PyGithub is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.                                                           
#                                                                              
# PyGithub is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS   
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#                                                                      
# You should have received a copy of the GNU Lesser General Public License
# along with PyGithub. If not, see <http://www.gnu.org/licenses/>.

import api_exceptions
import datetime

class _NotSetType:
    def __repr__(self):
        return "NotSet"

    value = None
NotSet = _NotSetType()

class _ValuedAttribute:
    def __init__(self, value):
        self.value = value

class _BadAttribute:
    def __init__(self, value, expectedType, exception=None):
        self.__value = value
        self.__expectedType = expectedType
        self.__exception = exception

    @property
    def value(self):
        raise api_exceptions.BadAttributeException(self.__value, self.__expectedType)

class ApiObject(object):

    def __init__(self, requester, headers, attributes):
        self._requester = requester
        self._initAttributes() # virtual
        self._storeAndUseAttributes(headers, attributes)
    
    def _storeAndUseAttributes(self, headers, attributes):
        # Make sure headers are assigned before calling _useAttributes
        # (Some derived classes will use headers in _useAttributes)
        self._headers = headers
        self._rawData = attributes
        self._useAttributes(attributes) # virtual

    @staticmethod
    def __makeSimpleAttribute(value, type):
        if value is None or isinstance(value, type):
            return _ValuedAttribute(value)
        else:
            return _BadAttribute(value, type)

    @staticmethod
    def _makeStringAttribute(value):
        return ApiObject.__makeSimpleAttribute(value, (str, unicode))

    @staticmethod
    def _makeIntAttribute(value):
        return ApiObject.__makeSimpleAttribute(value, (int, long))

    @staticmethod
    def _makeBoolAttribute(value):
        return ApiObject.__makeSimpleAttribute(value, bool)

    @staticmethod
    def _makeFloatAttribute(value):
        try:
            value = float(value)
        except ValueError:
            pass
        return ApiObject.__makeSimpleAttribute(value, float)

    @staticmethod
    def _makeDatetimeAttribute(value):
        try:
            d = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            d = datetime.datetime.strptime(value, "%Y-%m-%d")
        return ApiObject.__makeSimpleAttribute(d, datetime.datetime)

    @property
    def raw_data(self):
        """
        :type: dict
        """
        return self._rawData

    @property
    def raw_headers(self):
        """
        :type: dict
        """
        return self._headers

    def update(self):

        status, responseHeaders, output = self._requester.requestJson(
             self._resource_uri.value # virtual
        )

        headers, data = self._requester._Requester__check(status, responseHeaders, output)
        self._storeAndUseAttributes(headers, data)
    
