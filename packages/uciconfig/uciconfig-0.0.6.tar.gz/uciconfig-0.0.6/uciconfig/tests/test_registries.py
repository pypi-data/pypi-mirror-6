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

import unittest


from uciconfig import registries


class TestRegistry(unittest.TestCase):

    def setUp(self):
        super(TestRegistry, self).setUp()
        reg = registries.Registry()
        reg.register('one', 1, 'one help.')
        reg.register('two', 2, 'two help.')
        reg.register('four', 4, 'four help.')

        def five_help(reg, key):
            return 'five help.'
        reg.register('five', 5, five_help)

        self.reg = reg

    def test_get_unknown_key(self):
        with self.assertRaises(KeyError):
            self.reg.get('three')

    def test_get_existing_key(self):
        self.assertEqual(2, self.reg.get('two'))

    def test_get_help_unknown_key(self):
        with self.assertRaises(KeyError):
            self.reg.get_help('three')

    def test_get_help_existing_key(self):
        self.assertEqual('two help.', self.reg.get_help('two'))

    def test_get_callable_help_existing_key(self):
        self.assertEqual('five help.', self.reg.get_help('five'))

    def test_register_unknown_key(self):
        self.reg.register('forty-two', 42)
        self.assertEqual(42, self.reg.get('forty-two'))

    def test_register_existing_key(self):
        with self.assertRaises(KeyError):
            self.reg.register('one', 2)

    def test_remove_unknown_key(self):
        with self.assertRaises(KeyError):
            self.reg.remove('three')

    def test_remove_existing_key(self):
        self.reg.remove('one')
        with self.assertRaises(KeyError):
            self.reg.get('one')

    def test_keys(self):
        self.assertEqual(['five', 'four', 'one', 'two'],
                         sorted(self.reg.keys()))

    def test_values(self):
        self.assertEqual([1, 2, 4, 5], sorted(self.reg.values()))
