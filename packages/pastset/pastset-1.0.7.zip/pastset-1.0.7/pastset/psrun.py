#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# psrun - helper to run entire pastset environment and application
# Copyright (C) 2010-2012  The pypastset project lead by Brian Vinter
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

"""PastSet run helper to launch all PastSet components and then execute a user
supplied PastSet application"""

import logging
import os
import subprocess
import sys

import psbase


def usage():
    "Usage help"
    print '''Usage %s <executable>
%s''' % (sys.argv[0], psbase.settings_doc())

def main(conf):
    """Run all components and launch app"""
    psbase.init_logging(conf, logging)
    logging.debug("starting")
    for msg in psbase.extract_warnings(conf):
        logging.warn(msg)
    if not sys.argv[1:]:
        usage()
        sys.exit(1)

    app_args = sys.argv[2:]

    try:
        app = sys.argv[1]
        app_path = os.path.realpath(os.path.join(conf['psbin'], app))
        if not os.path.exists(app_path):
            raise OSError('No such file: %s' % app_path)
    except Exception, err:
        logging.error("failed to locate application %s: %s" % (app, err))
        usage()
        sys.exit(1)

    try:
        if conf['pshosts']:
            raw_hosts = open(conf['pshosts'], 'r').readlines()
        else:
            logging.warn('No PSHOSTS provided - only using localhost')
            raw_hosts = ['localhost']
    except Exception, err:
        logging.error('Unable to read hostfile: %s' % err)
        usage()
        sys.exit(1)

    hosts = []
    client_procs = int(conf['psprocs'])

    # Filter comments and white space

    for name in raw_hosts:
        name = name.split('#', 1)[0].strip()
        if name:
            hosts.append(name)
    if client_procs != len(hosts):
        if client_procs > len(hosts):
            logging.warn('More client processes than hosts - wrapping around')
        hosts = ((1 + client_procs / len(hosts)) * hosts)[:client_procs]

    # Check local installation

    try:
        scheduler_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                      'psscheduler.py')
        client_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   'psclient.py')
        if not os.path.exists(scheduler_path):
            raise OSError('No such file: %s' % scheduler_path)
        if not os.path.exists(client_path):
            raise OSError('No such file: %s' % client_path)
    except Exception, err:
        logging.error('Unable to find PastSet components: %s' % err)
        usage()
        sys.exit(1)

    # Use location independent path on remote hosts

    scheduler_path = 'pypsscheduler'
    client_path = 'pypsclient'

    # Default to localhost as master if PSMASTER is not set

    if conf['psmaster']:
        main_host = conf['psmaster']
    else:
        main_host = 'localhost'

    env_pairs = []
    for (key, val) in conf.items():
        if not key.startswith('ps') and not key.startswith('PYRO_'):
            continue
        env_pairs.append('%s="%s"' % (key.upper(), val))
    if os.getenv('PATH', None):
        env_pairs.append('PATH=%s' % os.getenv('PATH'))
    if os.getenv('PYTHONPATH', None):
        env_pairs.append('PYTHONPATH=%s' % os.getenv('PYTHONPATH'))
    cmd_env = ' '.join(env_pairs)
    scheduler_cmd = '%s %s' % (cmd_env, scheduler_path)
    client_cmd = '%s %s' % (cmd_env, client_path)

    # Run scheduler and server on main_host through ssh to silence it

    logging.debug("launching psscheduler on %s: %s" % (main_host,
                                                       scheduler_cmd))
    scheduler = subprocess.Popen(conf['psssh'].split() + \
                                 [main_host, scheduler_cmd])

    # Launch clients only after pastset is ready to make sure they do not
    # unnecessarily go through broadcast lookup because they get to the ns
    # check before name server is up

    ps_ready = psbase.wait_for_pastset(conf)
    nodes = {}
    if ps_ready:
        for host in hosts:
            logging.debug("launching psclient on %s: %s" % (host, client_cmd))
            nodes[host] = subprocess.Popen(conf['psssh'].split() + \
                                           [host, client_cmd])

        # Launch app locally

        logging.debug("launching pastset application %s" % app)
        app = subprocess.Popen(conf['pspython'].split() + [app_path] + \
                               app_args)
        app.wait()
    else:
        logging.error("gave up locating pastset - server not running?")

    # Graceful shutdown or kill - give clients a chance to exit cleanly

    psbase.graceful_exit(nodes)
    psbase.graceful_exit({'scheduler': scheduler})


if __name__ == '__main__':

    # Default settings - with environment overrides

    conf = psbase.load_settings()
    main(conf)
