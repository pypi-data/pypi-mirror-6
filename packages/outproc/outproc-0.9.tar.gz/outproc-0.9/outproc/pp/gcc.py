#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output processor for `gcc`
#
# Copyright (c) 2013 Alex Turbov <i.zaufi@gmail.com>
#
# Pluggable Output Processor is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pluggable Output Processor is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import collections
import os
import outproc
import outproc.term
import re
import shlex

from outproc.cpp_helpers import SimpleCppLexer, SnippetSanitizer

_LOCATION_RE = re.compile('([^ :]+?):([0-9]+(,|:[0-9]+[:,]?)?)?')
# /tmp/ccUlKMZA.o:zz.cc:function main: error: undefined reference to 'boost::iostreams::zlib::default_strategy'
_LINK_ERROR_RE = re.compile(':function (vtable for )?(.*): error: ')
_SKIPPING_WARN = re.compile('\[ skipping [0-9]+ instantiation contexts[^\]]+\]')
_WITH_LIST_START = ' [with '

# Introduce a named tuple class
Range = collections.namedtuple('Range', ['start', 'end'])


class Processor(outproc.Processor):

    def __init__(self, config, binary):
        super().__init__(config, binary)
        self.prev_line = None
        self.error = config.get_color('error', 'red')
        self.warning = config.get_color('warning', 'yellow')
        self.notice = config.get_color('notice', 'green')
        self.location = config.get_color('location', 'cyan')
        self.code = config.get_color('code', 'white')
        self.code_kw = config.get_color('code-keyword', 'yellow+bold')
        self.code_type = config.get_color('code-builtin-type', 'red')
        self.code_modifier = config.get_color('code-modifier', 'yellow')
        self.code_std_ns = config.get_color('code-std-namespace', 'green+bold')
        self.code_boost_ns = config.get_color('code-boost-namespace', 'normal')
        self.code_data_member = config.get_color('code-data-member', 'normal')
        self.code_preprocessor = config.get_color('code-preprocessor', 'green')
        self.code_number = config.get_color('code-numeric-literal', 'blue+bold')
        self.code_string = config.get_color('code-string-literal', 'magenta')
        self.code_comment = config.get_color('code-comment', 'grey+bold')
        self.code_cursor = outproc.term.fg2bg(config.get_color('code-cursor', 'red', with_reset=False))
        self.nl = config.get_bool('new-line-after-code', True)

    def _inject_color_at(self, line, color, pos):
        return line[:pos] + color + line[pos:]


    def _try_colorize_location(self, line, current_color):
        match = _LOCATION_RE.search(line)
        if match:
            line = self._inject_color_at(
                self._inject_color_at(line, current_color, match.end())
              , self.location
              , match.start()
              )
        return line


    def _colorize_token(self, t, color):
        return color + t.token + self.code


    def _handle_code_fragment(self, snippet, color_only):
        # Tokenize a given snippet
        tokens = SimpleCppLexer.tokenize_string(snippet)
        #print('tokens={}'.format(tokens))
        # Colorize it!
        for i, tok in enumerate(tokens):
            if tok.kind == SimpleCppLexer.Token.KEYWORD:
                tokens[i].token = self._colorize_token(tok, self.code_kw)
            elif tok.kind == SimpleCppLexer.Token.MODIFIER:
                tokens[i].token = self._colorize_token(tok, self.code_modifier)
            elif tok.kind == SimpleCppLexer.Token.BUILTIN_TYPE:
                tokens[i].token = self._colorize_token(tok, self.code_type)
            elif tok.kind == SimpleCppLexer.Token.PREPROCESSOR:
                tokens[i].token = self._colorize_token(tok, self.code_preprocessor)
            elif tok.kind == SimpleCppLexer.Token.NUMERIC_LITERAL:
                tokens[i].token = self._colorize_token(tok, self.code_number)
            elif tok.kind == SimpleCppLexer.Token.STRING_LITERAL:
                tokens[i].token = self._colorize_token(tok, self.code_string)
            elif tok.kind == SimpleCppLexer.Token.COMMENT:
                tokens[i].token = self._colorize_token(tok, self.code_comment)
            elif tok.kind == SimpleCppLexer.Token.IDENTIFIER:
                if tok.token.startswith('boost::') or tok.token.startswith('BOOST_'):
                    tokens[i].token = self._colorize_token(tok, self.code_boost_ns)
                elif tok.token.startswith('std::'):
                    tokens[i].token = self._colorize_token(tok, self.code_std_ns)
                elif tok.token.startswith('m_'):
                    tokens[i].token = self._colorize_token(tok, self.code_data_member)
        # Reassemble the code snippet
        snippet = SimpleCppLexer.assemble_statement(tokens)
        return snippet


    def _handle_code_snippet(self, snippet, current_color, color_only):
        if not color_only:
            # Try to sanitize whole fragment before doing anything else...
            snippet = SnippetSanitizer.cleanup_snippet(snippet)

        # Check if `[with ...]' parameter expansion present
        pos = snippet.find(_WITH_LIST_START)
        if pos == -1:
            # Handle an ordinal snippet...
            return self.code + self._handle_code_fragment(snippet, color_only) + current_color

        # Handle a complex message w/ possible few '[ with ' template argument expansions...
        result = ''
        last_leading_pos = 0
        # There are few '[with ' possible in one message
        while pos != -1:
            # Copy everything before '[with' (if anything present)
            if last_leading_pos != pos:
                result += self.code \
                    + self._handle_code_fragment(snippet[last_leading_pos:pos], color_only) \
                    + current_color + '\n[ with\n'
            else:
                result += current_color + '\n[ with\n'

            # Find corresponding close ']'... and get a list of ranges of template args
            arg_ranges = []
            with_start_pos = pos + len(_WITH_LIST_START)
            last_arg_start = with_start_pos
            opened_square_brackets = 0
            seen_semicolon = False
            for i, c in enumerate(snippet[last_arg_start:]):
                if c == ';':
                    seen_semicolon = True
                elif c == ' ' and seen_semicolon:
                    assert(last_arg_start < with_start_pos + i - 1)
                    arg_ranges.append(Range(last_arg_start, with_start_pos + i - 1))
                    last_arg_start = with_start_pos + i + 1
                    seen_semicolon = False
                elif c == '[':
                    opened_square_brackets += 1
                    assert(not seen_semicolon)
                elif c == ']':
                    assert(not seen_semicolon)
                    if not opened_square_brackets:
                        # Found a closing square bracket!
                        # Append last template arg
                        arg_ranges.append(Range(last_arg_start, with_start_pos + i))
                        assert(pos < with_start_pos + i)
                        pos = with_start_pos + i + 1
                        break
                    else:
                        opened_square_brackets -= 1

            # Check invariant
            assert('Misbalanced brackets?' and not opened_square_brackets)
            assert('Template argument ranges expected to be non empty' and arg_ranges)

            # Iterate over found template parameters
            for r in arg_ranges:
                result += '  ' + self.code \
                    + self._handle_code_fragment(snippet[r.start:r.end], color_only) \
                    + current_color + '\n'

            # Append closing square bracket for current '[with'
            result += ']'
            last_leading_pos = pos

            # Try to find a next '[with ' starting from last (current) position...
            pos = snippet.find(_WITH_LIST_START, pos)

        return result


    def _try_line_with_quoted_code(self, line, current_color):
        cnt = line.count("'")
        if not cnt or cnt % 2:                              # Skip lines w/o quoted code, or mis-balanced quotes
            return line
        # The line definitely has some code snippets!
        is_code_fragment = False
        fragments = []
        for fragment in line.split("'"):
            if is_code_fragment:
                fragment = self._handle_code_snippet(fragment, current_color, False)
            is_code_fragment = not is_code_fragment
            fragments.append(fragment)
        return "'".join(fragments)


    def _handle_link_error(self, line, function):
        idx = line.find(function)
        assert(idx != -1)
        code = self.code + self._handle_code_fragment(function, False) + self.error
        line = line[:idx] + code + line[idx + len(function):]
        return self._handle_error(line, idx + len(code))


    def _handle_link_notice(self, line):
        line = self._try_colorize_location(line, self.notice)
        return line + self.config.color.reset


    def _handle_error(self, line, start_at):
        #line = self._inject_color_at(line, self.error, start_at)
        line = self._try_colorize_location(line, self.error)
        line = self._try_line_with_quoted_code(line, self.error)
        return line + self.config.color.reset


    def _handle_warning(self, line, start_at):
        #line = self._inject_color_at(line, self.warning, start_at)
        line = self._try_colorize_location(line, self.warning)
        line = self._try_line_with_quoted_code(line, self.warning)
        return line + self.config.color.reset


    def _handle_notice(self, line):
        line = self._try_colorize_location(line, self.notice)
        line = self._try_line_with_quoted_code(line, self.notice)
        line = self._inject_color_at(line, self.notice, 0)
        return line + self.config.color.reset


    def _handle_notice_with_code(self, line, code_start_pos):
        line = line[:code_start_pos] \
          + self.code \
          + self._handle_code_snippet(line[code_start_pos:], self.notice, False) \
          + self.config.color.reset
        return self._try_colorize_location(line, self.notice)


    def handle_line(self, line):
        # Do not even try to handle empty lines
        if (not len(line.strip())):
            return line

        # Replace "couldn't" --> "could not" to avoid char literal ambiguity
        line = line.replace("couldn't", "could not")

        # Categorize message first...

        # Trying various error messages
        match = _LINK_ERROR_RE.search(line)
        if match:
            return self._handle_link_error(line, match.group(2))
        idx = line.find(' error: ')
        if idx != -1:
            return self._handle_error(line, idx)
        if line.startswith('compilation terminated.'):
            return self.error + line + self.config.color.reset

        # Trying some warning messages
        idx = line.find(' warning: ')
        if idx != -1:
            return self._handle_warning(line, idx)

        # Mark "[ skipping N instantiation contexts, use -ftemplate-backtrace-limit=0 to disable ]"
        # as warning, so it will be noticeable
        match = _SKIPPING_WARN.search(line)
        if match:
            return self._handle_warning(line, match.start())

        # TODO Transform into a container of strings and a predicate evaluation
        is_look_like_notice = line.find(' In instantiation of') != -1 \
          or line.find(' In function') != -1                          \
          or line.find(' In member function') != -1                   \
          or line.find(' In static member function ') != -1           \
          or line.find(' In substitution of ') != -1                  \
          or line.find(' In constructor ') != -1                      \
          or line.find(' In destructor ') != -1                       \
          or line.find('In file included from ') != -1                \
          or line.find('                 from ') != -1                \
          or line.find('   required from ') != -1                     \
          or line.find('   recursively required from ') != -1         \
          or line.find('   required by substitution of ') != -1       \
          or line.find('At global scope:') != -1
        if is_look_like_notice:
            return self._handle_notice(line)
        # Handle link notice
        if line.endswith(' previous definition here'):
            return self._handle_link_notice(line)

        # There are possible a bunch of messages started w/ 'note:'
        # some of them contains just an informational text, the others
        # may contain code (in single quotes) mixed w/ text, or just pure code line...
        # I see no other reliable way to recognize code (when it is not in a quotes)
        # than this:
        note_index = line.find(' note: ')
        if note_index != -1:
            is_look_like_notice = line.endswith('suggested alternatives:')               \
              or line.endswith('suggested alternative:')                                 \
              or line.endswith('candidate is:')                                          \
              or line.endswith('candidates are:')                                        \
              or line.endswith('invalid template non-type parameter')                    \
              or line.endswith('template argument deduction/substitution failed:')       \
              or line.endswith(' provided')
            if is_look_like_notice:
                return self._handle_notice(line)
            cnt = line.count("'")
            if not cnt or cnt % 2:
                return self._handle_notice_with_code(line, note_index + len(' note: '))
            return self._handle_notice(line)

        # All standalong code snippets (AFAIK) starts w/ at least one space...
        pos = line.find('^')
        if pos == -1 and line[0] == ' ':
            assert(self.prev_line is None)
            self.prev_line = line
            return None

        if pos != -1:
            assert(self.prev_line is not None)
            # Check if caret points after the end of a previous line.
            # For example:
            # /tmp/nn.cc:2:21: fatal error: iostreamz: No such file or directory
            # #include <iostreamz>
            #                     ^
            if len(self.prev_line) <= pos:
                # Append spaces to it! So pos_to_offset() will find a requested
                # position after line gets colorized...
                self.prev_line += ' ' * (pos - len(self.prev_line) + 1)
            line = self.code + self._handle_code_fragment(self.prev_line, True) + self.config.color.reset

            # Find a cursor position for a transformed line
            pos = outproc.term.pos_to_offset(line, pos)
            line = line[:pos] + self.code_cursor + line[pos:pos+1] + self.config.color.normal_bg \
              + line[pos+1:] + ('\n' if self.nl else '')
            self.prev_line = None

        # Return unmodified line if nothing has matched
        return line


    @staticmethod
    def config_file_name(module_name):
        return 'gcc.conf'
