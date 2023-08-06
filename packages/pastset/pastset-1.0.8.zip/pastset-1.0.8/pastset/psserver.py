#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# psserver - core server holding tuple space elements and tasks
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

"""Core PastSet server holding global tuple space elements and task queue"""

import logging
import sys
import Pyro.core
import Pyro.naming

import pastset.element
import psbase


def Element(template, xfunction, conf):
    """Actual PastSet element implementation grouping tuples with same
    tuple template into one tuple space. This is the public interface with
    support for an Xfunction to filter tuples during PastSet operations.

    Automatically adds PSBIN environment to python module load path before
    loading any Xfunctions.
    """

    if not xfunction:
        return pastset.element.Element(template)

    try:
        if not conf['psbin'] in sys.path:
            sys.path.append(conf['psbin'])

        xfunc = __import__(xfunction)
    except Exception, err:
        msg = 'Unable to import Xfunction (module path: %s): %s' % (err,
                                                                    sys.path)
        logging.error("server: %s" % msg)
        raise Exception(msg)

    if not xfunc.__dict__.has_key('Element'):
        msg = 'Xfunction %s does not implement Element' % xfunction
        logging.error(msg)
        raise Exception(msg)

    return xfunc.Element(template)


class MainPastSet:

    """Main set hosting actual tuple space elements"""

    def __init__(self, conf):
        self.__elements = {}
        self.__conf = conf

    def enter(self, template, xfunction):
        """Create or subscribe to tuple space element identified by a given
        tuple template"""

        if not self.__elements.has_key(template) \
            or self.__elements[template].__dict__.has_key('is_ghost'):
            logging.info('adding element: %s' % (template, ))
            self.__elements[template] = Element(template, xfunction,
                                                self.__conf)

        return self.__elements[template]


class PastSet(Pyro.core.ObjBase):

    """PastSet object implementation"""

    def __init__(self, pset):
        Pyro.core.ObjBase.__init__(self)
        self.__pset = pset
        self.__elements = {}

    def enter(self, template, xfunction):
        """Create or subscribe to tuple space element identified by a tuple
        template.
        Tuple operations use xfunction variable to automatically filter tuples
        going in and out of elements.
        """

        self.__elements[template] = self.__pset.enter(template, xfunction)
        return template

    def delelement(self, template):
        """Delete an entire element"""

        if not self.__elements.has_key(template):
            raise Exception('Unable to delete non-existing element.')

        logging.info('Server removing element: %s' % (template, ))
        self.__elements[template] = pastset.element.GhostElement()

    def move(self, element, data):
        """Append data tuple to tuple space element"""

        logging.debug('Server moving tuple')
        return self.__elements[element].move(data)

    def observe(self, element, index):
        """Observe unread tuple at postion given by index"""

        logging.debug('Server observing tuple %s' % index)
        return self.__elements[element].observe(index)

    def first(self, element):
        """Lookup index of next unread tuple"""

        logging.debug('Server calling first')
        return self.__elements[element].first()

    def last(self, element):
        """Lookup index of most recently inserted tuple"""

        logging.debug('Server calling last')
        return self.__elements[element].last()

    def delta(self, element, new=None):
        """Get or set delta i.e. number of allowed unread tuples"""

        logging.debug('Server calling delta')
        return self.__elements[element].delta(new)

    def axe(self, element, index):
        """Remove tuples older than index from element"""

        logging.info('Server axing from %d' % index)
        return self.__elements[element].axe(index)

    def template(self, element):
        """Lookup template of element"""

        return self.__elements[element].template()


def main(conf):
    """Run server"""
    psbase.init_logging(conf, logging)
    logging.debug("starting")
    for msg in psbase.extract_warnings(conf):
        logging.warn(msg)
    try:
        ns_ready = psbase.wait_for_ns(conf)
        if not ns_ready:
            err = "gave up locating name server - scheduler not running?"
            raise Exception(err)
        Pyro.core.initServer(banner=0)
        locator = Pyro.naming.NameServerLocator()
        # implicitly uses any PYRO_* environments
        name_server = locator.getNS()
        daemon = Pyro.core.Daemon()
        daemon.useNameServer(name_server)
        logging.info("init tuple space")
        pset = PastSet(MainPastSet(conf))
        
        # connect new object implementation
        
        daemon.connect(pset, 'PastSet')
        
        # enter the server loop.
        
        logging.info('"PastSet" object ready')
        daemon.requestLoop()
    except KeyboardInterrupt:
        logging.info('received interrupt - shutting down')
    except Exception, err:
        logging.error("caught unexpected exception: %s" % err)


if __name__ == '__main__':

    # Default settings - with environment overrides

    conf = psbase.load_settings()
    main(conf)
