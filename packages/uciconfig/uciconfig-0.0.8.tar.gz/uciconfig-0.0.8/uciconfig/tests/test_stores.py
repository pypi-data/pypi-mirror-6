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
import unittest
import warnings


from uciconfig import (
    errors,
    stores,
    tests,
)
from ucitests import (
    assertions,
    fixtures,
)


class TestSection(unittest.TestCase):

    def test_get_a_value(self):
        a_dict = dict(foo='bar')
        section = stores.Section('myID', a_dict)
        self.assertEquals('bar', section.get('foo'))

    def test_get_unknown_option(self):
        a_dict = dict()
        section = stores.Section(None, a_dict)
        self.assertEquals('out of thin air',
                          section.get('foo', 'out of thin air'))

    def test_options_is_shared(self):
        a_dict = dict()
        section = stores.Section(None, a_dict)
        self.assertIs(a_dict, section.options)


class TestMutableSection(unittest.TestCase):

    def get_section(self, opts):
        return stores.MutableSection('myID', opts)

    def test_set(self):
        a_dict = dict(foo='bar')
        section = self.get_section(a_dict)
        section.set('foo', 'new_value')
        self.assertEquals('new_value', section.get('foo'))
        # The change appears in the shared section
        self.assertEquals('new_value', a_dict.get('foo'))
        # We keep track of the change
        self.assertTrue('foo' in section.orig)
        self.assertEquals('bar', section.orig.get('foo'))

    def test_set_preserve_original_once(self):
        a_dict = dict(foo='bar')
        section = self.get_section(a_dict)
        section.set('foo', 'first_value')
        section.set('foo', 'second_value')
        # We keep track of the original value
        self.assertTrue('foo' in section.orig)
        self.assertEquals('bar', section.orig.get('foo'))

    def test_remove(self):
        a_dict = dict(foo='bar')
        section = self.get_section(a_dict)
        section.remove('foo')
        # We get None for unknown options via the default value
        self.assertEquals(None, section.get('foo'))
        # Or we just get the default value
        self.assertEquals('unknown', section.get('foo', 'unknown'))
        self.assertFalse('foo' in section.options)
        # We keep track of the deletion
        self.assertTrue('foo' in section.orig)
        self.assertEquals('bar', section.orig.get('foo'))

    def test_remove_new_option(self):
        a_dict = dict()
        section = self.get_section(a_dict)
        section.set('foo', 'bar')
        section.remove('foo')
        self.assertFalse('foo' in section.options)
        # The option didn't exist initially so it we need to keep track of it
        # with a special value
        self.assertTrue('foo' in section.orig)
        self.assertEquals(stores._NewlyCreatedOption, section.orig['foo'])


class TestFileStore(unittest.TestCase):

    def get_store(self):
        return stores.FileStore('foo.conf')

    def test_id(self):
        store = self.get_store()
        self.assertIsNot(None, store.id)

    def test_loading_unknown_file_fails(self):
        store = self.get_store()
        with self.assertRaises(errors.NoSuchFile):
            store.load()

    def test_invalid_content(self):
        store = self.get_store()
        self.assertFalse(store.is_loaded())
        with self.assertRaises(errors.InvalidSyntax) as cm:
            store._load_from_string('this is invalid !')
        self.assertEqual('foo.conf(1): Not a section nor an option.',
                         repr(cm.exception))
        # And the load failed
        self.assertFalse(store.is_loaded())


class TestReadOnlyFileStore(unittest.TestCase):

    def get_store(self):
        return stores.FileStore('foo.conf')

    def test_building_delays_load(self):
        store = self.get_store()
        self.assertEquals(False, store.is_loaded())
        store._load_from_string('')
        self.assertEquals(True, store.is_loaded())

    def test_get_no_sections_for_empty(self):
        store = self.get_store()
        store._load_from_string('')
        self.assertEquals([], list(store.get_sections()))

    def test_get_default_section(self):
        store = self.get_store()
        store._load_from_string('foo=bar')
        sections = list(store.get_sections())
        assertions.assertLength(self, 1, sections)
        tests.assertSectionContent(self, (None, {'foo': 'bar'}), sections[0])

    def test_get_named_section(self):
        store = self.get_store()
        store._load_from_string('[baz]\nfoo=bar')
        sections = list(store.get_sections())
        assertions.assertLength(self, 1, sections)
        tests.assertSectionContent(self, ('baz', {'foo': 'bar'}), sections[0])

    def test_load_from_string_fails_for_non_empty_store(self):
        store = self.get_store()
        store._load_from_string('foo=bar')
        self.assertRaises(AssertionError, store._load_from_string, 'bar=baz')


class TestFileStoreContent(unittest.TestCase):
    """Simulate loading a config store with content of various encodings.

    All files produced have an utf8 content.

    Users may modify them manually and end up with a file that can't be
    loaded. We need to issue proper error messages in this case.
    """

    invalid_utf8_char = b'\xff'

    def setUp(self):
        super(TestFileStoreContent, self).setUp()
        fixtures.set_uniq_cwd(self)

    def test_load_utf8(self):
        """Ensure we can load an utf8-encoded file."""
        # Store the raw content in the config file
        with open('foo.conf', 'wb') as f:
            f.write('user=b\N{Euro Sign}ar'.encode('utf8'))
        store = stores.FileStore('foo.conf')
        store.load()
        sections = list(store.get_sections())
        assertions.assertLength(self, 1, sections)
        s, section = sections[0]
        self.assertIs(store, s)
        self.assertEqual('b\N{Euro Sign}ar', section.get('user'))

    def test_load_non_ascii(self):
        """Ensure we display a proper error on non-ascii, non utf-8 content."""
        with open('foo.conf', 'wb') as f:
            f.write(b'user=foo\n#' + self.invalid_utf8_char + b'\n')
        store = stores.FileStore('foo.conf')
        with self.assertRaises(errors.InvalidContent):
            store.load()

    def test_load_erroneous_content(self):
        """Ensure we display a proper error on content that can't be parsed."""
        with open('foo.conf', 'w') as f:
            f.write('[open_section\n')
        store = stores.FileStore('foo.conf')
        with self.assertRaises(errors.InvalidSyntax):
            store.load()

    def test_load_permission_denied(self):
        """Ensure we get warned when trying to load an inaccessible file."""
        with open('foo.conf', 'w') as f:
            f.write('')
        os.chmod('foo.conf', 0o000)
        self.addCleanup(os.chmod, 'foo.conf', 0o644)
        store = stores.FileStore('foo.conf')
        with warnings.catch_warnings(record=True) as wcm:
            with self.assertRaises(errors.PermissionDenied):
                store.load()
        self.assertEqual('Permission denied while trying to load'
                         ' configuration store foo.conf.',
                         str(wcm[0].message))


class TestMutableStore(unittest.TestCase):

    def setUp(self):
        super(TestMutableStore, self).setUp()
        fixtures.set_uniq_cwd(self)

    def get_store(self):
        return stores.FileStore('foo.conf')

    def has_store(self, store):
        return os.access(store.path, os.F_OK)

    def test_save_empty_creates_no_file(self):
        store = self.get_store()
        store.save()
        self.assertEquals(False, self.has_store(store))

    def test_mutable_section_shared(self):
        store = self.get_store()
        store._load_from_string('foo=bar\n')
        section1 = store.get_mutable_section(None)
        section2 = store.get_mutable_section(None)
        # If we get different sections, different callers won't share the
        # modification
        self.assertIs(section1, section2)

    def test_save_emptied_succeeds(self):
        store = self.get_store()
        store._load_from_string('foo=bar\n')
        section = store.get_mutable_section(None)
        section.remove('foo')
        store.save()
        self.assertEquals(True, self.has_store(store))
        modified_store = self.get_store()
        sections = list(modified_store.get_sections())
        assertions.assertLength(self, 0, sections)

    def test_save_with_content_succeeds(self):
        store = self.get_store()
        store._load_from_string('foo=bar\n')
        self.assertEquals(False, self.has_store(store))
        store.save()
        self.assertEquals(True, self.has_store(store))
        modified_store = self.get_store()
        sections = list(modified_store.get_sections())
        assertions.assertLength(self, 1, sections)
        tests.assertSectionContent(self, (None, {'foo': 'bar'}), sections[0])

    def test_set_option_in_empty_store(self):
        store = self.get_store()
        section = store.get_mutable_section(None)
        section.set('foo', 'bar')
        store.save()
        modified_store = self.get_store()
        sections = list(modified_store.get_sections())
        assertions.assertLength(self, 1, sections)
        tests.assertSectionContent(self, (None, {'foo': 'bar'}), sections[0])

    def test_set_option_in_default_section(self):
        store = self.get_store()
        section = store.get_mutable_section(None)
        section.set('foo', 'bar')
        store.save()
        modified_store = self.get_store()
        sections = list(modified_store.get_sections())
        assertions.assertLength(self, 1, sections)
        tests.assertSectionContent(self, (None, {'foo': 'bar'}), sections[0])

    def test_set_option_in_named_section(self):
        store = self.get_store()
        store._load_from_string('')
        section = store.get_mutable_section('baz')
        section.set('foo', 'bar')
        store.save()
        modified_store = self.get_store()
        sections = list(modified_store.get_sections())
        assertions.assertLength(self, 1, sections)


class TestRoundTripping(unittest.TestCase):

    def setUp(self):
        super(TestRoundTripping, self).setUp()
        fixtures.set_uniq_cwd(self)
        self.store = stores.FileStore('foo.conf')

    def assertRoundTrip(self, content):
        self.store._load_from_string(content)
        self.store.save()
        with open(self.store.path) as f:
            new_content = f.read()
        assertions.assertMultiLineAlmostEqual(self, content, new_content)

    def test_raw(self):
        self.assertRoundTrip('''\
a = b
[s1]
c = d
[s2]
e = x
''')

    def test_with_comments(self):
        self.assertRoundTrip('''\
# Initial comment
a = b # And a comment
# section comment
[src] # another section comment
c = d
''')
