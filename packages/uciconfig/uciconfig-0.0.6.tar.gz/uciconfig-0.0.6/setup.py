#!/usr/bin/env python

# This file is part of Ubuntu Continuous Integration configuration framework.
#
# Copyright 2013, 2014 Canonical Ltd.
#  
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#  
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#  
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


import setuptools

import uciconfig


setuptools.setup(
    name='uciconfig',
    version='.'.join(str(c) for c in uciconfig.__version__[0:3]),
    description=('Ubuntu Continuous Integration config framework.'),
    author='Vincent Ladeuil',
    author_email='vila+ci@canonical.com',
    url='https://launchpad.net/uci-config',
    license='GPLv3',
    install_requires=['subunit', 'testtools'],
    packages=['uciconfig', 'uciconfig.tests'],
)
