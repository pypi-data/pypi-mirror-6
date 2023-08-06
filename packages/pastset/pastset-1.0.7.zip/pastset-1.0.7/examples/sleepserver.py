#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# sleepserver - sleeper server example application for testing e.g. manage
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

"""Sleep server example PastSet application for testing e.g. psmanage"""

import sys

import pastset

bags = 10
bagsize = 100
workers = 2

if sys.argv[1:] and sys.argv[1].isdigit():
    workers = int(sys.argv[1])
if sys.argv[2:] and sys.argv[2].isdigit():
    bags = int(sys.argv[2])
if sys.argv[3:] and sys.argv[3].isdigit():
    bagsize = int(sys.argv[3])

pset = pastset.PastSet()

jobs = pset.enter(('sleep-jobs', int))
results = pset.enter(('sleep-results', int))

for i in xrange(bags):
    jobs.move((bagsize, ))

for i in xrange(workers):
    pset.spawn('sleepclient.py', '')

for i in xrange(bags):
    res = results.observe()

print 'Sleepers all done'

pset.halt()

