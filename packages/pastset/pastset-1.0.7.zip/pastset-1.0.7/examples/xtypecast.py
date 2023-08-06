#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# xtypecast - example xfunction type cast application
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

"""Example PastSet Xfunction application casting tuples to template"""

import pastset.element


class Element(pastset.element.Element):

    """Extend default Element with Xfunction"""

    def __init__(self, template):
        super(Element, self).__init__(template)

    def move(self, data):
        """Override move to force type casting of types. This is likely to not
        work for complex types like objects.
        Supports e.g. tuples with string ID as first tuple template entry by
        using the type of such non-type entries.
        """

        if len(self.__template) != len(data):
            raise Exception('PastSet: move with incompatible data size (%d)' % \
                            len(data))
        types = []
        for entry in self.__template:
            if isinstance(entry, type):
                types.append(entry)
            else:
                types.append(entry.__class__)
        pairs = zip(types, data)
        typed_data = tuple([cast(i) for (cast, i) in pairs])
        super(Element, self).move(typed_data)
