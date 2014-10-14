import ast
import os

from .astpp import dump as ast_dump
from .parser import pg, lg
from .tokenise import tokenise, TOKEN_TEXT, TOKEN_VAR, TOKEN_BLOCK


AST_DEBUG = os.environ.get('RATTLE_AST_DEBUG', False)


class TemplateSyntaxError(Exception):
    pass


class SafeData(str):
    """
    A wrapper for str to indicate it doesn't need escaping.
    """
    pass


def escape(text):
    """
    Returns the given text with ampersands, quotes and angle brackets encoded
    for use in HTML.
    """
    if isinstance(text, SafeData):
        return text
    if not isinstance(text, str):
        text = str(text)
    return SafeData(
        text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;').replace("'", '&#39;')
    )


def auto_escape(s):
    if isinstance(s, SafeData):
        return s
    return escape(s)


class Library(object):

    def __init__(self):
        self._filters = {}
        self._tags = {}
        self._ambiguous_filters = set()
        self._ambiguous_tags = set()

    @property
    def filters(self):
        return self._filters

    @property
    def tags(self):
        return self._tags

    def register_filter(self, func):
        name = func.__name__
        full_name = '%s.%s' % (func.__module__, func.__name__)
        if name not in self._filters:
            if name not in self._ambiguous_filters:
                self._filters[func.__name__] = func
        elif full_name not in self._filters:
            self._ambiguous_filters.add(name)
            del self._filters[name]
        self._filters[full_name] = func
        # Allows user as decorator
        return func

    def unregister_filter(self, full_name):
        self._filters.pop(full_name, None)
        _, _, short_name = full_name.rpartition('.')
        self._filters.pop(short_name, None)

    def register_tag(self, func):
        name = func.__name__
        full_name = '%s.%s' % (func.__module__, func.__name__)
        if name not in self._tags:
            if name not in self._ambiguous_tags:
                self._tags[func.__name__] = func
        elif full_name not in self._tags:
            self._ambiguous_tags.add(name)
            del self._tags[name]
        self._tags[full_name] = func
        # Allows user as decorator
        return func

    def unregister_tag(self, full_name):
        self._tags.pop(full_name, None)
        _, _, short_name = full_name.rpartition('.')
        self._tags.pop(short_name, None)


library = Library()


class Template(object):

    def __init__(self, source):
        self.source = source

        # A list of compiled tags
        self.compiled_tags = []

        self.lexer = lg.build()
        self.parser = pg.build()

        code = self.parse()
        ast.fix_missing_locations(code)
        if AST_DEBUG:
            print(ast_dump(code))
        self.func = compile(code, filename="<template>", mode="eval")

        self.default_context = {
            'True': True,
            'False': False,
            'None': None,
        }

    def _token_to_code(self, token):
        """
        Given a Token instance, convert it to AST
        """
        code = None
        if token.mode == TOKEN_TEXT:
            code = ast.Str(s=token.content)
        elif token.mode == TOKEN_VAR:
            # parse
            code = self.parser.parse(self.lexer.lex(token.content))
            code = ast.Call(
                func=ast.Name(id='auto_escape', ctx=ast.Load()),
                args=[code],
                keywords=[],
            )
        elif token.mode == TOKEN_BLOCK:
            # Parse args/kwargs
            parsed = self.token_parser.parse(self.lexer.lex(token.content))
            token = parsed.pop(0)
            args = []
            kwargs = []
            for arg in all_args:
                if isinstance(arg, ast.keyword):
                    kwargs.append(arg)
                else:
                    args.append(arg)
            tag = self.tags[tag_name](self, *args, **kwargs)
            # place tag code in local "compiled_tags" storage
            self.compiled_tags.append(tag)
            code = ast.Call(
                func=ast.Subscript(
                    value=ast.Name(id='compiled_tags', ctx=ast.Load()),
                    slice=ast.Index(
                        value=ast.Num(n=len(self.compiled_tags)-1),
                        ctx=ast.Load()
                    ),
                    ctx=ast.Load(),
                ),
                args=args,
                keywords=kwargs,
            )
        else:
            # Must be a comment
            pass

        if code is not None:
            return token._position(code)

    def parse(self):
        """
        Convert the parsed tokens into a list of expressions then join them
        """
        self.stream = tokenise(self.source)
        steps = []
        for token in self.stream:
            code = self._token_to_code(token)
            if code:
                steps.append(code)

        # result = [str(x) for x in steps]
        return ast.Expression(
            body=ast.ListComp(
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

    def render(self, context={}):
        ctx = context.copy()
        ctx.update(self.default_context)
        return u''.join(eval(self.func, {}, {
            'context': ctx,
            'compiled_tags': self.compiled_tags,
            'filters': library.filters,
            'auto_escape': auto_escape,
        }))
