#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# simpleobject - simple example application using objects in tuples
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

"""Simple example PastSet application inserting and reading tuples with
python objects"""

import pastset
import pickle


class ObjectTest:
    """Simple class for object test"""
    
    def __init__(self, data):
        self.data = data

    def show(self):
        """Display object data"""

        print self.data


pset = pastset.PastSet()

data = ObjectTest('Hello world...')

test = pset.enter(('Test', str))
test.move((pickle.dumps(data), ))
print test.first(), test.last()
b = pickle.loads(test.observe()[0])
print test.first(), test.last()
b.show()

pset.halt()

