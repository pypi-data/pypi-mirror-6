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
"""Configuration stores contains key/value definitions.

They may define a single level of sections, each of which containing key/value
definitions.
"""

from __future__ import unicode_literals

import collections
import errno
import io
import warnings

from uciconfig import (
    errors,
    parsers,
)


class Section(object):
    """A section defines a dict of option name => value.

    This is merely a read-only dict which can add some knowledge about the
    options. It is *not* a python dict object though and doesn't try to mimic
    its API.
    """

    def __init__(self, section_id, options):
        self.id = section_id
        # We re-use the dict-like object received
        self.options = options

    def get(self, name, default=None, expand=True):
        return self.options.get(name, default)

    def iter_option_names(self):
        for k in self.options.iterkeys():
            yield k

    def __repr__(self):
        # Mostly for debugging purposes
        return "<stores.%s id=%s>" % (self.__class__.__name__, self.id)


_NewlyCreatedOption = object()
"""Was the option created during the MutableSection lifetime"""
_DeletedOption = object()
"""Was the option deleted during the MutableSection lifetime"""


class MutableSection(Section):
    """A section allowing changes and keeping track of the original values."""

    def __init__(self, section_id, options):
        super(MutableSection, self).__init__(section_id, options)
        self.reset_changes()

    def set(self, name, value):
        if name not in self.options:
            # This is a new option
            self.orig[name] = _NewlyCreatedOption
        elif name not in self.orig:
            self.orig[name] = self.get(name, None)
        self.options[name] = value

    def remove(self, name):
        if name not in self.orig and name in self.options:
            self.orig[name] = self.get(name, None)
        del self.options[name]

    def reset_changes(self):
        self.orig = {}

    def apply_changes(self, dirty, store):
        """Apply option value changes.

        ``self`` has been reloaded from the persistent storage. ``dirty``
        contains the changes made since the previous loading.

        :param dirty: the mutable section containing the changes.

        :param store: the store containing the section
        """
        for k, expected in dirty.orig.iteritems():
            actual = dirty.get(k, _DeletedOption)
            if actual is _DeletedOption:
                if k in self.options:
                    self.remove(k)
            else:
                self.set(k, actual)
        # No need to keep track of these changes
        self.reset_changes()


class FileStore(object):
    """A configuration store using a local file storage.

    The file content must be utf8 encoded.

    :cvar readonly_section_class: The class used to create read-only sections.

    :cvar mutable_section_class: The calss used to create mutable sections.
    """

    readonly_section_class = Section
    mutable_section_class = MutableSection

    def __init__(self, path):
        """A Store using a file on disk.

        :param path: The config file path.
        """
        super(FileStore, self).__init__()
        self.path = path
        self.sections = collections.OrderedDict()
        # Daughter classes can use a more specific id
        self.id = path
        # Which sections need to be saved (by section id). We use a dict here
        # so the dirty sections can be shared by multiple callers.
        self.dirty_sections = {}
        self._loaded = False

    def is_loaded(self):
        return self._loaded

    def unload(self):
        self._loaded = False
        self.dirty_sections = {}

    def _load_content(self):
        """Load the config file bytes.

        :return: Unicode string.
        """
        try:
            with io.open(self.path, encoding='utf8') as f:
                return f.read()
        except UnicodeDecodeError:
            raise errors.InvalidContent(self.path)
        except IOError as e:
            if e.errno == errno.EACCES:
                warnings.warn('Permission denied while trying to load'
                              ' configuration store {}.'
                              .format(self.external_url()))
                raise errors.PermissionDenied(self.path)
            elif e.errno in (errno.ENOENT, errno.ENOTDIR):
                raise errors.NoSuchFile(self.path)
            else:
                raise

    def _save_content(self, content):
        """Save the config file bytes.

        This should be provided by subclasses

        :param content: Config file unicode string to write
        """
        with io.open(self.path, 'w', encoding='utf8') as f:
            f.write(content)

    def load(self):
        """Load the store from the associated file."""
        if self.is_loaded():
            return
        content = self._load_content()
        self._load_from_string(content)

    def _load_from_string(self, text):
        """Create a config store from a string.

        :param text: A unicode string representing the file content.
        """
        if self.is_loaded():
            raise AssertionError('Already loaded')

        parser = parsers.Parser()
        tokens = parser.parse_config(self.path, text)
        for section in parser.make_sections(tokens):
            self.sections[section.name] = section
        self._loaded = True

    def _needs_saving(self):
        for s in self.dirty_sections.values():
            if s.orig:
                # At least one dirty section contains a modification
                return True
        return False

    # FIXME: Needs more testing -- vila 1014-01-13
    def apply_changes(self, dirty_sections):
        """Apply changes from dirty sections while checking for coherency.

        The Store content is discarded and reloaded from persistent storage to
        acquire up-to-date values.

        Dirty sections are MutableSection which kept track of the value they
        are expected to update.
        """
        # We need an up-to-date version from the persistent storage, unload the
        # store. The reload will occur when needed (triggered by the first
        # get_mutable_section() call below.
        self.unload()
        # Apply the changes from the preserved dirty sections
        for section_id, dirty in dirty_sections.iteritems():
            clean = self.get_mutable_section(section_id)
            clean.apply_changes(dirty, self)
        # Everything is clean now
        self.dirty_sections = {}

    # FIXME: Needs more testing -- vila 1014-01-13
    def save_changes(self):
        if not self.is_loaded():
            # Nothing to save
            return
        if not self._needs_saving():
            return
        # Preserve the current version
        dirty_sections = dict(self.dirty_sections.items())
        self.apply_changes(dirty_sections)
        # Save to the persistent storage
        self.save()

    def save(self):
        if not self.is_loaded():
            # Nothing to save
            return
        chunks = []
        for section in self.sections.values():
            chunks.append(section.serialize())
        self._save_content(''.join(chunks))

    def get_sections(self):
        """Get the section in the file order.

        :returns: An iterable of (store, section).
        """
        # We need a loaded store
        try:
            self.load()
        except (errors.NoSuchFile, errors.PermissionDenied):
            # If the file can't be read, there is no sections
            return
        for section_name in self.sections.keys():
            yield (self,
                   self.readonly_section_class(section_name,
                                               self.sections[section_name]))

    def get_mutable_section(self, section_id=None):
        # We need a loaded store
        try:
            self.load()
        except errors.NoSuchFile:
            # The file doesn't exist, let's pretend it was empty
            self._load_from_string('')
        if section_id in self.dirty_sections:
            # We already created a mutable section for this id
            return self.dirty_sections[section_id]
        section = self.sections.get(section_id, None)
        if section is None:
            section = parsers.Section(section_id)
            self.sections[section_id] = section
        mutable_section = self.mutable_section_class(section_id, section)
        # All mutable sections can become dirty
        self.dirty_sections[section_id] = mutable_section
        return mutable_section

    def quote(self, value):
        # We don't support quoting for now
        return value

    def unquote(self, value):
        # We don't support quoting for now
        return value

    def external_url(self):
        return self.path
