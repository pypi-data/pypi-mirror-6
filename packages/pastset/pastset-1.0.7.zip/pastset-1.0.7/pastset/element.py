#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# element - tuple space element
# Copyright (C) 2010-2011  The pypastset project lead by Brian Vinter
#
# This file is part of pypastset.
#
# pypastset is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pypastset is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# -- END_HEADER ---
#

"""PastSet tuple space element"""

import threading


class Element(object):

    """Actual PastSet element implementation grouping tuples with same
    tuple template into one tuple space"""

    def __init__(self, template):
        self.__template = template
        self.__first = 0
        self.__last = 0
        self.__delta = None
        self.__oldest = 0
        self.__data = {}
        self.__cond = threading.Condition()

    def __set_entry(self, index, data):
        """set element helper"""

        self.__data[index] = data

    def move(self, data):
        """Append data tuple to the tuple space. If the element has delta
        value defined this operation will block until the unread tuple
        sequence length is below delta.
        """

        self.__cond.acquire()
        while self.__delta and self.__last - self.__first \
            >= self.__delta:
            self.__cond.wait()
        self.__set_entry(self.__last, data)
        self.__cond.notifyAll()
        self.__last += 1
        self.__cond.release()
        return True

    def observe(self, req_index):
        """Read a tuple from the tuple space:
        Unindexed (req_index < 0): read the next previously unread tuple
        Indexed: read a specific tuple in the unread sequence
        If the requested index is higher than the index of the last available
        tuple this operation will block until enough tuples are inserted to
        fulfill the request.
        """

        if req_index > -1 and req_index < self.__oldest:
            raise Exception('Tuple has been deleted')

        self.__cond.acquire()
        if req_index == -1:
            index = self.__first
        else:
            index = req_index
        while self.__last <= index:
            self.__cond.wait()
            if req_index == -1:
                index = self.__first
        result = self.__data[index]
        if req_index == -1:
            self.__first += 1
        self.__cond.notifyAll()
        self.__cond.release()
        return result

    def first(self):
        """Lookup index of next unread tuple"""

        return self.__first

    def last(self):
        """Lookup index of most recently inserted tuple"""

        return self.__last

    def delta(self, value=None):
        """Get or set delta i.e. allowed number of unread tuples"""

        if value != None:
            if value < 0:
                self.__delta = 0
            else:
                self.__delta = value
            self.__cond.notifyAll()
        return self.__delta

    def axe(self, index):
        """Mark tuples before given index ready for garbage collection"""

        self.__cond.acquire()
        i = min(self.__first - 1, index - 1)
        self.__oldest = max(self.__oldest, i)
        while self.__data.has_key(i):
            del self.__data[i]
            i -= 1
        self.__cond.notifyAll()
        self.__cond.release()

    def template(self):
        """Return element template"""

        return self.__template


class GhostElement(object):

    """Wrapper to replace element with an exception raising element
    after a delelement"""

    is_ghost = True

    def __init__(self):
        pass

    def __raise(self):
        raise Exception('Element has been deleted')

    def __set_entry(self, index, data):
        self.__raise()

    def move(self, data):
        """ghost operation to catch illegal access to deleted elements"""

        self.__raise()

    def observe(self, req_index):
        """ghost operation to catch illegal access to deleted elements"""

        self.__raise()

    def first(self):
        """ghost operation to catch illegal access to deleted elements"""

        self.__raise()

    def last(self):
        """ghost operation to catch illegal access to deleted elements"""

        self.__raise()

    def delta(self, value=None):
        """ghost operation to catch illegal access to deleted elements"""

        self.__raise()

    def template(self):
        """ghost operation to catch illegal access to deleted elements"""

        self.__raise()

    def axe(self, index):
        """ghost operation to catch illegal access to deleted elements"""

        self.__raise()
