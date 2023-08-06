#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# xmcpiserver - example monte carlo pi server using xfunction
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

"""Example monte carlo pi server using Xfunction"""

import sys
import time

import pastset

bags = 1000
bagsize = 1000000
workers = 2

if sys.argv[1:] and sys.argv[1].isdigit():
    workers = int(sys.argv[1])
if sys.argv[2:] and sys.argv[2].isdigit():
    bags = int(sys.argv[2])
if sys.argv[3:] and sys.argv[3].isdigit():
    bagsize = int(sys.argv[3])

pset = pastset.PastSet()

jobs = pset.enter(('pi-jobs', int), 'xtimestamp')
results = pset.enter(('pi-results', int), 'xtimestamp')

for i in xrange(bags):
    jobs.move((bagsize, ))

for i in xrange(workers):
    pset.spawn('mcpiclient.py', '')

pi_val = 0.0
for i in xrange(bags):
    res = results.observe()
    pi_val += res[0]  # result is a tuple(float,) so we extract element 0

    org = jobs.observe(i)
    print 'Job submitted ', org[-2], 'started', org[-1], \
        'and finished', res[-2]

pi_val /= bags

print 'Pi is found as %f with %d worker(s), %d bag(s) and bagsize of %d' \
    % (pi_val, workers, bags, bagsize)

pset.halt()

