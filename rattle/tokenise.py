
import ast
import re
from tokenize import *
from StringIO import StringIO
from collections import namedtuple


class TemplateSyntaxError(Exception):
    pass

TOKEN_TEXT = 0
TOKEN_VAR = 1
TOKEN_BLOCK = 2
TOKEN_COMMENT = 3
TOKEN_MAPPING = {
    TOKEN_TEXT: u'Text',
    TOKEN_VAR: u'Var',
    TOKEN_BLOCK: u'Block',
    TOKEN_COMMENT: u'Comment',
}

class Token(object):
    __slots__ = ('mode', 'content', 'line', 'col',)
    def __init__(self, mode, content, line=None, col=None):
        self.mode = mode
        self.content = content
        self.line = line
        self.col = col

    def __repr__(self):
        return u'{%s} %s' % (TOKEN_MAPPING[self.mode], self.content,)

tag_re = re.compile(r'{%\s*(?P<tag>.+?)\s*%}|{{\s*(?P<var>.+?)\s*}}|{#\s*(?P<comment>.+?)\s*#}')

### Back-ported from Py3
EXACT_TOKEN_TYPES = {
    '(':   LPAR,
    ')':   RPAR,
    '[':   LSQB,
    ']':   RSQB,
    ':':   COLON,
    ',':   COMMA,
    ';':   SEMI,
    '+':   PLUS,
    '-':   MINUS,
    '*':   STAR,
    '/':   SLASH,
    '|':   VBAR,
    '&':   AMPER,
    '<':   LESS,
    '>':   GREATER,
    '=':   EQUAL,
    '.':   DOT,
    '%':   PERCENT,
    '{':   LBRACE,
    '}':   RBRACE,
    '==':  EQEQUAL,
    '!=':  NOTEQUAL,
    '<=':  LESSEQUAL,
    '>=':  GREATEREQUAL,
    '~':   TILDE,
    '^':   CIRCUMFLEX,
    '<<':  LEFTSHIFT,
    '>>':  RIGHTSHIFT,
    '**':  DOUBLESTAR,
    '+=':  PLUSEQUAL,
    '-=':  MINEQUAL,
    '*=':  STAREQUAL,
    '/=':  SLASHEQUAL,
    '%=':  PERCENTEQUAL,
    '&=':  AMPEREQUAL,
    '|=':  VBAREQUAL,
    '^=': CIRCUMFLEXEQUAL,
    '<<=': LEFTSHIFTEQUAL,
    '>>=': RIGHTSHIFTEQUAL,
    '**=': DOUBLESTAREQUAL,
    '//':  DOUBLESLASH,
    '//=': DOUBLESLASHEQUAL,
    '@':   AT
}

class TokenInfo(namedtuple('TokenInfo', 'type string start end line')):
    def __repr__(self):
        annotated_type = '%d (%s)' % (self.type, tok_name[self.type])
        return ('TokenInfo(type=%s, string=%r, start=%r, end=%r, line=%r)' %
                self._replace(type=annotated_type))

    @property
    def exact_type(self):
        if self.type == OP and self.string in EXACT_TOKEN_TYPES:
            return EXACT_TOKEN_TYPES[self.string]
        else:
            return self.type
###

def token_stream(content):
    '''Fix the hole in Py2, change token types to their real types'''
    for token in generate_tokens(StringIO(content).readline):
        yield TokenInfo(*token)

                
def tokenise(template):
    '''A generator which yields Token instances'''
    # XXX Add line number tracking
    # XXX Add line, col tracking to tokens
    upto = 0
    for m in tag_re.finditer(template):
        start, end = m.span()
        if upto < start:
            yield Token(TOKEN_TEXT, template[upto:start], col=upto)
        upto = end
        tag, var, comment = m.groups()
        if tag is not None:
            yield Token(TOKEN_BLOCK, tag, col=start)
        elif var is not None:
            yield Token(TOKEN_VAR, var, col=start)
        else:
            yield Token(TOKEN_COMMENT, comment, col=start)
    if upto < len(template):
        yield Token(TOKEN_TEXT, template[upto:], col=start)

def _context_lookup(x):
    '''Return AST for looking up x in the Context'''
    return ast.Subscript(
        value=ast.Name(id='context', ctx=ast.Load()),
        slice=ast.Index(value=ast.Str(s=x), ctx=ast.Load()),
        ctx=ast.Load(),
    )

def _make_number(x):
    '''Turn a token of type NUMBER into an ast.Num'''
    if '.' in tok.string:
        val = float(tok.string)
    else:
        val = int(tok.string)
    return ast.Num(n=val)

def parse_expr(content):
    '''Turn a content string into AST'''
    stream = token_stream(content)

    # First token MUST be either a literal, or name
    tok = next(stream)
    if tok.exact_type == STRING:
        code = ast.Str(s=tok.string)
    elif tok.exact_type == NUMBER:
        code = _make_number(tok)
    elif tok.exact_type == NAME:
        code = _context_lookup(tok.string)
    else:
        raise TemplateSyntaxError(content)

    for tok in stream:
        if tok.exact_type == ENDMARKER:
            break
        if tok.exact_type == DOT:
            tok = next(stream)
            if not tok.exact_type == NAME:
                raise TemplateSyntaxError(content)
            attr = s=tok.string
            code = ast.Attribute(value=code, attr=attr, ctx=ast.Load())
        else:
            raise TemplateSyntaxError('Found unexpected token %r', tok)
    return code


class Template(object):
    def __init__(self, source):
        self.source = source

        code = self.parse()
        ast.fix_missing_locations(code)
        self.func = compile(code, filename="<template>", mode="exec")

    def parse(self):
        '''Convert the parsed tokens into a list of expressions
        Then join them'''
        steps = []
        for token in tokenise(self.source):
            if token.mode == TOKEN_TEXT:
                steps.append(
                    ast.Str(s=token.content)
                )
            elif token.mode == TOKEN_VAR:
                # parse
                steps.append(
                    parse_expr(token.content)
                )
            elif token.mode == TOKEN_BLOCK:
                # Parse args/kwargs
                # create tag class instance
                pass
            else:
                # Must be a comment
                pass

        return ast.Module(
            body=[ast.Assign(
                targets=[ast.Name(id='result', ctx=ast.Store())],
                value=ast.ListComp(
                    elt=ast.Call(
                        func=ast.Name(id='str', ctx=ast.Load()),
                        args=[
                            ast.Name(id='x', ctx=ast.Load()),
                        ],
                        keywords=[],
                    ),
                    generators=[
                        ast.comprehension(
                            target=ast.Name(id='x', ctx=ast.Store()),
                            iter=ast.List(elts=steps, ctx=ast.Load()),
                            ifs=[]
                        )
                    ]
                )
            )
        ])

    def render(self, context):
        ctx = {'context': context}
        exec(self.func, ctx)
        return u''.join(ctx['result'])

