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

from __future__ import unicode_literals

import unittest
import warnings


from uciconfig import (
    errors,
    options,
    registries,
)
from ucitests import (
    assertions,
    fixtures,
)


class TestOption(unittest.TestCase):

    def test_default_value(self):
        opt = options.Option('foo', 'foo help.', default='bar')
        self.assertEqual('bar', opt.get_default())

    def test_callable_default_value(self):
        def bar():
            return 'bar'
        opt = options.Option('foo', 'foo help.', default=bar)
        self.assertEqual('bar', opt.get_default())

    def test_mandatory_option(self):
        opt = options.Option('foo', 'Foo help.', default=options.MANDATORY)
        with self.assertRaises(errors.OptionMandatoryValueError) as cm:
            opt.get_default()
        self.assertEqual('foo must be set.', unicode(cm.exception))

    def test_default_value_from_env(self):
        opt = options.Option('foo', 'foo help.', default='bar',
                             default_from_env=['FOO'])
        fixtures.override_env(self, 'FOO', 'quux')
        # Env variable provides a default taking over the option one
        self.assertEqual('quux', opt.get_default())

    def test_first_default_value_from_env_wins(self):
        opt = options.Option('foo', 'foo help.', default='bar',
                             default_from_env=['NO_VALUE', 'FOO', 'BAZ'])
        fixtures.override_env(self, 'FOO', 'foo')
        fixtures.override_env(self, 'BAZ', 'baz')
        # The first env var set wins
        self.assertEqual('foo', opt.get_default())

    def test_not_supported_list_default_value(self):
        with self.assertRaises(AssertionError):
            options.Option('foo', 'foo help.', default=[1])

    def test_not_supported_object_default_value(self):
        with self.assertRaises(AssertionError):
            options.Option('foo', 'foo help.', default=object())

    def test_not_supported_callable_default_value_not_unicode(self):
        def bar_not_unicode():
            return b'bar'
        opt = options.Option('foo', 'foo help.', default=bar_not_unicode)
        with self.assertRaises(AssertionError):
            opt.get_default()

    def test_get_help_topic(self):
        opt = options.Option('foo', 'foo help.')
        self.assertEqual('foo', opt.get_help_topic())


class TestBoolFromStore(unittest.TestCase):

    def assertIsTrue(self, s, accepted_values=None):
        res = options.bool_from_store(s, accepted_values=accepted_values)
        self.assertEqual(True, res)

    def assertIsFalse(self, s, accepted_values=None):
        res = options.bool_from_store(s, accepted_values=accepted_values)
        self.assertEqual(False, res)

    def assertIsNone(self, s, accepted_values=None):
        res = options.bool_from_store(s, accepted_values=accepted_values)
        self.assertIs(None, res)

    def test_know_valid_values(self):
        self.assertIsTrue('true')
        self.assertIsFalse('false')
        self.assertIsTrue('1')
        self.assertIsFalse('0')
        self.assertIsTrue('on')
        self.assertIsFalse('off')
        self.assertIsTrue('yes')
        self.assertIsFalse('no')
        self.assertIsTrue('y')
        self.assertIsFalse('n')
        # Also try some case variations
        self.assertIsTrue('True')
        self.assertIsFalse('False')
        self.assertIsTrue('On')
        self.assertIsFalse('Off')
        self.assertIsTrue('ON')
        self.assertIsFalse('OFF')
        self.assertIsTrue('oN')
        self.assertIsFalse('oFf')

    def test_invalid_values(self):
        self.assertIsNone(None)
        self.assertIsNone('doubt')
        self.assertIsNone('frue')
        self.assertIsNone('talse')
        self.assertIsNone('42')

    def test_provide_accepted_values(self):
        av = dict(y=True, n=False, yes=True, no=False)
        self.assertIsTrue('y', av)
        self.assertIsTrue('Y', av)
        self.assertIsTrue('Yes', av)
        self.assertIsFalse('n', av)
        self.assertIsFalse('N', av)
        self.assertIsFalse('No', av)
        self.assertIsNone('1', av)
        self.assertIsNone('0', av)
        self.assertIsNone('on', av)
        self.assertIsNone('off', av)


def assertConverted(test, expected, opt, value):
    test.assertEqual(expected, opt.convert_from_unicode(None, value))


def assertWarns(test, opt, value):
    with warnings.catch_warnings(record=True) as wcm:
        test.assertEqual(None, opt.convert_from_unicode(None, value))
    assertions.assertLength(test, 1, wcm)
    test.assertEqual(
        'Value "{}" is not valid for "{}"'.format(value, opt.name),
        str(wcm[0].message))


def assertErrors(test, opt, value):
    with test.assertRaises(errors.OptionValueError):
        opt.convert_from_unicode(None, value)


def assertConvertInvalid(test, opt, invalid_value):
    opt.invalid = None
    test.assertEqual(None, opt.convert_from_unicode(None, invalid_value))
    opt.invalid = 'warning'
    assertWarns(test, opt, invalid_value)
    opt.invalid = 'error'
    assertErrors(test, opt, invalid_value)


class TestOptionWithBooleanConverter(unittest.TestCase):

    def get_option(self):
        return options.Option('foo', 'A boolean.',
                              from_unicode=options.bool_from_store)

    def test_convert_invalid(self):
        opt = self.get_option()
        # Not all strings are recognized as a boolean
        assertConvertInvalid(self, opt, 'invalid-boolean')
        # A list of strings is never recognized as a boolean
        assertConvertInvalid(self, opt, ['not', 'a', 'boolean'])

    def test_convert_valid(self):
        opt = self.get_option()
        assertConverted(self, True, opt, 'True')
        assertConverted(self, True, opt, '1')


class TestOptionWithIntegerConverter(unittest.TestCase):

    def get_option(self):
        return options.Option('foo', 'An integer.',
                              from_unicode=options.int_from_store)

    def test_convert_invalid(self):
        opt = self.get_option()
        # A string that is not recognized as an integer
        assertConvertInvalid(self, opt, 'forty-two')
        # A list of strings is never recognized as an integer
        assertConvertInvalid(self, opt, ['a', 'list'])

    def test_convert_valid(self):
        opt = self.get_option()
        assertConverted(self, 16, opt, '16')


class TestOptionWithSIUnitConverter(unittest.TestCase):

    def get_option(self):
        return options.Option('foo', 'An integer in SI units.',
                              from_unicode=options.int_SI_from_store)

    def test_convert_invalid(self):
        opt = self.get_option()
        assertConvertInvalid(self, opt, 'not-a-unit')
        assertConvertInvalid(self, opt, 'Gb')  # Forgot the int
        assertConvertInvalid(self, opt, '1b')  # Forgot the unit
        assertConvertInvalid(self, opt, '1GG')
        assertConvertInvalid(self, opt, '1Mbb')
        assertConvertInvalid(self, opt, '1MM')

    def test_convert_valid(self):
        opt = self.get_option()
        assertConverted(self, int(5e3), opt, '5kb')
        assertConverted(self, int(5e6), opt, '5M')
        assertConverted(self, int(5e6), opt, '5MB')
        assertConverted(self, int(5e9), opt, '5g')
        assertConverted(self, int(5e9), opt, '5gB')
        assertConverted(self, 100, opt, '100')


class TestRegistryOption(unittest.TestCase):

    def get_option(self, registry, default=None):
        return options.RegistryOption('fooreg', 'A registry option.', registry,
                                      default=default)

    def test_convert_invalid(self):
        registry = registries.Registry()
        opt = self.get_option(registry)
        assertConvertInvalid(self, opt, [1])
        assertConvertInvalid(self, opt, 'notregistered')

    def test_convert_valid(self):
        registry = registries.Registry()
        registry.register('someval', 1234, 'Some help.')
        opt = self.get_option(registry)
        assertConverted(self, 1234, opt, 'someval')
        assertConverted(self, None, opt, None)

    def test_help(self):
        registry = registries.Registry()
        registry.register('someval',  1234, 'Some option.')
        registry.register('dunno', 1234, 'Some other option.')
        opt = self.get_option(registry)
        self.assertEqual('''A registry option.

The following values are supported:
 dunno - Some other option.
 someval - Some option.
''',
                         opt.help)

    def test_default_value(self):
        registry = registries.Registry()
        opt = self.get_option(registry, default='someval')
        self.assertEqual('someval', opt.get_default())


class TestOptionRegistry(unittest.TestCase):

    def setUp(self):
        super(TestOptionRegistry, self).setUp()
        # Always start with an empty registry
        fixtures.patch(self, options, 'option_registry',
                       options.OptionRegistry())
        self.registry = options.option_registry

    def test_register(self):
        opt = options.Option('foo', 'foo help.')
        self.registry.register(opt)
        self.assertIs(opt, self.registry.get('foo'))

    def test_registered_help(self):
        opt = options.Option('foo', 'A simple option')
        self.registry.register(opt)
        self.assertEquals('A simple option', self.registry.get_help('foo'))


class TestListOption(unittest.TestCase):

    def get_option(self):
        return options.ListOption('foo', 'A list.')

    def test_convert_invalid(self):
        opt = self.get_option()
        # We don't even try to convert a list into a list, we only expect
        # strings
        assertConvertInvalid(self, opt, [1])
        # No string is invalid as all forms can be converted to a list

    def test_convert_valid(self):
        opt = self.get_option()
        # An empty string is an empty list
        assertConverted(self, [], opt, '')
        # A boolean
        assertConverted(self, ['True'], opt, 'True')
        # An integer
        assertConverted(self, ['42'], opt, '42')
        # A single string
        assertConverted(self, ['bar'], opt, 'bar')
