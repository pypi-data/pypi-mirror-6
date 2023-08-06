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
# Copyright (c) 2013 Canonical. See COPYING for details.

from ucitests.tests import test_style

import uciconfig


class TestPep8(test_style.TestPep8):

    packages = [uciconfig]


class TestPyflakes(test_style.TestPyflakes):

    packages = [uciconfig]
