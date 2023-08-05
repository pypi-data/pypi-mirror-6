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

class PaginatedList():

    def __init__(self, contentClass, requester, uri, parameters=None):

        self.__requester = requester
        self.__contentClass = contentClass
        self.__uri = uri
        self.__parameters = parameters
        
        self.__getFirstPage()

    def __iter__(self):
        
        for element in self.__elements:
            yield self.__contentClass(
                    self.__requester, self.__headers, element)
        while self.__next:
            self.__getNextPage()
            for element in self.__elements:
                yield self.__contentClass(
                    self.__requester, self.__headers, element)
    
    def __getFirstPage(self):
        
        headers, data = self.__requester.requestJsonAndCheck(
                self.__uri,
                self.__parameters
        )

        self.__parse(headers, data)
    
    def __getNextPage(self):

        headers, data = self.__requester.requestJsonAndCheck(
                self.__next
        )

        self.__parse(headers, data)

    def __parse(self, headers, data):

        self.__headers = headers
        meta = data["meta"]
        self.__limit = meta["limit"]
        self.__next = meta["next"]
        self.__offset = meta["offset"]
        self.__previous = meta["previous"]
        self.__total_count = meta["total_count"]
        self.__elements = data["objects"]
