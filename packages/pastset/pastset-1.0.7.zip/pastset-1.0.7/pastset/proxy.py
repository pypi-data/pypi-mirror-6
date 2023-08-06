#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# proxy - proxy for clients to access global tuple space elements and tasks
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

"""Client proxy used to access PastSet tuple space elements and tasks"""

import time
import Pyro.core


class Element:

    """PastSet tuple space element proxy"""

    def __init__(self, pset, element):
        self.__pset = pset
        self.__element = element

    def observe(self, index=-1):
        """Read a tuple from the tuple space:
        Unindexed (default or index < 0): read the next previously unread tuple
        Indexed: read a specific tuple in the unread sequence
        If the requested index is higher than the index of the last available
        tuple this operation will block until enough tuples are inserted to
        fulfill the request.
        """

        try:
            return self.__pset.observe(self.__element, index)
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

    def move(self, data):
        """Append data tuple to the tuple space. If the element has delta
        value defined this operation will block until the unread tuple
        sequence length is below delta.
        """

        try:
            return self.__pset.move(self.__element, data)
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

    def first(self):
        """Lookup index of next unread tuple"""

        try:
            return self.__pset.first(self.__element)
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

    def last(self):
        """Lookup index of most recently inserted tuple"""

        try:
            return self.__pset.last(self.__element)
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

    def delta(self, new=None):
        """Get or set delta i.e. allowed number of unread tuples"""

        try:
            return self.__pset.delta(self.__element, new)
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

    def axe(self, index):
        """Remove tuples older than index"""

        try:
            return self.__pset.axe(self.__element, index)
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

    def template(self):
        """Lookup template og element"""

        try:
            return self.__pset.template(self.__element)
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)


class PastSet:

    """PastSet proxy - returns a handle to the global PastSet which may
    subsequently be used to manage tasks and access tuple space elements.
    """

    def __init__(self):
        try:            
            self.__pset = Pyro.core.getProxyForURI('PYRONAME://PastSet')
        except Exception, err:
            raise Exception('PastSet error, unable to connect to server: %s'
                             % err)

        try:
            self.__jobs = self.enter(('__jobs', str, str, str))
        except Exception, err:
            raise Exception('PastSet error (shutdown while initializing?): %s'
                             % err)

    def spawn(self, app, args):
        """Spawn a task running app with command args"""

        try:
            if isinstance(args, list) or isinstance(args, tuple):
                args = [str(i) for i in args]
            else:
                args = [str(args)]
            self.__jobs.move((app, args, time.asctime()))
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

    def halt(self):
        """Signal no more tasks"""

        try:
            self.__jobs.move(('__HALT', '', time.asctime()))
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

    def enter(self, template, xfunction=None):
        """Create or subscribe to tuple space element identified by given
        tuple template. xfunction is an optional custom Element implementation
        to pre- and post-process tuples.
        """

        try:
            elem = Element(self.__pset, self.__pset.enter(template,
                                                          xfunction))
        except Exception, err:
            raise Exception('PastSet error (shutdown happened?): %s'
                            % err)

        return elem

    def delelement(self, element):
        """Unsubribe from and delete tuple space element"""

        if type(element) != tuple:
            element = element.template()

        self.__pset.delelement(element)


