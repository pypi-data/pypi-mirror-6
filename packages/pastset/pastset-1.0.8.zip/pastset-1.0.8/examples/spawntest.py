#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# simple - simple example application inserting and reading tuples
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

"""Simple example PastSet application inserting and reading tuples"""

import pastset
import time
pset = pastset.PastSet()

pset.spawn('spawnclient.py', 'test')

pset.spawn('spawnclient.py', ('test', -1))

param = ['test']
for i in xrange(10):
    param.append(i)
    pset.spawn('spawnclient.py', param)

time.sleep(10)
pset.halt()

