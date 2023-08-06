#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# sleepclient - sleep client used by sleepserver
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

"""Example PastSet sleep application client used by sleepserver"""

import time

import pastset

pset = pastset.PastSet()

jobs = pset.enter(('sleep-jobs', int))
results = pset.enter(('sleep-results', int))

while True:
    sleep_time = jobs.observe()[0]  # Job is a tuple (int,) so we extract element 0
    time.sleep(sleep_time)
    results.move((sleep_time, ))

