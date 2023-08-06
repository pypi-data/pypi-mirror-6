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

import unittest


from uciconfig import (
    errors,
    parsers,
)


# Some aliases to make tests shorter
SD = parsers.SectionDefinition
OD = parsers.OptionDefinition


def assertTokens(test, expected, to_parse):
    test.assertEqual(expected,
                     test.parser.parse_config('<string>', to_parse))


class TestParseConfigEdgeCases(unittest.TestCase):

    def setUp(self):
        super(TestParseConfigEdgeCases, self).setUp()
        self.parser = parsers.Parser()

    def test_empty(self):
        assertTokens(self, [], '')

    def test_almost_empty(self):
        # Empty lines or lines containing only spaces are ignored
        assertTokens(self, [], ' \n   \n\n   \n   ')

    def test_invalid(self):
        with self.assertRaises(errors.InvalidSyntax):
            self.parser.parse_config('<string>', 'whatever')


class TestParseKeyValues(unittest.TestCase):

    def setUp(self):
        super(TestParseKeyValues, self).setUp()
        self.parser = parsers.Parser()

    def test_single_key_value(self):
        assertTokens(self, [SD(None), OD('a', 'b')], 'a=b')

    def test_single_key_value_stripping_spaces(self):
        assertTokens(self, [SD(None), OD('a', 'b')], ' a = b ')

    def test_empty_value(self):
        assertTokens(self, [SD(None), OD('a', '')], 'a=')

    def test_pre_comment(self):
        assertTokens(self, [SD(None), OD('a', 'b', '# Define a\n')],
                     '# Define a\na=b')

    def test_post_comment(self):
        # The comment collect even the preceding spaces as they are not part of
        # the value
        assertTokens(self, [SD(None), OD('a', 'b', None, ' # b is good\n')],
                     'a=b # b is good\n')

    def test_several_options(self):
        assertTokens(self, [SD(None),
                            OD('a', 'b'),
                            OD('c', 'd', '# c now\n', ' # c is better\n')],
                     'a=b\n# c now\nc=d # c is better\n')


class TestParseSections(unittest.TestCase):

    def setUp(self):
        super(TestParseSections, self).setUp()
        self.parser = parsers.Parser()

    def test_empty_section(self):
        assertTokens(self, [SD('s')], '[s]')

    def test_empty_section_name(self):
        with self.assertRaises(errors.SectionEmptyName):
            self.parser.parse_config('<string>', '[]')

    def test_pre_comment(self):
        assertTokens(self, [SD('s', '  # Empty section\n')],
                     '  # Empty section\n[s]')

    def test_post_comment(self):
        assertTokens(self, [SD('s', None, ' # It is empty\n')],
                     '[s] # It is empty\n')


class TestSerializeSection(unittest.TestCase):

    def test_serialize_empty(self):
        sect = parsers.Section(None)
        self.assertEqual('', sect.serialize())

    def test_single_option(self):
        sect = parsers.Section(None)
        sect.add('foo', 'bar', '# This is foo\n', ' # Set to bar\n')
        self.assertEqual('''# This is foo
foo = bar # Set to bar
''',
                         sect.serialize())

    def test_single_option_in_named_section(self):
        sect = parsers.Section('sect', '# This is sect\n # A simple section\n',
                               ' # Just saying\n')
        sect.add('foo', 'bar', '# This is foo\n', ' # Set to bar\n')
        self.assertEqual('''# This is sect
 # A simple section
[sect] # Just saying
# This is foo
foo = bar # Set to bar
''',
                         sect.serialize())

    def test_several_options(self):
        sect = parsers.Section(None)
        sect.add('foo', 'bar', '# This is foo\n', ' # Set to bar\n')
        sect.add('baz', 'qux', '# This is baz\n', ' # Set to qux\n')
        self.assertEqual('''# This is foo
foo = bar # Set to bar
# This is baz
baz = qux # Set to qux
''',
                         sect.serialize())


class TestModifiedSectionSerialization(unittest.TestCase):

    def setUp(self):
        super(TestModifiedSectionSerialization, self).setUp()
        sect = parsers.Section(None)
        sect.add('b', '1', '# Define b\n', ' # set to 1\n')
        sect.add('a', '2', '# Define a\n', ' # set to 2\n')
        sect.add('z', '3', '# Define z\n', ' # set to 3\n')
        self.section = sect

    def test_added_option(self):
        self.section.add('foo', 'bar')
        self.assertEqual('''# Define b
b = 1 # set to 1
# Define a
a = 2 # set to 2
# Define z
z = 3 # set to 3
foo = bar
''',
                         self.section.serialize())

    def test_modified_option(self):
        self.section['a'] = '42'
        self.assertEqual('''# Define b
b = 1 # set to 1
# Define a
a = 42 # set to 2
# Define z
z = 3 # set to 3
''',
                         self.section.serialize())

    def test_deleted_option(self):
        del self.section['a']
        self.assertEqual('''# Define b
b = 1 # set to 1
# Define z
z = 3 # set to 3
''',
                         self.section.serialize())


class TestMakeSections(unittest.TestCase):

    def setUp(self):
        super(TestMakeSections, self).setUp()
        self.parser = parsers.Parser()

    def test_empty(self):
        self.assertEqual([], list(self.parser.make_sections([])))

    def test_single_section(self):
        defs = [SD(None), OD('a', 'b', None, ' # b is good\n')]
        sections = list(self.parser.make_sections(defs))
        self.assertEqual(1, len(sections))
        section = sections[0]
        self.assertEqual('b', section['a'])

    def test_several_sections(self):
        defs = [SD('s1'), OD('a', 'b', None, ' # b is good\n'),
                SD('s2'), OD('c', 'd'), OD('foo', 'bar')]
        sections = list(self.parser.make_sections(defs))
        self.assertEqual(2, len(sections))
        s1, s2 = sections
        self.assertEqual('b', s1['a'])
        self.assertEqual('d', s2['c'])
        self.assertEqual('bar', s2['foo'])
