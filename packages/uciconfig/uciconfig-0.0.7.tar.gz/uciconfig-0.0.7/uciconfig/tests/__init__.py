# This file is part of Ubuntu Continuous Integration configuration framework.
#
# Copyright 2013 Canonical Ltd.
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


def assertSectionContent(test, expected, actual):
    """Assert that some options have the proper values in a section.

    :param expected: A (name, options) tuple where 'name' is a section name and
        'options' a dict of the expection key/value pairs for the options.

    :param actual: A (store, section) tuple where 'store' is unused here but
       make the assertion easier to use and 'section' contains the options to
       check.
    """
    expected_name, expected_options = expected
    _, section = actual
    test.assertEquals(expected_name, section.id)
    test.assertEquals(expected_options,
                      dict([(k, section.get(k))
                            for k in expected_options.keys()]))
