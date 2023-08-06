#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# psclean - helper to clean up after pastset environment and application
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

"""PastSet clean up helper to make sure all PastSet components are in a clean
state for a new PastSet application. Should only be required if previous
application severely misbehaved leaving stray processes.
"""

import logging
import os
import subprocess
import sys

import psbase


def usage():
    "Usage help"
    print '''Usage %s [application]
%s''' % (sys.argv[0], psbase.settings_doc())

def main(conf):
    """Clean up all components"""
    psbase.init_logging(conf, logging)
    logging.debug("starting")
    for msg in psbase.extract_warnings(conf):
        logging.warn(msg)

    app_list = []
    if sys.argv[1:]:
        app_list = sys.argv[1:]
    for app in app_list:
        try:
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
        scheduler_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'psscheduler.py')
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

    server_path = 'psserver'
    scheduler_path = 'psscheduler'
    run_path = 'psrun'
    client_path = 'psclient'
    pyro_path = 'Pyro'

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
    server_cmd = '%s %s %s' % (cmd_env, conf['pspkill'], server_path)
    scheduler_cmd = '%s %s %s' % (cmd_env, conf['pspkill'], scheduler_path)
    client_cmd = '%s %s %s' % (cmd_env, conf['pspkill'], client_path)
    run_cmd = '%s %s %s' % (cmd_env, conf['pspkill'], run_path)
    pyro_cmd = '%s %s %s' % (cmd_env, conf['pspkill'], pyro_path)

    # Kill app (optional) and clients first

    for app in app_list:
        app_cmd = '%s %s %s' % (cmd_env, conf['pspkill'], app_path)
        logging.debug("killing pastset application %s (%s)" % (app, app_cmd))
        try:
            application = subprocess.Popen(app_cmd, shell=True)
            application.wait()
        except Exception, exc:
            logging.error("could not kill %s: %s" % (app, exc))
    logging.debug("killing psrun (%s)" % run_cmd)
    try:
        run = subprocess.Popen(run_cmd, shell=True)
        run.wait()
    except Exception, exc:
        logging.error("could not kill psrun: %s" % exc)
    nodes = {}
    for host in hosts:
        logging.debug("killing psclient on %s: %s" % (host, client_cmd))
        nodes[host] = subprocess.Popen(conf['psssh'].split() + \
                                       [host, client_cmd])
    psbase.graceful_exit(nodes, sleep_secs=2)

    # Kill scheduler and server on main_host through ssh to silence it

    logging.debug("killing psscheduler on %s: %s" % (main_host,
                                                       scheduler_cmd))
    scheduler = subprocess.Popen(conf['psssh'].split() + \
                                 [main_host, scheduler_cmd])
    logging.debug("killing psserver on %s: %s" % (main_host, server_cmd))
    server = subprocess.Popen(conf['psssh'].split() + \
                              [main_host, server_cmd])
    logging.debug("killing Pyro %s: %s" % (main_host, pyro_cmd))
    pyro = subprocess.Popen(conf['psssh'].split() + \
                              [main_host, pyro_cmd])
    psbase.graceful_exit({'scheduler': scheduler, 'server': server,
                          'pyro': pyro}, sleep_secs=2)


if __name__ == '__main__':

    # Default settings - with environment overrides

    conf = psbase.load_settings()
    main(conf)
