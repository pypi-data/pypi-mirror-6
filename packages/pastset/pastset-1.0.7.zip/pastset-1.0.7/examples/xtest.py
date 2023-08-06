#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# xtest - example xfunction test application
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

"""Example PastSet Xfunction application"""

import pastset.element


class Element(pastset.element.Element):

    """Extend default Element with Xfunction"""

    def __init__(self, template):
        super(Element, self).__init__(template)
        self.template = tuple(list(template)[1:])
        expected = (int, float, str)
        if self.template != expected:
            raise Exception('PastSet error xtest expected %s entries got %s' \
                            % (expected, self.template))

    def extract_template(self, data):
        """Find tuple signature"""

        return tuple([type(x) for x in data])

    def move(self, data):
        """Override move to double all integer data values"""

        if self.template != self.extract_template(data):
            raise Exception('PastSet: move with incompatible template')

        (a, b, c) = data
        data = (2 * a, 2 * b, 2 * c)

        super(Element, self).move(data)

    def observe(self, index):
        """Override observe to add test string to last data value"""

        (a, b, c) = super(Element, self).observe(index)
        return (a, b, c + ' - Hello from xtest')


