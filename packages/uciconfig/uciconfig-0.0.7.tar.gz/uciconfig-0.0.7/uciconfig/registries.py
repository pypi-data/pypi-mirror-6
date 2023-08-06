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


class Registry(object):
    """A class that registers objects to a name.

    There are many places that want to collect related objects and access them
    by a key. This class is designed to allow registering the mapping from key
    to object.
    """

    def __init__(self):
        """Create a new Registry."""
        self.data = {}
        self.help = {}

    def register(self, key, obj, help_string=None):
        """Register a new object to a name.

        :param key: This is the key to use to request the object later.

        :param obj: The object to register.

        :param help_string: Help text for this entry. This may be a string or
                a callable. If it is a callable, it should take two
                parameters (registry, key): this registry and the key that
                the help was registered under.
        """
        if key in self.data:
            raise KeyError('Key {!r} is already registered'.format(key))
        self.data[key] = obj
        self.help[key] = help_string

    def get(self, key):
        """Return the object register()'ed to the given key.

        :param key: The key to obtain the object for. If no object has been
            registered to that key, KeyError will be
            raised.
        :return: The previously registered object.
        """
        return self.data[key]

    def get_help(self, key):
        """Get the help text associated with the given key"""
        the_help = self.help[key]
        if callable(the_help):
            return the_help(self, key)
        return the_help

    def remove(self, key):
        """Remove a registered entry.

        This is mostly for the test suite, but it can be used by others
        """
        del self.data[key]
        del self.help[key]

    def keys(self):
        return sorted(self.data.keys())

    def values(self):
        return self.data.values()
