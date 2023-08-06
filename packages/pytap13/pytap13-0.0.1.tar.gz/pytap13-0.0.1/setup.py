#!/usr/bin/env python
# Copyright 2011, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Author: Josef Skladanka <jskladan@redhat.com>

from distutils.core import setup

setup(  name = 'pytap13',
        py_modules = ['pytap13'],
        version = '0.0.1',
        description = 'Python parser for the Test Anything Protocol (TAP) version 13',
        author = 'Josef Skladanka',
        author_email = 'jskladan@redhat.com',
        url = "https://bitbucket.org/rajcze/pytap13",
        install_requires = ['yamlish'],
        classifiers = [

            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2",
            "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
            "Topic :: Software Development :: Testing",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],

     )

