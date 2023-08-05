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
import price
from requester import Requester

class Product(api_objects.ApiObject):

    @property
    def age(self):
        """
        :type: float
        """
        return self._age.value

    @property
    def bottles_per_case(self):
        """
        :type: int
        """
        return self._bottles_per_case.value

    @property
    def code(self):
        """
        :type: string
        """
        return self._code.value

    @property
    def created_at(self):
        """
        :type: datetime
        """
        return self._created_at.value
    
    @property
    def description(self):
        """
        :type: string
        """
        return self._description.value

    @property
    def id(self):
        """
        :type: string
        """
        return self._id.value

    @property
    def modified_at(self):
        """
        :type: datetime
        """
        return self._modified_at.value

    @property
    def on_sale(self):
        """
        :type: bool
        """
        return self._on_sale.value

    @property
    def proof(self):
        """
        :type: float
        """
        return self._proof.value
    
    @property
    def resource_uri(self):
        """
        :type: string
        """
        return self._resource_uri.value

    @property
    def size(self):
        """
        :type: string
        """
        return self._size.value

    @property
    def slug(self):
        """
        :type: string
        """
        return self._slug.value

    @property
    def status(self):
        """
        :type: string
        """
        return self._status.value

    @property
    def title(self):
        """
        :type: string
        """
        return self._title.value

    def get_price(self):

        headers, data = self._requester.requestJsonAndCheck(
            '/api/v1/price/' + str(self.id) + '/'
        )
        return price.Price(self._requester, headers, data)

    def _initAttributes(self):
        self._age = api_objects.NotSet
        self._bottles_per_case = api_objects.NotSet
        self._code = api_objects.NotSet
        self._created_at = api_objects.NotSet
        self._description = api_objects.NotSet
        self._id = api_objects.NotSet
        self._modified_at = api_objects.NotSet
        self._on_sale = api_objects.NotSet
        self._proof = api_objects.NotSet
        self._resource_uri = api_objects.NotSet
        self._size = api_objects.NotSet
        self._slug = api_objects.NotSet
        self._status = api_objects.NotSet
        self._title = api_objects.NotSet

    def _useAttributes(self, attributes):
        if "age" in attributes:
            self._age = self._makeFloatAttribute(attributes["age"])
        if "bottles_per_case" in attributes:
            self._bottles_per_case = self._makeIntAttribute(attributes["bottles_per_case"])
        if "code" in attributes:
            self._code = self._makeStringAttribute(attributes["code"])
        if "created_at" in attributes:
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "description" in attributes:
            self._description = self._makeStringAttribute(attributes["description"])
        if "id" in attributes:
            self._id = self._makeStringAttribute(attributes["id"])
        if "modified_at" in attributes:
            self._modified_at = self._makeDatetimeAttribute(attributes["modified_at"])
        if "on_sale" in attributes:
            self._on_sale = self._makeBoolAttribute(attributes["on_sale"])
        if "proof" in attributes:
            self._proof = self._makeFloatAttribute(attributes["proof"])
        if "resource_uri" in attributes:
            self._resource_uri = self._makeStringAttribute(attributes["resource_uri"])
        if "size" in attributes:
            self._size = self._makeStringAttribute(attributes["size"])
        if "slug" in attributes:
            self._slug = self._makeStringAttribute(attributes["slug"])
        if "status" in attributes:
            self._status = self._makeStringAttribute(attributes["status"])
        if "title" in attributes:
            self._title = self._makeStringAttribute(attributes["title"])
