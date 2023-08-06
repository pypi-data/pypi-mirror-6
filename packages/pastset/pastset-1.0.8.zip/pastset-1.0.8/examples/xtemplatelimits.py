#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# xtemplatelimits - default and type casting example xfunction application
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

"""Example PastSet application investigating tuple template limits:
Compare the default loose restrictions on actual tuple contents to the strict
casting and checks with the xtypecast XFunction.
All but the two first entries should fail for the strict version whereas the
default loose version should silently accept all entries.
"""

import pastset

entries = [[123, 42.42, 'abc'], ['123', '42.42', 'abc'], [123, ],
           [123, 42.42, 'abc', 'def'], ['abc', 42.42, 'abc'],
           [123, 'abc', 'def'], [123, 42.42, u'æøå'], [id, 42.42, 'abc']]
pset = pastset.PastSet()
loose = pset.enter(('Loose', int, float, str))
strict = pset.enter(('Strict', int, float, str), 'xtypecast')
for entry in entries:
    print "compare loose and strict handling of payload: %s" % (entry, )
    loose_entry = tuple(['Loose'] + entry)
    strict_entry = tuple(['Strict'] + entry)
    try:
        loose.move(loose_entry)
        print "loose content observed: %s" % (loose.observe(), )
    except Exception, exc:
        print "loose handling failed: %s" % exc
    try:
        strict.move(strict_entry)
        print "strict content observed: %s" % (strict.observe(), )
    except Exception, exc:
        print "strict handling failed: %s" % exc

pset.halt()

