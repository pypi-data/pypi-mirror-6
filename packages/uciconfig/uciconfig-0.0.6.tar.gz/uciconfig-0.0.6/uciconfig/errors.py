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


class ConfigError(Exception):
    """Base class for all uci-config exceptions.

    :cvar fmt: A format string that daughter classes override
    """

    fmt = 'Daughter classes should redefine this'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __unicode__(self):
        return self.fmt.format([], **self.__dict__)

    __repr__ = __unicode__


class ParseError(ConfigError):

    fmt = '{path}({line}): {msg}'

    def __init__(self, path, line, **kwargs):
        super(ParseError, self).__init__(**kwargs)
        self.path = path
        self.line = line


class SectionEmptyName(ParseError):

    fmt = '{path}({line}): Section name cannot be empty.'


class InvalidSyntax(ParseError):

    fmt = '{path}({line}): Not a section nor an option.'


class StoreError(ConfigError):

    def __init__(self, path, **kwargs):
        super(StoreError, self).__init__(**kwargs)
        self.path = path


class InvalidContent(StoreError):

    fmt = '{path}: Content is not utf8.'


class PermissionDenied(StoreError):

    fmt = '{path}: Permission denied.'


class NoSuchFile(StoreError):

    fmt = '{path}: No such file.'


class OptionError(ConfigError):

    def __init__(self, name, **kwargs):
        """Base class for option related errors.

        :param name: The option name.
        """
        super(OptionError, self).__init__(**kwargs)
        self.name = name


class OptionValueError(OptionError):

    fmt = '{name}: Value "{value}" is not valid.'

    def __init__(self, name, value, **kwargs):
        super(OptionValueError, self).__init__(name, **kwargs)
        self.value = value


class OptionMandatoryValueError(OptionError):

    fmt = '{name} must be set.'


class StackError(ConfigError):
    """Base class for stack related errors."""


class OptionExpansionLoop(StackError):

    fmt = 'Loop involving {refs!r} while expanding "{string}".'

    def __init__(self, string, refs, **kwargs):
        super(OptionExpansionLoop, self).__init__(**kwargs)
        self.string = string
        self.refs = '->'.join(refs)


class ExpandingUnknownOption(StackError):

    fmt = 'Option {name} is not defined while expanding "{string}".'

    def __init__(self, name, string, **kwargs):
        super(ExpandingUnknownOption, self).__init__(**kwargs)
        self.name = name
        self.string = string
