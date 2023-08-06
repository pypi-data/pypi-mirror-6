# -*- coding: utf-8 -*-
# Copyright 2012 Mark Hall (Mark.Hall@work.room3b.eu)
# 
# This file is part of the PyWebTools.
# 
# The PyWebTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# The PyWebTools are distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with PyWebTools. If not, see <http://www.gnu.org/licenses/>.

import collections
import re

OBJ = 'OBJ'
VAL = 'VAL'
CALL = 'CALL'
IDENT = 'IDENT'
OP = 'OP'
BRACE_LEFT = 'BRLEFT'
BRACE_RIGHT = 'BRRIGHT'
EOL = 'EOL'

class AuthorisationException(Exception):
    
    def __init__(self, message):
        self.message = message
    
    def __repr__(self):
        return 'AuthorisationException(%s)' % repr(self.message)
    
    def __str__(self):
        return self.message

class AccessDeniedException(AuthorisationException):
    
    def __init__(self):
        AuthorisationException.__init__(self, 'Access denied')

def tokenise(auth_string):
    def process(token):
        token = ''.join(token)
        if token == '(':
            return (BRACE_LEFT, token)
        elif token == ')':
            return (BRACE_RIGHT, token)
        elif token.lower() in ['.', '==', '!=', 'or', 'and']:
            return (OP, token.lower())
        elif token.startswith(':'):
            return (OBJ, token[1:])
        else:
            return (IDENT, token)
    tokens = []
    token = []
    string_marker = None
    for char in auth_string:
        if string_marker:
            if char == string_marker:
                token.append(char)
                tokens.append((VAL, ''.join(token)))
                token = []
                string_marker = None
            else:
                token.append(char)
        else:
            if char in ['(', ')', '.']:
                if token:
                    tokens.append(process(token))
                    token = []
                tokens.append(process(char))
            elif char in ['!', '=']:
                if token:
                    if len(token) > 1 or token[0] not in ['!', '=']:
                        tokens.append(process(token))
                        token = []
                token.append(char)
            elif char == ' ':
                if token:
                    tokens.append(process(token))
                    token = []
            elif char in ["'", '"']:
                if token:
                    tokens.append(process(token))
                    token = []
                token.append(char)
                string_marker = char
            else:
                token.append(char)
    if string_marker:
        raise AuthorisationException("Invalid authorisation statement. Unterminated string literal.")
    if token:
        tokens.append(process(token))
    tokens.append((EOL, ''))
    return tokens

def parse(tokens):
    def value(token):
        if token[1] == 'True':
            return (VAL, True)
        elif token[1] == 'False':
            return (VAL, False)
        elif re.match(r'[0-9]+', token[1]):
            return (VAL, int(token[1]))
        elif token[1].startswith("'") and token[1].endswith("'"):
            return (VAL, token[1][1:-1])
        elif token[1].startswith('"') and token[1].endswith('"'):
            return (VAL, token[1][1:-1])
        else:
            return (VAL, token[1])
    def float_value(token, tokens):
        if len(tokens) > 0:
            ntoken = tokens.pop()
            if ntoken[0] == OP and ntoken[1] == '.':
                ntoken2 = tokens.pop()
                if ntoken2[0] == IDENT and isinstance(value(ntoken2)[1], int):
                    return (VAL, float('%s.%s' % (token[1], ntoken2[1])))
                else:
                    tokens.append(ntoken2)
                    tokens.append(ntoken)
                    return token
            else:
                tokens.append(ntoken)
                return token
    def params(tokens):
        param_list = []
        while True:
            ntoken = tokens.pop()
            if ntoken[0] == IDENT:
                tmp = value(ntoken)
                if tmp[0] == VAL and isinstance(tmp[1], int):
                    param_list.append(float_value(tmp, tokens))
                else:
                    param_list.append(tmp)
            elif ntoken[0] == OBJ:
                param_list.append(ntoken)
            elif ntoken[0] == VAL:
                param_list.append(value(ntoken))
            elif ntoken[0] == BRACE_RIGHT:
                break
            else:
                raise AuthorisationException('Invalid authorisation statement: Was expecting IDENT, OBJ, VAL, or ), but got %s' % (ntoken[1]))
        return param_list
    def obj(token, tokens):
        ntoken = tokens.pop()
        if ntoken == (EOL, ''):
            tokens.append((EOL, ''))
            return (OBJ, token[1])
        elif ntoken == (OP, '.'):
            ntoken = tokens.pop()
            if ntoken == (EOL, ''):
                raise AuthorisationException('Invalid authorisation statement: Was expecting IDENT, but got EOL')
            if ntoken[0] == IDENT:
                result = [CALL, token[1], ntoken[1]]
                if len(tokens) > 0:
                    ntoken = tokens.pop()
                    if ntoken[0] == BRACE_LEFT:
                        result.extend(params(tokens))
                    else:
                        tokens.append(ntoken)
                return tuple(result)
    output = []
    tokens.reverse()
    if len(tokens) == 0 or tokens[0][0] != EOL:
        raise AuthorisationException('Invalid authorisation statement. Missing EOL')
    expected = [OBJ, IDENT, VAL, BRACE_LEFT]
    while len(tokens) > 0:
        ntoken = tokens.pop()
        if ntoken[0] not in expected:
            raise AuthorisationException('Invalid authorisation statement. Was expecting one of %s, but got %s' % (', '.join(expected), ntoken[0]))
        if ntoken[0] == OBJ:
            output.append(obj(ntoken, tokens))
            expected = [OP, BRACE_RIGHT, EOL]
        elif ntoken[0] == IDENT:
            tmp = value(ntoken)
            if tmp[0] == VAL and isinstance(tmp[1], int):
                output.append(float_value(tmp, tokens))
            else:
                output.append(tmp)
            expected = [OP, BRACE_RIGHT, EOL]
        elif ntoken[0] == VAL:
            output.append(value(ntoken))
            expected = [OP, BRACE_RIGHT, EOL]
        elif ntoken[0] == OP:
            if ntoken[1] == '.':
                raise AuthorisationException('Invalid authorisation statement. Was expecting one of OBJ, IDENT, VAL, OP, or BRACE_LEFT, but got .')
            output.append(ntoken)
            expected = [OBJ, IDENT, VAL, BRACE_LEFT]
        elif ntoken[0] == BRACE_LEFT:
            output.append(ntoken)
            expected = [OBJ, IDENT, VAL, BRACE_LEFT]
        elif ntoken[0] == BRACE_RIGHT:
            output.append(ntoken)
            expected = [OP, BRACE_RIGHT, EOL]
    return output

def infix_to_reverse_polish(tokens):
    def op_precedence(token):
        if token[0] == BRACE_LEFT:
            return 0
        elif token[0] == OP and token[1] in ['==', '!=']:
            return 2
        else:
            return 1
    output = []
    stack = []
    for token in tokens:
        if token[0] == BRACE_LEFT:
            stack.append(token)
        elif token[0] == BRACE_RIGHT:
            while True:
                if len(stack) == 0:
                    raise AuthorisationException('Invalid authorisation statement: Too many ).')
                ntoken = stack.pop()
                if ntoken[0] == BRACE_LEFT:
                    break
                else:
                    output.append(ntoken)
        elif token[0] == OP:
            while len(stack) > 0:
                ntoken = stack.pop()
                if op_precedence(token) > op_precedence(ntoken):
                    stack.append(ntoken)
                    break
                else:
                    output.append(ntoken)
            stack.append(token)
        else:
            output.append(token)
    while len(stack) > 0:
        ntoken = stack.pop()
        if ntoken[0] == BRACE_LEFT:
            raise AuthorisationException('Invalid authorisation statement: Missing ).')
        output.append(ntoken)
    return output

def is_authorised(auth_string, objects):
    stack = []
    for token in infix_to_reverse_polish(parse(tokenise(auth_string))):
        if token[0] == VAL:
            stack.append(token)
        elif token[0] == OBJ:
            if token[1] in objects:
                stack.append((OBJ, objects[token[1]]))
            else:
                stack.append((OBJ, None))
        elif token[0] == CALL:
            if token[1] in objects:
                obj = objects[token[1]]
                func = token[2].replace('-', '_')
                if hasattr(obj, func):
                    attr = getattr(obj, func)
                    if isinstance(attr, collections.Callable):
                        params = []
                        for param in token[3:]:
                            if param[0] == OBJ:
                                if param[1] in objects:
                                    params.append(objects[param[1]])
                                else:
                                    params.append(None)
                            elif param[0] == VAL:
                                params.append(param[1])
                        stack.append((VAL, attr(*params)))
                    else:
                        stack.append((VAL, attr))
                else:
                    stack.append((VAL, False))
            else:
                stack.append((VAL, False))
        elif token[0] == OP:
            op2 = stack.pop()
            op1 = stack.pop()
            if token[1] == 'and':
                stack.append((VAL, op1[1] and op2[1]))
            elif token[1] == 'or':
                stack.append((VAL, op1[1] or op2[1]))
            elif token[1] == '!=':
                stack.append((VAL, op1[1] != op2[1]))
            elif token[1] == '==':
                stack.append((VAL, op1[1] == op2[1]))
        else:
            raise AuthorisationException('Internal authorisation execution error.') # pragma: no cover
    if len(stack) == 0:
        raise AuthorisationException('Empty authorisation statement') # pragma: no cover
    return bool(stack[0][1])

def assert_authorised(auth, objects):
    if is_authorised(auth, objects):
        return True
    else:
        raise AccessDeniedException()
