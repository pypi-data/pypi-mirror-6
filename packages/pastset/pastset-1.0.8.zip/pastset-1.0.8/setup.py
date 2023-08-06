#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# setup - distutils install helper
# Copyright (C) 2010-2014  The pypastset project lead by Brian Vinter
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

"""Distutils install helper"""

import os
from distutils.core import setup

requires = ['pyro']
core_packages = ['pastset']
helper_modules = ['psbase']
exec_modules = ['psrun', 'psclient', 'psscheduler', 'psserver', 'psmanage', 'psclean']
core_scripts = ['py%s' % i for i in exec_modules]
example_scripts = ['simpleobject', 'xmcpiserver', 'ping', 'simple',
                   'xsimple', 'pong', 'spawnclient', 'xtest',
                   'mcpiclient', 'spawntest', 'xtimestamp',
                   'mcpiserver', 'tracer', 'flac2mp3']
extra_docs = ["../README", "Programming with Python PastSet.pdf", "pshosts-localhost"]
extra_docs_paths = [os.path.join("doc", name) for name in extra_docs]
example_scripts_paths = [os.path.join("examples", "%s.py" % i) for i in \
                         example_scripts]
package_list = core_packages

install_name = "python-pastset"
long_desc = '''pyPastSet is a Python implementation of the PastSet tuple-based
distributed shared memory and computing system.

In some ways PastSet is similar to the classic Linda tuplespace, but with some
significant differences. In PastSet, tuples are generated dynamically based on
tuple templates that may also be generated dynamically. Each set of tuples
based on identical templates is denoted an element of PastSet. An element may
be seen as representing a trace of interprocess communications in the
multidimensional space spawned by the tuple template.

In effect, PastSet keeps a sequentially ordered log of all tuples of the same
or identical templates that have existed in the system. This also allows the
processes to re-read previously read tuples.
It is the intention that the added semantics of PastSet will allow programmers
to more easily create parallel programs that are not limited to the
traditional ‘bag of tasks’ type.

pyPastSet implements the PastSet tuple memory and process distribution model
using the powerful Pyro distributed object framework for the core communication
and SSH for secure remote process spawning.
'''
classify = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: System :: Distributed Computing ',
    'Topic :: System :: Networking',
    'Topic :: Software Development :: Distributed Shared Memory',
    ],
      
setup(name='pastset',
      version='1.0.8',
      description='PastSet is a tuple-based distributed shared memory system',
      long_description=long_desc,
      author='The pyPastSet project',
      author_email='jonas DOT bardino AT gmail DOT com',
      url='http://code.google.com/p/pypastset/',
      download_url='https://pypi.python.org/pypi/pastset',
      license='GNU GPL v2',
      platforms=['All'],
      requires=requires,
      install_requires=requires,
      packages=package_list,
      scripts=core_scripts,
      data_files=[(os.path.join("share", "doc", install_name),
                   extra_docs_paths),
                  (os.path.join("share", "doc", install_name, "examples"),
                   example_scripts_paths)]
      )
