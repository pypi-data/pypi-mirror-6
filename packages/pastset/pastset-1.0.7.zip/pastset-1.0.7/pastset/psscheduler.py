#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# psscheduler - runs all server components and schedules tasks to workers
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

"""Runs global name server, PastSet core server and schedules global PastSet
tasks to available workers"""

import logging
import os
import subprocess
import sys
import time

import pastset
import psbase


def usage():
    "Usage help"
    print '''Usage %s
%s''' % (sys.argv[0], psbase.settings_doc())

def register_clients(pset, conf, client_set, work_qs, count):
    """Wait for count new clients to register in client_set element and add
    each of them to work_qs mapping from worker IDs to corresponding job
    queue.
    """
    logging.debug("register %d pending clients" % count)
    new_size = len(work_qs) + count
    while len(work_qs) < new_size:
        logging.debug("waiting for %d more client(s)" % \
                     (new_size - len(work_qs)))
        specs = client_set.observe()
        (psid, host, system, arch, cores, mem, disk, bench) = specs
        if work_qs.has_key(psid):
            raise Exception("duplicate client registration: %s!" % psid)
        logging.info("signing up client %s %s" % (psid, specs[1:]))
        work_qs[psid] = pset.enter((psid, str, str))
    return work_qs

def load_balancer(pset, conf):
    """Load balance tasks among clients - waits for requested number of
    clients to sign in before handing out work.
    """

    workers = {}
    clients = pset.enter(('__clients', str, str, str, int, int, int, float))
    available = pset.enter(('__jobreq', str))
    jobs = pset.enter(('__jobs', str, str, str))

    # Wait for pswaitprocs workers to check in before proceeding

    register_clients(pset, conf, clients, workers, conf['pswaitprocs'])
    logging.info("at least %d client(s) ready - begin scheduling" % \
                 conf['pswaitprocs'])

    # Schedule jobs to workers while still accepting any pending new clients
    # if psprocs > pswaitprocs.
    
    while True:
        next = available.observe()
        if not workers.has_key(next):

            # Request from new client - handle all pending registrations first
            # and assert next is in workers then

            pending_clients = clients.last() - clients.first()
            register_clients(pset, conf, clients, workers, pending_clients)
        job = jobs.observe()
        if job[0] == '__HALT':
            logging.info("received halt request")

            # Handle any pending registrations first - limit race for fast apps

            pending_clients = clients.last() - clients.first()
            register_clients(pset, conf, clients, workers, pending_clients)
            for w in workers.keys():
                workers[w].move(('__HALT', ''))
            return
        else:
            logging.info("scheduling task for worker %s" % next)
            workers[next].move((job[0], job[1]))

def main(conf):
    """Run name server, core server and load balancer"""
    psbase.init_logging(conf, logging)
    logging.debug("starting")
    for msg in psbase.extract_warnings(conf):
        logging.warn(msg)

    # Check local installation
    
    try:
        server_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   'psserver.py')
        if not os.path.exists(server_path):
            raise Exception('No such server executable: %s' % server_path)
    except Exception, err:
        logging.error("failed to locate psserver: %s" % err)
        usage()
        sys.exit(1)

    # Use location independent path
    
    server_path = 'pypsserver'

    # Run pyro name server (pyro-ns) without wrapper script

    logging.info("starting name server")

    # Skip slow check for existing server

    ns_args = ['-r']
    
    # implicitly uses any PYRO_* environments

    pyro_ns = 'import Pyro.naming,sys; Pyro.naming.main(%s)' % ns_args
    logging.debug("name server command: %s" % \
                  (conf['pspython'].split() + ['-tt', '-c', pyro_ns]))
    name_server = subprocess.Popen(conf['pspython'].split() + \
                                   ['-tt', '-c', pyro_ns])

    # Now launch server and enable scheduler (automatically waits for ns)

    logging.debug("starting server")
    try:
        server = subprocess.Popen([server_path])
    except Exception, err:
        logging.error("caught unexpected exception: %s" % err)

    logging.debug("waiting for server")
    ps_ready = psbase.wait_for_pastset(conf)
    if ps_ready:
        try:
            pset = pastset.PastSet()
            logging.info("starting load balancer")
            load_balancer(pset, conf)
        except KeyboardInterrupt:
            logging.info('received interrupt - shutting down')
        except Exception, err:
            logging.error("caught unexpected exception: %s" % err)
        
        time.sleep(3)
    else:
        logging.error("gave up locating pastset - server not running?")
        
    psbase.graceful_exit({'server': server, 'name_server': name_server})
    

if __name__ == '__main__':

    # Default settings - with environment overrides

    conf = psbase.load_settings()
    main(conf)
