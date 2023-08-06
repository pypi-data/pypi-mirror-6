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

import os
import re
import warnings


from uciconfig import (
    errors,
    registries,
)


class Option(object):
    """An option definition.

    The option *values* are stored in config files and found in sections.

    Here we define various properties about the option itself, its default
    value, how to convert it from stores, what to do when invalid values are
    encoutered, in which config files it can be stored.
    """

    def __init__(self, name, help_string, default=None,
                 default_from_env=None, override_from_env=None,
                 from_unicode=None, invalid=None, unquote=True):
        """Build an option definition.

        :param name: The name used to refer to the option.

        :param help_string: A doc string to explain the option to the user.

        :param default: The default value to use when none exist in the config
            stores. This is either a string that ``from_unicode`` will convert
            into the proper type, a callable returning a unicode string so that
            ``from_unicode`` can be used on the return value, or a python
            object that can be stringified (so only the empty list is supported
            for example). If an option must be set, the special MANDATORY
            (defined in this module) value can be used, an error is then raised
            if an attempt is made to access the option value.

        :param default_from_env: A list of environment variables which can
           provide a default value. 'default' will be used only if none of the
           variables specified here are set in the environment.

        :param override_from_env: A list of environment variables which can
           override any configuration setting.

        :param from_unicode: A callable to convert the unicode string
            representing the option value in a store or its default value.

        :param invalid: The action to be taken when an invalid value is
            encountered in a store. This is called only when from_unicode is
            invoked to convert a string and returns None or raise ValueError or
            TypeError. Accepted values are: None (ignore invalid values),
            'warning' (emit a warning), 'error' (emit an error message and
            terminates).

        :param unquote: Should the unicode value be unquoted before conversion.
           This should be used only when the store providing the values cannot
           safely unquote them. It is provided so daughter classes can handle
           the quoting themselves.
        """
        if override_from_env is None:
            override_from_env = []
        if default_from_env is None:
            default_from_env = []
        self.name = name
        self._help = help_string
        self.override_from_env = override_from_env
        # Convert the default value to a unicode string so all values are
        # strings internally before conversion (via from_unicode) is attempted.
        if default is None:
            self.default = None
        elif default is MANDATORY:
            # Special case, no further check needed
            self.default = default
        elif isinstance(default, list):
            # Only the empty list is supported
            if default:
                raise AssertionError(
                    'Only empty lists are supported as default values')
            self.default = ','
        elif isinstance(default, (unicode, bool, int, float)):
            # Rely on python to convert strings, booleans, floats and integers
            self.default = '{}'.format(default)
        elif callable(default):
            self.default = default
        else:
            # other python objects are not expected
            raise AssertionError(
                '{!r} is not supported as a default value'.format(default))
        self.default_from_env = default_from_env
        self.from_unicode = from_unicode
        self.unquote = unquote
        if invalid and invalid not in ('warning', 'error'):
            raise AssertionError(
                "{} not supported for 'invalid'".format(invalid))
        self.invalid = invalid

    @property
    def help(self):
        return self._help

    def convert_from_unicode(self, store, unicode_value):
        if self.unquote and store is not None and unicode_value is not None:
            unicode_value = store.unquote(unicode_value)
        if self.from_unicode is None or unicode_value is None:
            # Don't convert or nothing to convert
            return unicode_value
        try:
            converted = self.from_unicode(unicode_value)
        except (ValueError, TypeError):
            # Invalid values are ignored
            converted = None
        if converted is None and self.invalid is not None:
            # The conversion failed
            if self.invalid == 'warning':
                warnings.warn('Value "{}" is not valid'
                              ' for "{}"'.format(unicode_value, self.name))
            elif self.invalid == 'error':
                raise errors.OptionValueError(self.name, unicode_value)
        return converted

    def get_override(self):
        value = None
        for var in self.override_from_env:
            try:
                # If the env variable is defined, its value takes precedence
                value = os.environ[var]
                break
            except KeyError:
                continue
        return value

    def get_default(self):
        value = None
        for var in self.default_from_env:
            try:
                # If the env variable is defined, its value is the default one
                value = os.environ[var]
                break
            except KeyError:
                continue
        if value is None:
            # Otherwise, fallback to the value defined at registration
            if callable(self.default):
                value = self.default()
                if not isinstance(value, unicode):
                    raise AssertionError(
                        "Callable default value for '%s' should be unicode"
                        % (self.name))
            else:
                value = self.default
        if value is MANDATORY:
            raise errors.OptionMandatoryValueError(self.name)
        return value

    def get_help_topic(self):
        return self.name


# A special default value to indicate that an option must be set.
MANDATORY = object()


# Predefined converters to convert values from store into types other than
# unicode

_valid_boolean_strings = dict(yes=True, no=False,
                              y=True, n=False,
                              on=True, off=False,
                              true=True, false=False)
_valid_boolean_strings['1'] = True
_valid_boolean_strings['0'] = False


def bool_from_store(s, accepted_values=None):
    """Returns a boolean if the string can be interpreted as such.

    Interpret case insensitive strings as booleans. The default values
    includes: 'yes', 'no, 'y', 'n', 'true', 'false', '0', '1', 'on',
    'off'. Alternative values can be provided with the 'accepted_values'
    parameter.

    :param s: A string that should be interpreted as a boolean. It should be of
        type string or unicode.

    :param accepted_values: An optional dict with accepted strings as keys and
        True/False as values. The strings will be tested against a lowered
        version of 's'.

    :return: True or False for accepted strings, None otherwise.
    """
    if accepted_values is None:
        accepted_values = _valid_boolean_strings
    val = None
    if type(s) is unicode:
        try:
            val = accepted_values[s.lower()]
        except KeyError:
            pass
    return val


def int_from_store(string):
    return int(string)


_unit_suffixes = dict(K=10 ** 3, M=10 ** 6, G=10 ** 9)
_unit_re = re.compile("^(\d+)(([" + ''.join(_unit_suffixes) + "])b?)?$",
                      re.IGNORECASE)


def int_SI_from_store(string):
    """Convert a human readable size in SI units, e.g 10MB into an integer.

    Accepted suffixes are K,M,G. It is case-insensitive and may be followed
    by a trailing b (i.e. Kb, MB). This is intended to be practical and not
    pedantic.

    :param string: The option value as a unicode string.

    :return Integer, expanded to its base-10 value if a proper SI unit is
        found, None otherwise.
    """
    m = _unit_re.match(string)
    val = None
    if m is not None:
        val, _, unit = m.groups()
        val = int(val)
        if unit:
            try:
                coeff = _unit_suffixes[unit.upper()]
            except KeyError:
                raise ValueError('{0} is not an SI unit.'.format(unit))
            val *= coeff
    return val


def float_from_store(string):
    return float(string)


class ListOption(Option):

    def __init__(self, name, help_string, default=None,
                 default_from_env=None, override_from_env=None,
                 invalid=None):
        """A list Option definition.

        This overrides the base class so the conversion from a unicode string
        can take quoting (NIY) into account.
        """
        super(ListOption, self).__init__(name, help_string, default=default,
                                         default_from_env=default_from_env,
                                         override_from_env=override_from_env,
                                         from_unicode=self.from_unicode,
                                         invalid=invalid, unquote=False)

    def from_unicode(self, string):
        if not isinstance(string, unicode):
            raise TypeError
        return [s.strip() for s in string.split(',') if s]


class RegistryOption(Option):
    """Option for a choice from a registry."""

    def __init__(self, name, help_string, registry,
                 default=None, default_from_env=None,
                 invalid=None):
        """A registry based Option definition.

        This overrides the base class so the conversion from a unicode string
        can take quoting (NIY) into account.
        """
        super(RegistryOption, self).__init__(
            name, help_string, default=default,
            default_from_env=default_from_env,
            from_unicode=self.from_unicode,
            invalid=invalid, unquote=False)
        self.registry = registry

    def from_unicode(self, string):
        if not isinstance(string, unicode):
            raise TypeError
        try:
            return self.registry.get(string)
        except KeyError:
            raise ValueError(
                'Invalid value {} for {}.'
                'See help for a list of possible values.'.format(string,
                                                                 self.name))

    @property
    def help(self):
        ret = [self._help, "\n\nThe following values are supported:\n"]
        for key in sorted(self.registry.keys()):
            ret.append(" %s - %s\n" % (key, self.registry.get_help(key)))
        return "".join(ret)


class OptionRegistry(registries.Registry):
    """Register config options by their name.

    This overrides ``registries.Registry`` to simplify registration by
    acquiring some information from the option object itself.
    """

    def register(self, option):
        """Register a new option under its name.

        :param option: The option to register. Its name is used as the key.
        """
        super(OptionRegistry, self).register(option.name, option, option.help)


option_registry = OptionRegistry()
