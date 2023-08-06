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

import collections
import re


from uciconfig import errors


class Definition(object):

    def __init__(self, pre_comment, post_comment):
        self.pre_comment = pre_comment
        self.post_comment = post_comment

    def __eq__(self, other):
        return (self.pre_comment == other.pre_comment
                and self.post_comment == other.post_comment)


class OptionDefinition(Definition):

    def __init__(self, key, value, pre=None, post=None):
        super(OptionDefinition, self).__init__(pre, post)
        self.key = key
        self.value = value

    def __eq__(self, other):
        return (self.key == other.key
                and self.value == other.value
                and super(OptionDefinition, self).__eq__(other))

    def __repr__(self):
        s = ''
        if self.pre_comment:
            s = s + self.pre_comment
        s = s + self.key + '=' + self.value
        if self.post_comment:
            s = s + self.post_comment
        return s


class SectionDefinition(Definition):

    def __init__(self, name, pre=None, post=None):
        super(SectionDefinition, self).__init__(pre, post)
        self.name = name

    def __eq__(self, other):
        return (self.name == other.name
                and super(SectionDefinition, self).__eq__(other))

    def __repr__(self):
        s = ''
        if self.pre_comment:
            s = s + self.pre_comment
        if self.name is not None:
            s = s + '[' + self.name + ']'
        if self.post_comment:
            s = s + self.post_comment
        return s


class Section(collections.OrderedDict):
    """A section holding options with their associated value and comments.

    This allows serializing configuration files where users can add comments
    and keep them when the configuration file is updated.
    """
    def __init__(self, name, pre=None, post=None):
        super(Section, self).__init__()
        self.name = name
        # The section comments
        self.pre_comment = pre
        self.post_comment = post
        # The option comments. They are handled separatly from the values since
        # relying on the key is enough (renaming options is not a feature ;)
        self.pre = {}
        self.post = {}

    def add(self, key, value, pre=None, post=None):
        """Add a new option.

        :param key: The option name.

        :param value: The option value.

        :param pre: The preceding comment.

        :param post: The comment follwoing the value up to the end of the line
            where it is defined.
        """
        self[key] = value
        self.pre[key] = pre
        self.post[key] = post

    def serialize(self):
        """Serialize the section with the comments.

        :return: The serialized unicode text.
        """
        chunks = []
        if self.name is not None:
            if self.pre_comment is not None:
                chunks.append(self.pre_comment)
            chunks.extend(['[', self.name, ']'])
            if self.post_comment is not None:
                chunks.append(self.post_comment)
            else:
                # Add a newline after each section definition if there is no
                # post comment (which always contain a final newline).
                chunks.append('\n')
        for key, value in self.items():
            pre = self.pre.get(key, None)
            if pre is not None:
                chunks.append(pre)
            chunks.extend([key, ' = ', value])
            post = self.post.get(key, None)
            if post is not None:
                chunks.append(post)
            else:
                # Add a newline after each definition if there is no post
                # comment (which always contain a final newline).
                chunks.append('\n')
        return ''.join(chunks)


class Parser(object):

    comment_re = re.compile(r'(\s*#.*\n)')
    section_re = re.compile(r'\[([^]]*)\]')
    option_re = re.compile(r'\s*([a-zA-Z_][a-zA-Z0-9_.]*)\s*=\s*')

    def __init__(self):
        self.path = None
        self.line = None

    def parse_config(self, path, text):
        """Parse a text containing sections, options and comments.

        :param path: The path where the text is coming from (used for error
            reporting).

        :param text: The unicode string to parse.

        :return: A list of section and option definitions.
        """
        self.path = path
        self.line = 1
        tokens = []
        remaining = text
        pre = None
        while remaining:
            pre_comment = self.comment_re.match(remaining)
            if pre_comment:
                # Buffer the comment lines until a section or an option collect
                # it
                if pre is None:
                    pre = pre_comment.group(1)
                else:
                    pre = pre + pre_comment.group(1)
                remaining = remaining[pre_comment.end():]
                self.line += 1
                continue

            section = self.section_re.match(remaining)
            if section:
                # A new section
                name = section.group(1)
                if name == '':
                    raise errors.SectionEmptyName(self.path, self.line)
                remaining = remaining[section.end():]
                post_comment = self.comment_re.match(remaining)
                if post_comment:
                    post = post_comment.group(1)
                    remaining = remaining[post_comment.end():]
                else:
                    post = None
                tokens.append(SectionDefinition(name, pre, post))
                pre = None
                if post is not None:
                    self.line += 1
                post = None
                continue

            key_matches = self.option_re.match(remaining)
            if key_matches:
                if not tokens:
                    # First option definition without a previous section, it's
                    # the None section.
                    tokens.append(SectionDefinition(None))
                key = key_matches.group(1)
                remaining = remaining[key_matches.end():]
                value, post, remaining = self.parse_value(remaining)
                tokens.append(OptionDefinition(key, value, pre, post))
                if post is not None:
                    self.line += 1
                pre = None
                continue

            if remaining.startswith('\n'):
                # Keep track of the current line
                self.line += 1
                remaining = remaining[1:]
                continue

            if remaining.startswith(' '):
                # Consume spaces to get rid of empty lines
                remaining = remaining[1:]
                continue

            raise errors.InvalidSyntax(self.path, self.line)
        return tokens

    def parse_value(self, text):
        """Parse an option value.

        :param text: The unicode string to parse containing the value.

        :return: A (value, post, remaining) tuple where 'value' is the string
            representing the value, 'post' the associated comment (can be None)
            and 'remaining' the rest of text after parsing.
        """
        value = ''
        post = ''
        cur = 0
        post_last = len(text)
        # ignore leading spaces
        while cur < post_last and text[cur] == ' ':
            cur += 1
        # build value until we encounter end of line or a comment
        while cur < post_last and text[cur] not in ('#', '\n'):
            value += text[cur]
            cur += 1
        # remove trailing spaces
        spaces = ''
        while value.endswith(' '):
            spaces += value[-1]
            value = value[:-1]
        # comment (if present) ends at end of line
        if cur < post_last and text[cur] == '#':
            post = spaces
            while cur < post_last and text[cur] != '\n':
                post += text[cur]
                cur += 1
        if post == '':
            post = None
        # Consume end of line if present
        if cur < post_last and text[cur] == '\n':
            if post is not None:
                post += '\n'
            cur += 1
        remaining = text[cur:]
        return value, post, remaining

    def make_sections(self, tokens):
        """Yields the sections built from the received tokens.

        :param tokens: An iterable of tokens as returned by 'parse_config'.

        :yield: A Section object as soon as one is complete.
        """
        cur = None
        for token in tokens:
            if isinstance(token, SectionDefinition):
                if cur is not None:
                    yield cur
                cur = Section(token.name,
                              token.pre_comment, token.post_comment)
            else:
                cur.add(token.key, token.value,
                        token.pre_comment, token.post_comment)
        if cur is not None:
            yield cur
