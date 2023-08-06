#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# xtimestamp - example xfunction application appending timestamps to tuples
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

"""Example Xfunction application appending timestamps to tuples"""

import time

import pastset.element


class Element(pastset.element.Element):

    """Extend default Element with Xfunction"""

    def __init__(self, template):
        super(Element, self).__init__(template)

    def move(self, data):
        """Override move to automatically insert timestamp"""

        try:
            data = list(data)
            data.append(time.asctime())
            data = tuple(data)
            super(Element, self).move(data)
        except Exception, err:
            raise Exception('PastSet timestamp error on %s: %s'
                            % (data, err))

    def observe(self, index):
        """Override observe to automatically insert timestamp"""

        data = super(Element, self).observe(index)
        if index == -1:
            data = list(data)
            data.append(time.asctime())
            data = tuple(data)
            target = super(Element, self).first() - 1
            super(Element, self).__set_entry(target, data)
        return data


