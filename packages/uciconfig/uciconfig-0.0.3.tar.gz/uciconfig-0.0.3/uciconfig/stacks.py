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

import os
import re


from uciconfig import (
    errors,
    options,
    stores,
)


class SectionMatcher(object):
    """Select sections into a given Store.

    This is intended to be used to postpone getting an iterable of sections
    from a store.
    """

    def __init__(self, store):
        self.store = store

    def get_sections(self):
        # This is where we require loading the store so we can see all defined
        # sections.
        sections = self.store.get_sections()
        # Walk the revisions in the order provided
        for store, s in sections:
            if self.match(s):
                yield store, s

    def match(self, section):
        """Does the proposed section match.

        :param section: A Section object.

        :returns: True if the section matches, False otherwise.
        """
        raise NotImplementedError(self.match)


class NameMatcher(SectionMatcher):
    """Select a single section from a store."""

    def __init__(self, store, section_id):
        super(NameMatcher, self).__init__(store)
        self.section_id = section_id

    def match(self, section):
        return section.id == self.section_id


class PathSection(stores.Section):
    """A section providing additional options.

    When the section names are paths, the sections can be selected to provide
    options for a subtree. This section provide automatic options related to
    the full path:

     * relpath: The part of the path that is not in the section name.
     * basename: The last part of the path.
    """

    def __init__(self, section, extra_path):
        super(PathSection, self).__init__(section.id, section.options)
        self.extra_path = extra_path
        self.locals = {'relpath': extra_path,
                       'basename': os.path.basename(extra_path)}

    def get(self, name, default=None, expand=True):
        value = super(PathSection, self).get(name, default)
        if value is not None and expand:
            # expand section local options right now.
            chunks = []
            for is_ref, chunk in iter_option_refs(value):
                if not is_ref:
                    chunks.append(chunk)
                else:
                    ref = chunk[1:-1]
                    if ref in self.locals:
                        chunks.append(self.locals[ref])
                    else:
                        chunks.append(chunk)
            value = ''.join(chunks)
        return value


class StartingPathMatcher(SectionMatcher):
    """A sub path section matcher.

    This selects sections starting with a given path respecting the Store
    order.
    """

    def __init__(self, store, path):
        super(StartingPathMatcher, self).__init__(store)
        self.path = path

    def get_sections(self):
        """Get all sections starting with ``path`` in the store.

        The most generic sections are described first in the store, then more
        specific ones can be provided for reduced scopes.

        The returned sections are therefore returned in the reversed order so
        the most specific ones can be found first.
        """
        path_parts = self.path.rstrip('/').split('/')
        store = self.store
        # Later sections are more specific, they should be returned first
        for _, section in reversed(list(store.get_sections())):
            if section.id is None:
                # The no-name section is always included if present
                yield store, PathSection(section, self.path)
                continue
            section_path = section.id
            if self.path.startswith(section_path):
                section_parts = section_path.rstrip('/').split('/')
                extra_path = '/'.join(path_parts[len(section_parts):])
                yield store, PathSection(section, extra_path)


_option_ref_re = re.compile('({[^{}\n]+})')
"""Describes an expandable option reference.

We want to match the most embedded reference first.

I.e. for '{{foo}}' we will get '{foo}',
for '{bar{baz}}' we will get '{baz}'
"""


def iter_option_refs(string):
    # Split isolate refs so every other chunk is a ref
    is_ref = False
    for chunk in _option_ref_re.split(string):
        yield is_ref, chunk
        is_ref = not is_ref


_shared_stores = {}
_shared_stores_at_exit_installed = False


class Stack(object):
    """A stack of configurations where an option can be defined"""

    def __init__(self, sections_def, store=None, mutable_section_id=None):
        """Creates a stack of sections with an optional store for changes.

        :param sections_def: A list of Section or callables that returns an
            iterable of Section. This defines the Sections for the Stack and
            can be called repeatedly if needed.

        :param store: The optional Store where modifications will be
            recorded. If none is specified, no modifications can be done.

        :param mutable_section_id: The id of the MutableSection where changes
            are recorded. This requires the ``store`` parameter to be
            specified.
        """
        self.sections_def = sections_def
        self.store = store
        self.mutable_section_id = mutable_section_id

    def iter_sections(self):
        """Iterate all the defined sections."""
        # Ensuring lazy loading is achieved by delaying section matching (which
        # implies querying the persistent storage) until it can't be avoided
        # anymore by using callables to describe (possibly empty) section
        # lists.
        for sections in self.sections_def:
            for store, section in sections():
                yield store, section

    def get(self, name, expand=True, convert=True):
        """Return the *first* option value found in the sections.

        This is where we guarantee that sections coming from Store are loaded
        lazily: the loading is delayed until we need to either check that an
        option exists or get its value, which in turn may require to discover
        in which sections it can be defined. Both of these (section and option
        existence) require loading the store (even partially).

        :param name: The queried option.

        :param expand: Whether options references should be expanded.

        :param convert: Whether the option value should be converted from
            unicode (do nothing for non-registered options).

        :returns: The value of the option.
        """
        # FIXME: No caching of options nor sections yet -- vila 20110503
        value = None
        found_store = None  # Where the option value has been found
        # If the option is registered, it may provide additional info about
        # value handling
        try:
            opt = options.option_registry.get(name)
        except KeyError:
            # Not registered
            opt = None

        def expand_and_convert(val):
            # This may need to be called in different contexts if the value is
            # None or ends up being None during expansion or conversion.
            if val is not None:
                if expand:
                    val = self._expand_options_in_string(val)
                if opt is None:
                    val = found_store.unquote(val)
                elif convert:
                    val = opt.convert_from_unicode(found_store, val)
            return val

        # First of all, check if the environment can override the configuration
        # value
        if opt is not None and opt.override_from_env:
            value = opt.get_override()
            value = expand_and_convert(value)
        if value is None:
            for store, section in self.iter_sections():
                value = section.get(name)
                if value is not None:
                    found_store = store
                    break
            value = expand_and_convert(value)
            if opt is not None and value is None:
                # If the option is registered, it may provide a default value
                value = opt.get_default()
                value = expand_and_convert(value)
        return value

    def expand_options(self, string, env=None):
        """Expand option references in the string in the configuration context.

        :param string: The string containing option(s) to expand.

        :param env: An option dict defining additional configuration options or
            overriding existing ones.

        :returns: The expanded string.
        """
        return self._expand_options_in_string(string, env)

    def _expand_options_in_string(self, string, env=None, _refs=None):
        """Expand options in the string in the configuration context.

        :param string: The string to be expanded.

        :param env: An option dict defining additional configuration options or
            overriding existing ones.

        :param _refs: Private list (FIFO) containing the options being expanded
            to detect loops.

        :returns: The expanded string.
        """
        if string is None:
            # Not much to expand there
            return None
        if _refs is None:
            # What references are currently resolved (to detect loops)
            _refs = []
        result = string
        # We need to iterate until no more refs appear ({{foo}} will need two
        # iterations for example).
        expanded = True
        while expanded:
            expanded = False
            chunks = []
            for is_ref, chunk in iter_option_refs(result):
                if not is_ref:
                    chunks.append(chunk)
                else:
                    expanded = True
                    name = chunk[1:-1]
                    if name in _refs:
                        raise errors.OptionExpansionLoop(string, _refs)
                    _refs.append(name)
                    value = self._expand_option(name, env, _refs)
                    if value is None:
                        raise errors.ExpandingUnknownOption(name, string)
                    chunks.append(value)
                    _refs.pop()
            result = ''.join(chunks)
        return result

    def _expand_option(self, name, env, _refs):
        if env is not None and name in env:
            # Special case, values provided in env takes precedence over
            # anything else
            value = env[name]
        else:
            value = self.get(name, expand=False, convert=False)
            value = self._expand_options_in_string(value, env, _refs)
        return value

    def _get_mutable_section(self):
        """Get the MutableSection for the Stack.

        This is where we guarantee that the mutable section is lazily loaded:
        this means we won't load the corresponding store before setting a value
        or deleting an option. In practice the store will often be loaded but
        this helps catching some programming errors.
        """
        store = self.store
        section = store.get_mutable_section(self.mutable_section_id)
        return store, section

    def set(self, name, value):
        """Set a new value for the option."""
        store, section = self._get_mutable_section()
        section.set(name, store.quote(value))

    def remove(self, name):
        """Remove an existing option."""
        _, section = self._get_mutable_section()
        section.remove(name)

    def __repr__(self):
        # Mostly for debugging use
        return "<config.%s(%s)>" % (self.__class__.__name__, id(self))

    def get_shared_store(self, store):
        """Get a known shared store.

        Store urls uniquely identify them and are used to ensure a single copy
        is shared across all users.

        :param store: The store known to the caller.

        :returns: The store received if it's not a known one, an already known
            otherwise.
        """
        global _shared_stores_at_exit_installed
        the_stores = _shared_stores
        if not _shared_stores_at_exit_installed:
            import atexit

            def save_config_changes():
                for k, store in the_stores.items():
                    store.save_changes()

            atexit.register(save_config_changes)
            _shared_stores_at_exit_installed = True

        url = store.external_url()
        try:
            return the_stores[url]
        except KeyError:
            the_stores[url] = store
            return store


class MemoryStack(Stack):
    """A configuration stack defined from a string.

    This is mainly intended for tests and requires no disk resources.
    """

    def __init__(self, content=None):
        """Create an in-memory stack from a given content.

        It uses a single FileStore without a real file and support reading and
        writing options.

        :param content: The initial content of the store. If None, the store is
            not loaded and ``_load_from_string`` can and should be used if
            needed.
        """
        store = stores.FileStore('<string>')
        if content is not None:
            store._load_from_string(content)
        super(MemoryStack, self).__init__(
            [store.get_sections], store)
