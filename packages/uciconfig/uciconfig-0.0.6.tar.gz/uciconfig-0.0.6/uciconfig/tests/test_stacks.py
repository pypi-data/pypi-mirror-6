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


from uciconfig import (
    errors,
    options,
    registries,
    stacks,
    stores,
    tests,
)
from ucitests import (
    assertions,
    fixtures,
)


class TestSectionMatcher(unittest.TestCase):

    def setUp(self):
        super(TestSectionMatcher, self).setUp()
        fixtures.set_uniq_cwd(self)
        self.store = stores.FileStore('foo.conf')
        self.matcher = stacks.NameMatcher

    def test_no_matches_for_empty_stores(self):
        self.store._load_from_string('')
        matcher = self.matcher(self.store, '/bar')
        self.assertEquals([], list(matcher.get_sections()))

    def test_build_doesnt_load_store(self):
        self.matcher(self.store, '/bar')
        self.assertFalse(self.store.is_loaded())

    def get_matching_sections(self, name):
        self.store._load_from_string('''
[foo]
option=foo
[foo/baz]
option=foo/baz
[bar]
option=bar
''')
        matcher = self.matcher(self.store, name)
        return list(matcher.get_sections())

    def test_matching(self):
        sections = self.get_matching_sections('foo')
        assertions.assertLength(self, 1, sections)
        tests.assertSectionContent(self, ('foo', {'option': 'foo'}),
                                   sections[0])

    def test_not_matching(self):
        sections = self.get_matching_sections('baz')
        assertions.assertLength(self, 0, sections)


class TestNameMatcher(unittest.TestCase):

    def setUp(self):
        super(TestNameMatcher, self).setUp()
        self.matcher = stacks.NameMatcher
        # Any simple store is good enough
        fixtures.set_uniq_cwd(self)
        self.store = stores.FileStore('foo.conf')

    def get_matching_sections(self, name):
        self.store._load_from_string('''
[foo]
option=foo
[foo/baz]
option=foo/baz
[bar]
option=bar
''')
        matcher = self.matcher(self.store, name)
        return list(matcher.get_sections())

    def test_matching(self):
        sections = self.get_matching_sections('foo')
        assertions.assertLength(self, 1, sections)
        tests.assertSectionContent(self, ('foo', {'option': 'foo'}),
                                   sections[0])

    def test_not_matching(self):
        sections = self.get_matching_sections('baz')
        assertions.assertLength(self, 0, sections)


class TestPathSection(unittest.TestCase):

    def get_section(self, options, extra_path):
        section = stores.Section('foo', options)
        return stacks.PathSection(section, extra_path)

    def test_simple_option(self):
        section = self.get_section({'foo': 'bar'}, '')
        self.assertEquals('bar', section.get('foo'))

    def test_option_with_extra_path(self):
        section = self.get_section({'foo': 'bar/{basename}'},
                                   'baz')
        self.assertEquals('bar/baz', section.get('foo'))


class TestStartingPathMatcher(unittest.TestCase):

    def setUp(self):
        super(TestStartingPathMatcher, self).setUp()
        fixtures.set_uniq_cwd(self)
        # Any simple store is good enough
        self.store = stores.FileStore('foo.conf')

    def assertSectionIDs(self, expected, path, content):
        self.store._load_from_string(content)
        matcher = stacks.StartingPathMatcher(self.store, path)
        sections = list(matcher.get_sections())
        assertions.assertLength(self, len(expected), sections)
        self.assertEqual(expected, [section.id for _, section in sections])
        return sections

    def test_empty(self):
        self.assertSectionIDs([], '/', '')

    def test_matching_paths(self):
        self.assertSectionIDs(['/foo/bar', '/foo'],
                              '/foo/bar/baz', '''\
[/foo]
[/foo/bar]
''')

    def test_no_name_section_included_when_present(self):
        # Note that other tests will cover the case where the no-name section
        # is empty and as such, not included.
        sections = self.assertSectionIDs(['/foo/bar', '/foo', None],
                                         '/foo/bar/baz', '''\
option = defined so the no-name section exists
[/foo]
[/foo/bar]
''')
        self.assertEquals(['baz', 'bar/baz', '/foo/bar/baz'],
                          [s.locals['relpath'] for _, s in sections])

    def test_order_reversed(self):
        self.assertSectionIDs(['/foo/bar', '/foo'], '/foo/bar/baz', '''\
[/foo]
[/foo/bar]
''')

    def test_unrelated_section_excluded(self):
        self.assertSectionIDs(['/foo/bar', '/foo'], '/foo/bar/baz', '''\
[/foo]
[/foo/qux]
[/foo/bar]
''')

    def test_respect_order(self):
        self.assertSectionIDs(['/foo', '/foo/b', '/foo/bar/baz'],
                              '/foo/bar/baz', '''\
[/foo/bar/baz]
[/foo/qux]
[/foo/b]
[/foo]
''')


class TestBaseStackGet(unittest.TestCase):

    def setUp(self):
        super(TestBaseStackGet, self).setUp()
        fixtures.patch(self, options, 'option_registry',
                       options.OptionRegistry())

    def test_get_first_definition(self):
        store1 = stores.FileStore('<string>')
        store1._load_from_string('foo=bar')
        store2 = stores.FileStore('<string>')
        store2._load_from_string('foo=baz')
        conf = stacks.Stack([store1.get_sections, store2.get_sections])
        self.assertEqual('bar', conf.get('foo'))

    def test_get_with_registered_default_value(self):
        options.option_registry.register(options.Option('foo', 'foo help.',
                                                        default='bar'))
        conf_stack = stacks.Stack([])
        self.assertEqual('bar', conf_stack.get('foo'))

    def test_get_without_registered_default_value(self):
        options.option_registry.register(options.Option('foo', 'foo help.'))
        conf_stack = stacks.Stack([])
        self.assertEqual(None, conf_stack.get('foo'))

    def test_get_without_default_value_for_not_registered(self):
        conf_stack = stacks.Stack([])
        self.assertEqual(None, conf_stack.get('foo'))

    def test_get_for_empty_section_callable(self):
        conf_stack = stacks.Stack([lambda: []])
        self.assertEqual(None, conf_stack.get('foo'))

    def test_get_for_broken_callable(self):
        # Trying to use and invalid callable raises an exception on first use
        conf_stack = stacks.Stack([object])
        self.assertRaises(TypeError, conf_stack.get, 'foo')

    def test_get_registry_option_default_value(self):
        registry = registries.Registry()
        registry.register('bar', 'abc', 'Some help.')
        reg_opt = options.RegistryOption(
            'fooreg', 'A registry option.', registry, default='bar')
        options.option_registry.register(reg_opt)
        conf_stack = stacks.Stack([])
        self.assertEqual('abc', conf_stack.get('fooreg'))


class TestStackWithSimpleStore(unittest.TestCase):

    def setUp(self):
        super(TestStackWithSimpleStore, self).setUp()
        fixtures.patch(self, options, 'option_registry',
                       options.OptionRegistry())
        self.registry = options.option_registry

    def get_conf(self, content=None):
        return stacks.MemoryStack(content)

    def test_override_value_from_env(self):
        fixtures.override_env(self, 'FOO', None)
        self.registry.register(options.Option('foo', 'foo help.', default='b',
                                              override_from_env=['FOO']))
        fixtures.override_env(self, 'FOO', 'quux')
        # Env variable provides a default taking over the option one
        conf = self.get_conf('foo=store')
        self.assertEqual('quux', conf.get('foo'))

    def test_first_override_value_from_env_wins(self):
        fixtures.override_env(self, 'NO_VALUE', None)
        fixtures.override_env(self, 'FOO', None)
        fixtures.override_env(self, 'BAZ', None)
        self.registry.register(options.Option('foo', 'foo help.', default='b',
                                              override_from_env=['NO_VALUE',
                                                                 'FOO',
                                                                 'BAZ']))
        fixtures.override_env(self, 'FOO', 'foo')
        fixtures.override_env(self, 'BAZ', 'baz')
        # The first env var set wins
        conf = self.get_conf('foo=store')
        self.assertEqual('foo', conf.get('foo'))


class TestMemoryStack(unittest.TestCase):

    def test_get(self):
        conf = stacks.MemoryStack('foo=bar')
        self.assertEqual('bar', conf.get('foo'))

    def test_set(self):
        conf = stacks.MemoryStack('foo=bar')
        conf.set('foo', 'baz')
        self.assertEqual('baz', conf.get('foo'))

    def test_no_content(self):
        conf = stacks.MemoryStack()
        # No content means no loading
        self.assertFalse(conf.store.is_loaded())
        # A content can still be provided
        conf.store._load_from_string('foo=bar')
        self.assertEqual('bar', conf.get('foo'))

    # The two following tests are arguably testing the stores but stores do not
    # provide a way to set an option so we need a stack for that.
    def test_set_mark_dirty(self):
        stack = stacks.MemoryStack('')
        assertions.assertLength(self, 0, stack.store.dirty_sections)
        stack.set('foo', 'baz')
        assertions.assertLength(self, 1, stack.store.dirty_sections)
        self.assertTrue(stack.store._needs_saving())

    def test_remove_mark_dirty(self):
        stack = stacks.MemoryStack('foo=bar')
        assertions.assertLength(self, 0, stack.store.dirty_sections)
        stack.remove('foo')
        assertions.assertLength(self, 1, stack.store.dirty_sections)
        self.assertTrue(stack.store._needs_saving())


class TestStackIterSections(unittest.TestCase):

    def test_empty_stack(self):
        conf = stacks.Stack([])
        sections = list(conf.iter_sections())
        assertions.assertLength(self, 0, sections)

    def test_empty_store(self):
        store = stores.FileStore('<string>')
        store._load_from_string('')
        conf = stacks.Stack([store.get_sections])
        sections = list(conf.iter_sections())
        assertions.assertLength(self, 0, sections)

    def test_simple_store(self):
        store = stores.FileStore('<string>')
        store._load_from_string('foo=bar')
        conf = stacks.Stack([store.get_sections])
        tuples = list(conf.iter_sections())
        assertions.assertLength(self, 1, tuples)
        (found_store, found_section) = tuples[0]
        self.assertIs(store, found_store)

    def test_two_stores(self):
        store1 = stores.FileStore('<string>')
        store1._load_from_string('foo=bar')
        store2 = stores.FileStore('<string>')
        store2._load_from_string('bar=qux')
        conf = stacks.Stack([store1.get_sections, store2.get_sections])
        tuples = list(conf.iter_sections())
        assertions.assertLength(self, 2, tuples)
        self.assertIs(store1, tuples[0][0])
        self.assertIs(store2, tuples[1][0])


class TestStackGet(unittest.TestCase):

    def setUp(self):
        super(TestStackGet, self).setUp()
        self.conf = self.get_stack()

    def get_stack(self):
        return stacks.MemoryStack()

    def test_get_for_empty_stack(self):
        self.assertEqual(None, self.conf.get('foo'))


class TestStackGetWithConverter(unittest.TestCase):

    def setUp(self):
        super(TestStackGetWithConverter, self).setUp()
        fixtures.patch(self, options, 'option_registry',
                       options.OptionRegistry())
        self.registry = options.option_registry

    def get_conf(self, content=None):
        return stacks.MemoryStack(content)

    def register_bool_option(self, name, default=None, default_from_env=None):
        b = options.Option(name, 'A boolean.',
                           default=default, default_from_env=default_from_env,
                           from_unicode=options.bool_from_store)
        self.registry.register(b)

    def test_get_default_bool_None(self):
        self.register_bool_option('foo')
        conf = self.get_conf('')
        self.assertEqual(None, conf.get('foo'))

    def test_get_default_bool_True(self):
        self.register_bool_option('foo', 'True')
        conf = self.get_conf('')
        self.assertEqual(True, conf.get('foo'))

    def test_get_default_bool_False(self):
        self.register_bool_option('foo', False)
        conf = self.get_conf('')
        self.assertEqual(False, conf.get('foo'))

    def test_get_default_bool_False_as_string(self):
        self.register_bool_option('foo', 'False')
        conf = self.get_conf('')
        self.assertEqual(False, conf.get('foo'))

    def test_get_default_bool_from_env_converted(self):
        self.register_bool_option('foo', 'True', default_from_env=['FOO'])
        fixtures.override_env(self, 'FOO', 'False')
        conf = self.get_conf('')
        self.assertEqual(False, conf.get('foo'))

    def test_get_default_bool_when_conversion_fails(self):
        self.register_bool_option('foo', default='True')
        conf = self.get_conf('foo=invalid boolean')
        self.assertEqual(True, conf.get('foo'))

    def register_integer_option(self, name,
                                default=None, default_from_env=None):
        i = options.Option(name, 'An integer.',
                           default=default, default_from_env=default_from_env,
                           from_unicode=options.int_from_store)
        self.registry.register(i)

    def test_get_default_integer_None(self):
        self.register_integer_option('foo')
        conf = self.get_conf('')
        self.assertEqual(None, conf.get('foo'))

    def test_get_default_integer(self):
        self.register_integer_option('foo', 42)
        conf = self.get_conf('')
        self.assertEqual(42, conf.get('foo'))

    def test_get_default_integer_as_string(self):
        self.register_integer_option('foo', '42')
        conf = self.get_conf('')
        self.assertEqual(42, conf.get('foo'))

    def test_get_default_integer_from_env(self):
        self.register_integer_option('foo', default_from_env=['FOO'])
        fixtures.override_env(self, 'FOO', '18')
        conf = self.get_conf('')
        self.assertEqual(18, conf.get('foo'))

    def test_get_default_integer_when_conversion_fails(self):
        self.register_integer_option('foo', default='12')
        conf = self.get_conf('foo=invalid integer')
        self.assertEqual(12, conf.get('foo'))

    def register_list_option(self, name, default=None, default_from_env=None):
        l = options.ListOption(name, 'A list.', default=default,
                               default_from_env=default_from_env)
        self.registry.register(l)

    def test_get_default_list_None(self):
        self.register_list_option('foo')
        conf = self.get_conf('')
        self.assertEqual(None, conf.get('foo'))

    def test_get_default_list_empty(self):
        self.register_list_option('foo', '')
        conf = self.get_conf('')
        self.assertEqual([], conf.get('foo'))

    def test_get_default_list_from_env(self):
        self.register_list_option('foo', default_from_env=['FOO'])
        fixtures.override_env(self, 'FOO', '')
        conf = self.get_conf('')
        self.assertEqual([], conf.get('foo'))

    def test_get_with_list_converter_no_item(self):
        self.register_list_option('foo', None)
        conf = self.get_conf('foo=,')
        self.assertEqual([], conf.get('foo'))

    def test_get_with_list_converter_many_items(self):
        self.register_list_option('foo', None)
        conf = self.get_conf('foo=m,o,r,e')
        self.assertEqual(['m', 'o', 'r', 'e'], conf.get('foo'))

    @unittest.skip('Quoting not supported')
    def test_get_with_list_converter_embedded_spaces_many_items(self):
        self.register_list_option('foo', None)
        conf = self.get_conf('foo=" bar", "baz "')
        self.assertEqual([' bar', 'baz '], conf.get('foo'))

    def test_get_with_list_converter_stripped_spaces_many_items(self):
        self.register_list_option('foo', None)
        conf = self.get_conf('foo= bar ,  baz ')
        self.assertEqual(['bar', 'baz'], conf.get('foo'))


class TestStackSet(unittest.TestCase):

    def setUp(self):
        super(TestStackSet, self).setUp()
        fixtures.set_uniq_cwd(self)

    def get_stack(self):
        return stacks.MemoryStack()

    def test_simple_set(self):
        conf = self.get_stack()
        self.assertEqual(None, conf.get('foo'))
        conf.set('foo', 'baz')
        # Did we get it back ?
        self.assertEqual('baz', conf.get('foo'))

    def test_set_creates_a_new_section(self):
        conf = self.get_stack()
        assertions.assertLength(self, 0, list(conf.iter_sections()))
        conf.set('foo', 'baz')
        self.assertEqual, 'baz', conf.get('foo')
        assertions.assertLength(self, 1, list(conf.iter_sections()))


class TestStackRemove(unittest.TestCase):

    def setUp(self):
        super(TestStackRemove, self).setUp()
        fixtures.set_uniq_cwd(self)

    def get_stack(self):
        return stacks.MemoryStack()

    def test_remove_existing(self):
        conf = self.get_stack()
        conf.set('foo', 'bar')
        self.assertEqual('bar', conf.get('foo'))
        conf.remove('foo')
        # Did we get it back ?
        self.assertEqual(None, conf.get('foo'))

    def test_remove_unknown(self):
        conf = self.get_stack()
        self.assertRaises(KeyError, conf.remove, 'I_do_not_exist')


class TestIterOptionRefs(unittest.TestCase):
    """iter_option_refs is a bit unusual, document some cases."""

    def assertRefs(self, expected, string):
        self.assertEqual(expected, list(stacks.iter_option_refs(string)))

    def test_empty(self):
        self.assertRefs([(False, '')], '')

    def test_no_refs(self):
        self.assertRefs([(False, 'foo bar')], 'foo bar')

    def test_single_ref(self):
        self.assertRefs([(False, ''), (True, '{foo}'), (False, '')], '{foo}')

    def test_broken_ref(self):
        self.assertRefs([(False, '{foo')], '{foo')

    def test_embedded_ref(self):
        self.assertRefs([(False, '{'), (True, '{foo}'), (False, '}')],
                        '{{foo}}')

    def test_two_refs(self):
        self.assertRefs([(False, ''), (True, '{foo}'),
                         (False, ''), (True, '{bar}'),
                         (False, ''), ],
                        '{foo}{bar}')

    def test_newline_in_refs_are_not_matched(self):
        self.assertRefs([(False, '{\nxx}{xx\n}{{\n}}')], '{\nxx}{xx\n}{{\n}}')


class TestStackExpandOptions(unittest.TestCase):

    def setUp(self):
        super(TestStackExpandOptions, self).setUp()
        fixtures.set_uniq_cwd(self)
        fixtures.patch(self, options, 'option_registry',
                       options.OptionRegistry())
        self.registry = options.option_registry
        store = stores.FileStore('foo.conf')
        self.conf = stacks.Stack([store.get_sections], store)

    def assertExpansion(self, expected, string, env=None):
        self.assertEqual(expected, self.conf.expand_options(string, env))

    def test_no_expansion(self):
        self.assertExpansion('foo', 'foo')

    def test_expand_default_value(self):
        self.conf.store._load_from_string('bar=baz')
        self.registry.register(options.Option('foo',  'foo help.',
                                              default='{bar}'))
        self.assertEqual('baz', self.conf.get('foo', expand=True))

    def test_expand_default_from_env(self):
        self.conf.store._load_from_string('bar=baz')
        self.registry.register(options.Option('foo', 'foo help.',
                                              default_from_env=['FOO']))
        fixtures.override_env(self, 'FOO', '{bar}')
        self.assertEqual('baz', self.conf.get('foo', expand=True))

    def test_expand_default_on_failed_conversion(self):
        self.conf.store._load_from_string('baz=bogus\nbar=42\nfoo={baz}')
        self.registry.register(
            options.Option('foo', 'foo help.', default='{bar}',
                           from_unicode=options.int_from_store))
        self.assertEqual(42, self.conf.get('foo', expand=True))

    def test_env_adding_options(self):
        self.assertExpansion('bar', '{foo}', {'foo': 'bar'})

    def test_env_overriding_options(self):
        self.conf.store._load_from_string('foo=baz')
        self.assertExpansion('bar', '{foo}', {'foo': 'bar'})

    def test_simple_ref(self):
        self.conf.store._load_from_string('foo=xxx')
        self.assertExpansion('xxx', '{foo}')

    def test_unknown_ref(self):
        self.assertRaises(errors.ExpandingUnknownOption,
                          self.conf.expand_options, '{foo}')

    def test_indirect_ref(self):
        self.conf.store._load_from_string('''
foo=xxx
bar={foo}
''')
        self.assertExpansion('xxx', '{bar}')

    def test_embedded_ref(self):
        self.conf.store._load_from_string('''
foo=xxx
bar=foo
''')
        self.assertExpansion('xxx', '{{bar}}')

    def test_simple_loop(self):
        self.conf.store._load_from_string('foo={foo}')
        with self.assertRaises(errors.OptionExpansionLoop) as cm:
            self.conf.expand_options('{foo}')
        self.assertEqual('{foo}', cm.exception.string)
        self.assertEqual('foo', cm.exception.refs)
        self.assertEqual('''Loop involving u'foo' while expanding "{foo}".''',
                         unicode(cm.exception))

    def test_indirect_loop(self):
        self.conf.store._load_from_string('''
foo={bar}
bar={baz}
baz={foo}''')
        with self.assertRaises(errors.OptionExpansionLoop) as cm:
            self.conf.expand_options('{foo}')
        self.assertEqual('foo->bar->baz', cm.exception.refs)
        self.assertEqual('{foo}', cm.exception.string)

    def test_list(self):
        self.conf.store._load_from_string('''
foo=start
bar=middle
baz=end
list={foo},{bar},{baz}
''')
        self.registry.register(
            options.ListOption('list', 'A list.'))
        self.assertEqual(['start', 'middle', 'end'],
                         self.conf.get('list', expand=True))

    def test_cascading_list(self):
        self.conf.store._load_from_string('''
foo=start,{bar}
bar=middle,{baz}
baz=end
list={foo}
''')
        self.registry.register(options.ListOption('list', 'A list.'))
        # Register an intermediate option as a list to ensure no conversion
        # happen while expanding. Conversion should only occur for the original
        # option ('list' here).
        self.registry.register(options.ListOption('baz', 'A list.'))
        self.assertEqual(['start', 'middle', 'end'],
                         self.conf.get('list', expand=True))

    def test_pathologically_hidden_list(self):
        self.conf.store._load_from_string('''
foo=bin
bar=go
start={foo
middle=},{
end=bar}
hidden={start}{middle}{end}
''')
        # What matters is what the registration says, the conversion happens
        # only after all expansions have been performed
        self.registry.register(options.ListOption('hidden', 'hidden help.'))
        self.assertEqual(['bin', 'go'],
                         self.conf.get('hidden', expand=True))


class TestStackExpandSectionLocals(unittest.TestCase):
    """Test section local options expansion under various setups."""

    def setUp(self):
        super(TestStackExpandSectionLocals, self).setUp()
        fixtures.set_uniq_cwd(self)

    def get_sections_stack(self, section_path, content):
        """Build a stack from a given content.

        This selects sections with StartingPathMatcher so the section local
        optioins can be expanded.
        """
        store = stores.FileStore('sections.conf')
        store._load_from_string(content)
        store.save()

        class SectionsStack(stacks.Stack):
            """A stack from a store with sections."""

            def __init__(self, store, path):
                super(SectionsStack, self).__init__(
                    [stacks.StartingPathMatcher(store, path).get_sections])

        return SectionsStack(store, section_path)

    def test_expand_locals_empty(self):
        stack = self.get_sections_stack('/home/user/project/', '''
[/home/user/project]
base = {basename}
rel = {relpath}
''')
        self.assertEquals('', stack.get('base', expand=True))
        self.assertEquals('', stack.get('rel', expand=True))

    def test_expand_basename_locally(self):
        stack = self.get_sections_stack('/home/user/project/dir', '''
[/home/user/project]
bfoo = {basename}
''')
        self.assertEquals('dir', stack.get('bfoo', expand=True))

    def test_expand_basename_locally_longer_path(self):
        stack = self.get_sections_stack('/home/user/project/dir/subdir', '''
[/home/user]
bfoo = {basename}
''')
        self.assertEquals('subdir', stack.get('bfoo', expand=True))

    def test_expand_relpath_locally(self):
        stack = self.get_sections_stack('/home/user/project/dir', '''
[/home/user/project]
lfoo = loc-foo/{relpath}
''')
        self.assertEquals('loc-foo/dir', stack.get('lfoo', expand=True))

    def test_locals_dont_leak(self):
        """Ensure we chose the right local across several sections."""
        stack = self.get_sections_stack('/home/user/project/dir', '''
[/home/user]
lfoo = loc-foo/{relpath}
[/home/user/project]
lfoo = loc-foo/{relpath}
''')
        self.assertEquals('loc-foo/dir', stack.get('lfoo', expand=True))
        stack = self.get_sections_stack('/home/user/bar/baz', '''
[/home/user]
lfoo = loc-foo/{relpath}
[/home/user/project]
lfoo = loc-foo/{relpath}
''')
        self.assertEquals('loc-foo/bar/baz', stack.get('lfoo', expand=True))

    def get_2stores_stack(self, section_path,
                          sections_content, no_name_content):
        """Build a stack from two stores with a given content.

        Two stores are built, one with a no-name section, the other with
        several sections.

        The stack will use StartingPathMatcher on the sections store and
        NameMatcher on the no-name one.

        The section local options only exist on the sections store.
        """
        n_store = stores.FileStore('no-name.conf')
        n_store._load_from_string(no_name_content)
        n_store.save()

        s_store = stores.FileStore('sections.conf')
        s_store._load_from_string(sections_content)
        s_store.save()

        class TwoStoresStack(stacks.Stack):
            """A stack from a store with only the no-name section."""

            def __init__(self, s_store, n_store):
                super(TwoStoresStack, self).__init__(
                    [stacks.StartingPathMatcher(s_store,
                                                section_path).get_sections,
                     stacks.NameMatcher(n_store, None).get_sections])

        return TwoStoresStack(s_store, n_store)

    def test_expand_relpath_unknonw_in_global(self):
        stack = self.get_2stores_stack('/home/user/project/dir',
                                       '',
                                       '''
 gfoo = {relpath}
''')
        self.assertRaises(errors.ExpandingUnknownOption,
                          stack.get, 'gfoo', expand=True)

    def test_expand_local_option_locally(self):
        stack = self.get_2stores_stack('/home/user/project/dir',
                                       '''
[/home/user/project]
lfoo = loc-foo/{relpath}
lbar = {gbar}
''',
                                       '''
gfoo = {lfoo}
gbar = glob-bar
''')
        self.assertEquals('glob-bar', stack.get('lbar', expand=True))
        self.assertEquals('loc-foo/dir', stack.get('gfoo', expand=True))


class TestStackCrossSectionsExpand(unittest.TestCase):

    def setUp(self):
        super(TestStackCrossSectionsExpand, self).setUp()
        fixtures.set_uniq_cwd(self)

    def get_config(self, path, string):
        if string is None:
            string = ''

        class PathsStack(stacks.Stack):

            def __init__(self, path):
                store = stores.FileStore('foo.conf')
                super(PathsStack, self).__init__(
                    [stacks.StartingPathMatcher(store, path).get_sections],
                    store)

        c = PathsStack(path)
        c.store._load_from_string(string)
        return c

    def test_dont_cross_unrelated_section(self):
        c = self.get_config('/another/path', '''
[/one/path]
foo = hello
bar = {foo}/2

[/another/path]
bar = {foo}/2
''')
        with self.assertRaises(errors.ExpandingUnknownOption) as cm:
            c.get('bar', expand=True)
        self.assertEqual(
            '''Option foo is not defined while expanding "{foo}/2".''',
            unicode(cm.exception))

    def test_cross_related_sections(self):
        c = self.get_config('/project/branch/path', '''
[/project]
foo = qu

[/project/branch/path]
bar = {foo}ux
''')
        self.assertEqual('quux', c.get('bar', expand=True))


class TestStackCrossStoresExpand(unittest.TestCase):

    def setUp(self):
        super(TestStackCrossStoresExpand, self).setUp()
        fixtures.set_uniq_cwd(self)

    def test_cross_global_locations(self):
        f_store = stores.FileStore('foo.conf')
        f_store._load_from_string('''
[/here]
lfoo = loc-foo
lbar = {gbar}
''')
        f_store.save()
        b_store = stores.FileStore('bar.conf')
        b_store._load_from_string('''
[/]
gfoo = {lfoo}
gbar = glob-bar
''')
        b_store.save()

        class Stack(stacks.Stack):

            def __init__(self, path):
                spm = stacks.StartingPathMatcher
                super(Stack, self).__init__(
                    [spm(f_store, path).get_sections,
                     spm(b_store, path).get_sections])

        stack = Stack('/here')
        self.assertEqual('glob-bar', stack.get('lbar', expand=True))
        self.assertEqual('loc-foo', stack.get('gfoo', expand=True))


class TestSharedStores(unittest.TestCase):

    def test_store_is_shared(self):

        class Stack(stacks.Stack):

            def __init__(self):
                store = self.get_shared_store(stores.FileStore('foo.conf'))
                super(Stack, self).__init__(
                    [store.get_sections],
                    store)

        g1 = Stack()
        g2 = Stack()
        # The two stacks share the same store
        self.assertIs(g1.store, g2.store)
