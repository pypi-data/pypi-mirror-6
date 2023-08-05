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

class ApiException(Exception):

    def __init__(self, status, data):
        super(ApiException, self).__init__(self)
        self.__status = status
        self.__data = data

    @property
    def status(self):
        """
        The status returned by the API
        """
        return self.__status

    @property
    def data(self):
        """
        The (decoded) data returned by the API
        """
        return self.__data

    def __str__(self):
        return str(self.status) + " " + str(self.data)

class BadAttributeException(Exception):
    """
    Exception raised when the API returns an attribute with the wrong type.
    """
    def __init__(self, actualValue, expectedType):
        self.__actualValue = actualValue
        self.__expectedType = expectedType

    @property
    def actual_value(self):
        """
        The value returned by the API
        """
        return self.__actualValue

    @property
    def expected_type(self):
        """
        The type expected
        """
        return self.__expectedType
