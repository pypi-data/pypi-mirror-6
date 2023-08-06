#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# psmanage - manae and monitor pastset instances
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

"""PastSet manager and monitor"""

import logging
import sys

import psbase
import pastset

specs_cmds = ['mstat', 'clients', 'hosts']
tasks_cmds = ['pstat', 'tasks', 'processes']
def usage():
    "Usage help"
    print '''Usage %s <command> [filter]
Where command is
  %s\t\tto show client specs
  %s\t\tto show client tasks
and filter is an optional name to match in the first column of the output.
%s''' % (sys.argv[0], ' | '.join(specs_cmds), ' | '.join(tasks_cmds),
         psbase.settings_doc())

def show_table(col_header, col_sizes, col_gap, entries):
    """Pretty print table with headers followed by entries using specified
    spacing.
    """
    for entry in col_header + entries:
        line = ""
        col = 0
        for item in entry:
            cut_item = str(item)[:col_sizes[col]]
            prefix_space = " " * (col_sizes[col]-len(cut_item))
            suffix_space = " " * col_gap
            line += "%s%s%s" % (prefix_space, cut_item, suffix_space)
            col += 1
        print line

def show_clients(client_specs):
    """Pretty print client specs"""
    col_sizes = [14, 12, 8, 7, 5, 6, 8, 8]
    col_gap = 2
    header = [('psid', 'host', 'system', 'arch', 'cores', 'mem', 'disk',
              'bench')]
    show_table(header, col_sizes, col_gap, client_specs)

def show_tasks(client_tasks):
    """Pretty print client tasks"""
    col_sizes = [22, 32, 24]
    col_gap = 2
    header = [('cmd', 'args', 'spawned')]
    show_table(header, col_sizes, col_gap, client_tasks)

def client_specs(conf, pset, psid_filter=[]):
    """Look up client specs with indexed observes on client registration
    element.
    If psid_filter is set to a list of host IDs or patterns only the specs for
    matching hosts will be returned.
    """

    clients = pset.enter(('__clients', str, str, str, int, int, int, float))
    workers = []
    for i in xrange(0, clients.last()):
        specs = clients.observe(i)
        (psid, host, system, arch, cores, mem, disk, bench) = specs
        if not psid_filter or psid in psid_filter:
            workers.append(specs)
    return workers

def client_tasks(conf, pset, cmd_filter=[]):
    """Look up client tasks with indexed observes on jobs element.
    If cmd_filter is set to a list of task name or patterns only the matching
    tasks will be returned.
    """

    jobs = pset.enter(('__jobs', str, str, str))
    tasks = []
    for i in xrange(0, jobs.last()):
        task = jobs.observe(i)
        (cmd, args, time_stamp) = task
        task_string = (cmd, ' '.join(args), time_stamp)
        if not cmd_filter or cmd in cmd_filter:
            tasks.append(task_string)
    return tasks

def main(conf):
    """Execute manage or monitoring operation"""
    psbase.init_logging(conf, logging)
    logging.debug("starting")
    for msg in psbase.extract_warnings(conf):
        logging.warn(msg)
    if not sys.argv[1:]:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]
    cmd_args = sys.argv[2:]

    ready = psbase.wait_for_pastset(conf, 10)
    if not ready:
        logging.error("gave up locating active PastSet")
        sys.exit(1)
    pset = pastset.PastSet()

    if cmd in specs_cmds:
        specs = client_specs(conf, pset, cmd_args)
        show_clients(specs)
    elif cmd in tasks_cmds:
        tasks = client_tasks(conf, pset, cmd_args)
        show_tasks(tasks)
    else:
        logging.error("unknown command: %s" % cmd)
        usage()
        sys.exit(1)


if __name__ == '__main__':

    # Default settings - with environment overrides

    conf = psbase.load_settings()
    main(conf)
