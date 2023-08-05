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

import api_objects

class Store(api_objects.ApiObject):

    @property
    def address(self):
        """
        :type: string
        """
        return self._address.value

    @property
    def address_raw(self):
        """
        :type: string
        """
        return self._address_raw.value

    @property
    def county(self):
        """
        :type: string
        """
        return self._county.value

    @property
    def hours_raw(self):
        """
        :type: string
        """
        return self._hours_raw.value

    @property
    def id(self):
        """
        :type: string
        """
        return self._id.value
    
    @property
    def key(self):
        """
        :type: int
        """
        return self._key.value
    
    @property
    def latitude(self):
        """
        :type: float
        """
        return self._latitude.value
    
    @property
    def longitude(self):
        """
        :type: float
        """
        return self._longitude.value

    @property
    def name(self):
        """
        :type: string
        """
        return self._name.value

    @property
    def phone(self):
        """
        :type: string
        """
        return self._phone.value

    @property
    def resource_uri(self):
        """
        :type: string
        """
        return self._resource_uri.value

    def _initAttributes(self):
        self._address = api_objects.NotSet
        self._address_raw = api_objects.NotSet
        self._county = api_objects.NotSet
        self._hours_raw = api_objects.NotSet
        self._id = api_objects.NotSet
        self._key = api_objects.NotSet
        self._latitude = api_objects.NotSet
        self._longitude = api_objects.NotSet
        self._name = api_objects.NotSet
        self._phone = api_objects.NotSet
        self._resource_uri = api_objects.NotSet

    def _useAttributes(self, attributes):
        if "address" in attributes:
            self._address = self._makeStringAttribute(attributes["address"])
        if "address_raw" in attributes:
            self._address_raw = self._makeStringAttribute(attributes["address_raw"])
        if "county" in attributes:
            self._county = self._makeStringAttribute(attributes["county"])
        if "hours_raw" in attributes:
            self._hours_raw = self._makeStringAttribute(attributes["hours_raw"])
        if "id" in attributes:
            self._id = self._makeStringAttribute(attributes["id"])
        if "key" in attributes:
            self._key = self._makeIntAttribute(attributes["key"])
        if "latitude" in attributes:
            self._latitude = self._makeFloatAttribute(attributes["latitude"])
        if "longitude" in attributes:
            self._longitude = self._makeFloatAttribute(attributes["longitude"])
        if "name" in attributes:
            self._name = self._makeStringAttribute(attributes["name"])
        if "phone" in attributes:
            self._phone = self._makeStringAttribute(attributes["phone"])
        if "resource_uri" in attributes:
            self._resource_uri = self._makeStringAttribute(attributes["resource_uri"])
