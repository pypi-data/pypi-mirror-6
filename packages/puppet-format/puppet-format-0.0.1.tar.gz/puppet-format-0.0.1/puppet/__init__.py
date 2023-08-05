#
# Puppet manifest file parser.
# 
# @link https://github.com/markwatkinson/python-string-scanner/blob/master/scanner/scanner.py
# @link https://github.com/rodjek/puppet-lint/blob/master/lib/puppet-lint/lexer.rb
#

import os
import sys
import tempfile
import subprocess
import yaml
import re
import scanner

class Lexer(scanner.Scanner):

    # Keywords
    KEYWORDS = (
        'class',
        'case',
        'default',
        'define',
        'import',
        'if',
        'else',
        'elsif',
        'inherits',
        'node',
        'and',
        'or',
        'undef',
        'true',
        'false',
        'in',
        'unless',
    )

    # Token types that can be described by a single regular expression.
    # Order by precedence from high to low.
    TOKENS_BY_REGEX = [
        ('CLASSREF'    , r'(((::){0,1}[A-Z][-\w]*)+)'),
        ('NUMBER'      , r'\b((?:0[xX][0-9A-Fa-f]+|0?\d+(?:\.\d+)?(?:[eE]-?\d+)?))\b'),
        ('NAME'        , r'(((::)?[a-z0-9][-\w]*)(::[a-z0-9][-\w]*)*)'),
        ('LBRACK'      , r'(\[)'),
        ('RBRACK'      , r'(\])'),
        ('LBRACE'      , r'(\{)'),
        ('RBRACE'      , r'(\})'),
        ('LPAREN'      , r'(\()'),
        ('RPAREN'      , r'(\))'),
        ('ISEQUAL'     , r'(==)'),
        ('MATCH'       , r'(=~)'),
        ('FARROW'      , r'(=>)'),
        ('EQUALS'      , r'(=)'),
        ('APPENDS'     , r'(\+=)'),
        ('PARROW'      , r'(\+>)'),
        ('PLUS'        , r'(\+)'),
        ('GREATEREQUAL', r'(>=)'),
        ('RSHIFT'      , r'(>>)'),
        ('GREATERTHAN' , r'(>)'),
        ('LESSEQUAL'   , r'(<=)'),
        ('LLCOLLECT'   , r'(<<\|)'),
        ('OUT_EDGE'    , r'(<-)'),
        ('OUT_EDGE_SUB', r'(<~)'),
        ('LCOLLECT'    , r'(<\|)'),
        ('LSHIFT'      , r'(<<)'),
        ('LESSTHAN'    , r'(<)'),
        ('NOMATCH'     , r'(!~)'),
        ('NOTEQUAL'    , r'(!=)'),
        ('NOT'         , r'(!)'),
        ('RRCOLLECT'   , r'(\|>>)'),
        ('RCOLLECT'    , r'(\|>)'),
        ('IN_EDGE'     , r'(->)'),
        ('IN_EDGE_SUB' , r'(~>)'),
        ('MINUS'       , r'(-)'),
        ('COMMA'       , r'(,)'),
        ('DOT'         , r'(\.)'),
        ('COLON'       , r'(:)'),
        ('AT'          , r'(@)'),
        ('SEMIC'       , r'(;)'),
        ('QMARK'       , r'(\?)'),
        ('BACKSLASH'   , r'(\\)'),
        ('TIMES'       , r'(\*)'),
    ]

    FORMATTING_TOKENS = (
        'WHITESPACE', 
        'NEWLINE', 
        'COMMENT',
        'MLCOMMENT',
        'SLASH_COMMENT', 
        'INDENT'
    )

    NEWLINE_PATTERN = r'\r\n|\r|\n'

    #
    # Returns a list of tokens.
    #
    def tokenize(self):
        tokens = []
        while not self.eos():
            """
            It pays to do string based checks (isspace, isalpha, etc) before
            running regex methods if possible.
            """
            index = self.pos
            c = self.peek()
            token = None

            for k, v in self.TOKENS_BY_REGEX:
                if not self.scan(v):
                    continue
                value = self.match()
                if k == "NAME" and k in self.KEYWORDS:
                    self.new_token(tokens, value.upper(), value, index)
                else:
                    self.new_token(tokens, k, value, index)
                break

            if c == '$' and self.scan(r"\$((::)?([\w-]+::)*[\w-]+)"):
                print(self.match())
                sys.exit(0)
            elif c == " ":
                self.skip_bytes(1)
                self.new_token(tokens, "WHITESPACE", " ", index)
            elif c == "\t":
                self.skip_bytes(1)
                self.new_token(tokens, "INDENT", "\t", index)
            elif c in ("\r", "\n") and self.scan(self.NEWLINE_PATTERN):
                self.new_token(tokens, "NEWLINE", self.match(), index)
            elif c == '"' or c == "'":
                self.scan(r'{0}( (?: [^{0}\\]+ | \\.)* ){0}'.format(c), re.X|re.S)
                value = self.match_group(1)
                if not value:
                    raise Exception("invalid string format", index)
                if c == '"':
                    self.new_token(tokens, "STRING", value, index)
                else:
                    self.new_token(tokens, "SSTRING", value, index)
            elif c == '#':
                value = self.scan_to(self.NEWLINE_PATTERN)
                self.new_token(tokens, "COMMENT", value, index)

            if index >= self.pos:
                raise Exception(index, c, self.check_until('\n'))

        return tokens

    #
    # Create a new Token object, calculate its line number and column.
    #
    def new_token(self, tokens, t, value, index):
        s = self.string[0:index]
        lines = re.split(self.NEWLINE_PATTERN, s)
        line = len(lines) - 1
        column = len(lines[-1]) if len(lines) > 0 else 0
        token = Token(t, value, line, column)
        last_token = tokens[-1] if len(tokens) > 0 else None
        if last_token:
            token.prev_token = last_token
            last_token.next_token = token
            if t not in self.FORMATTING_TOKENS:
                prev_code_token = self.prev_code_token(tokens)
                if prev_code_token:
                    prev_code_token.next_code_token = token
                    token.prev_code_token = prev_code_token
        tokens.append(token)

    def prev_code_token(self, tokens):
        for token in reversed(tokens):
            if token.type not in self.FORMATTING_TOKENS:
                return token
        return None

def tokenize(path):
    lexer = Lexer(open(path).read())
    tokens = lexer.tokenize()
    return tokens

def first_code_token(tokens):
    for token in tokens:
        if token.type in Lexer.FORMATTING_TOKENS:
            continue
        return token
    return None

def find_next(token, type):
    for token in until_end(token):
        if token.type == type:
            return token

def find_next_string(token):
    for token in until_end(token):
        if token.type == "STRING" or token.type == "SSTRING":
            return token

def until_token(token, type, code = True):
    for token in until_end(token, code):
        if code:
            if token.prev_code_token and token.prev_code_token.type == "RBRACE":
                break
        else:
            if token.prev_token and token.prev_token.type == "RBRACE":
                break
        yield token

def until_end(token, code = True):
    while True:
        yield token
        if code:
            token = token.next_code_token
        else:
            token = token.next_token
        if not token:
            break

def find_token(token, name = None):
    for token in until_end(token):
        if token.type == "NAME":
            if name and token.value != name:
                continue
            return token

def find_type(token, type, value=None):
    for token in until_end(token):
        if token.type == type:
            if value and token.value != value:
                continue
            return token

def find_resource(token):
    for token in until_end(token):
        if token.type == "NAME":
            if token.next_code_token and token.next_code_token.type == "LBRACE":
                return token

class Token(object):
    def __init__(self, type, value, line = 0, column = 0, next_token = None, prev_token = None, next_code_token = None, prev_code_token = None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.next_token = next_token
        self.prev_token = prev_token
        self.next_code_token = next_code_token
        self.prev_code_token = prev_code_token
    def __str__(self):
        return "<Token {} ({}) @{}:{}>".format(self.type, repr(self.value), self.line, self.column)
    def __repr__(self):
        return self.__str__()
    def to_manifest(self):
        if self.type == "STRING":
            return '"{}"'.format(self.value)
        elif self.type == "SSTRING":
            return "'{}'".format(self.value)
        elif self.type == "DQPRE":
            return "\"{}".format(self.value)
        elif self.type == "DQPOST":
            return "{}\"".format(self.value)
        elif self.type == "VARIABLE":
            if self.prev_code_token and self.prev_code_token.type in ("DQPRE",
                    "DQPOST"):
                return "${#{{}}}".format(self.value)
            else:
                return "$#{{}}".format(self.value)
        elif self.type == "NEWLINE":
            return "\n"
        elif self.type == "REGEX":
            return "/{}/".format(self.value)
        else:
            return self.value

def parse(token):
    """Parse into resource, class objects."""
    resources = []
    classes = []
    while True:
        token = find_resource(token)
        if not token:
            break
        resource, token = parse_resource(token)
        resources.append(resource)
        token = token.next_code_token
        if not token:
            break
    return (resources, classes)

def parse_resource(token):
    if token.type != "NAME":
        return None
    token_start = token
    name = token.value
    token = find_next_string(token)
    title = token.value
    attrs = {}
    cur_key = None
    for token in until_token(token, 'RBRACE'):
        if token.type == "NAME" and not cur_key:
            cur_key = token.value
        if cur_key and token.prev_code_token.type == 'FARROW':
            attrs[cur_key] = token.value
            cur_key = None
    token_end = token
    return Resource(name, title, attrs, token_start, token_end), token

def find_prev_non_comment(token):
    while True:
        token = token.prev_token
        if not token:
            break
        if token.type != 'NEWLINE' and token.type != 'COMMENT':
            return token

class Resource(object):
    def __init__(self, name, title, attrs, token_start, token_end):
        self.name = name
        self.title = title
        self.attrs = attrs
        self.token_start = token_start
        self.token_end = token_end
    def __str__(self):
        return "<Resource {}:{}>".format(self.name, self.title)
    def __repr__(self):
        return self.__str__()
    def discard(self):
        """ Discard this resource from token list. """
        self.token_start.prev_token.next_token = self.token_end.next_token
    def rewrite(self):
        token = self.token_start
        indent_spaces = 2
        attr_indent = False
        attr_key = False
        attr_value = False
        if self.attrs:
            max_attr_len = max(map(len, self.attrs))
        # separate resource by newline
        prev_token = find_prev_non_comment(token)
        if prev_token:
            insert_after(prev_token, newline_token())
        while True:
            if token == self.token_start:
                token = insert_after(token, whitespace_token())
            elif token.type == "LBRACE":
                token = insert_after(token, whitespace_token())
            elif token.type == "COLON":
                token = insert_after(token, newline_token())
                attr_indent = True
            elif token.type == "COMMA":
                token = insert_after(token, newline_token())
                attr_indent = True
            elif token.type == "NAME" and attr_key:
                for i in range(max_attr_len - len(token.value) + 1):
                    token = insert_after(token, whitespace_token())
                attr_key = False
            elif token.type == "FARROW":
                token = insert_after(token, whitespace_token())
                attr_value = True
            elif attr_value:
                if token.next_token.type != 'COMMA':
                    insert_after(token, comma_token())
                attr_value = False
            # post processing
            if attr_indent:
                if token.next_token.type == "NAME":
                    for i in range(4):
                        token = insert_after(token, whitespace_token())
                attr_indent = False
                attr_key = True
            if token == self.token_end:
                insert_after(token, newline_token())
                break
            token = token.next_token

def array_token():
    return Token("FARROW", "=>")

def lbrace_token():
    return Token("LBRACE", "{")

def rbrace_token():
    return Token("RBRACE", "}")

def whitespace_token():
    return Token("WHITESPACE", " ")

def newline_token():
    return Token("NEWLINE", "\n")

def comma_token():
    return Token("COMMA", ",")

def colon_token():
    return Token("COLON", ":")

def arrow_token():
    return Token("FARROW", "=>")

def insert_before(first_token, token, *newtokens):
    if len(newtokens) == 1:
        newtoken = newtokens[0]
        if first_token == token:
            newtoken.next_token = token
            token.prev_token = newtoken
            return newtoken, newtoken
        if token.prev_token:
            token.prev_token.next_token = newtoken
        newtoken.prev_token = token.prev_token
        token.prev_token = newtoken
        newtoken.next_token = token
        return first_token, newtoken
    else:
        for newtoken in newtokens:
            token = insert_before(token, newtoken)
        return first_token, token

def insert_after(token, *newtokens):
    if len(newtokens) == 1:
        newtoken = newtokens[0]
        if token.next_token:
            token.next_token.prev_token = newtoken
        newtoken.next_token = token.next_token
        token.next_token = newtoken
        newtoken.prev_token = token
        return newtoken
    else:
        for newtoken in newtokens:
            token = insert_after(token, newtoken)
        return token

def insert_attr(token, attr, value):
    for i in range(2):
        token = insert_after(token, whitespace_token())
    if isinstance(value, Token):
        value_token = value
    else:
        value_token = Token("STRING", value)
    token = insert_after(token, Token("NAME", attr))
    token = insert_after(token, whitespace_token())
    token = insert_after(token, arrow_token())
    token = insert_after(token, whitespace_token())
    token = insert_after(token, value_token)
    token = insert_after(token, comma_token())
    token = insert_after(token, newline_token())
    return token

def remove_token(first_token, token):
    if token.prev_token:
        token.prev_token.next_token = token.next_token
    else:
        first_token = token.next_token
    if token.next_token:
        token.next_token.prev_token = token.prev_token
    return first_token

def remove_whitespace(first_token):
    token = first_token
    removed_types = ('WHITESPACE', 'INDENT', 'NEWLINE')
    comment_line = False
    while True:
        if token.type == "COMMENT":
            comment_line = True
        if not comment_line and token.type in removed_types:
            first_token = remove_token(first_token, token)
        if comment_line and token.type == "NEWLINE":
            comment_line = False
        token = token.next_token
        if not token:
            break
    return first_token
