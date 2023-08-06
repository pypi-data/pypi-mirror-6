#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# psclient - client worker running tasks repeatedly
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

"""PastSet client worker: keeps handling tasks from the global PastSet task
queue until it is told to halt"""

import logging
import os
import platform
import random
import subprocess
import sys
import time

import pastset
import psbase


def usage():
    "Usage help"
    print '''Usage %s
%s''' % (sys.argv[0], psbase.settings_doc())

def cpu_cores():
    """Detect number of available CPU cores"""
    try:
        import multiprocessing
        cores = multiprocessing.cpu_count()
    except:
        try:
            cores = int(os.sysconf("SC_NPROCESSORS_ONLN"))
        except:
            try:
                cores = int(os.environ["NUMBER_OF_PROCESSORS"])
            except:
                cores = 1
    return max(1, cores)

def benchmark():
    """Run short benchmark to estimate client performance"""
    # TODO: use e.g. fast pystone benchmark instead 
    bench_time = -time.time()
    checksum = 0
    for i in xrange(10000):
        checksum += 1.0*i*i/(i+1)
    bench_time += time.time()
    return 1.0/bench_time

def client_specs():
    """Extract client specs for this particular host"""
    (host, system, arch) = 3 * ["unknown"]
    try:
        (system, host, _, _, arch, _) = platform.uname()
    except:
        pass
    # Mem and disk sizes are measured in megabytes
    (cores, mem, disk, bench) = 1, 1024, 16*1024, 100.0
    cores = cpu_cores()
    # TODO: estimate or improve mem and disk defaults
    bench = benchmark()
    return (host, system, arch, cores, mem, disk, bench)

def main(conf):
    """Run client"""

    psbase.init_logging(conf, logging)
    logging.debug("starting")
    for msg in psbase.extract_warnings(conf):
        logging.warn(msg)
    ps_ready = psbase.wait_for_pastset(conf)
    if not ps_ready:
        logging.error("gave up locating pastset - server not running?")
        sys.exit(1)
    pset = pastset.PastSet()
    logging.debug("got pastset handle")
    psid = str(random.random())
    # Register clients with psid, host, system, cores, mem, disk, bench 
    clients = pset.enter(('__clients', str, str, str, int, int, int, float))
    token = pset.enter(('__jobreq', str))
    jobs = pset.enter((psid, str, str))
    (host, system, arch, cores, mem, disk, bench) = client_specs()
    logging.info("register with ID %s (%s %s %s %d %d %d %f)" % \
                 (psid, host, system, arch, cores, mem, disk, bench))
    clients.move((psid, host, system, arch, cores, mem, disk, bench))
    app = None
    
    while True:
        token.move(psid)
        result = jobs.observe()
        (cmd, args) = result
        if cmd == '__HALT':
            logging.debug("%s received halt" % psid)
            break

        try:
            app_path = os.path.realpath(os.path.join(conf['psbin'], cmd))
            if not os.path.exists(app_path):
                raise OSError('No such file: %s' % app_path)
        except Exception, err:
            logging.error("%s unable to locate application: %s : %s" % \
                          (psid, cmd, err))
            usage()
            continue

        logging.debug("%s launching %s" % (psid, app_path))
        app = subprocess.Popen(conf['pspython'].split() + [app_path] + args)
        # Dummy poll to make sure app starts
        __ = app.poll()
        # We do not wait here as each node may be able to handle multiple apps
    logging.info("%s shutting down" % psid)


if __name__ == '__main__':

    # Default settings - with environment overrides

    conf = psbase.load_settings()
    main(conf)
