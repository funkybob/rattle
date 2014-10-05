import ast

from .tokenise import tokenise, TOKEN_TEXT, TOKEN_VAR, TOKEN_BLOCK
from .parser import pg, lg


class TemplateSyntaxError(Exception):
    pass


class Template(object):
    def __init__(self, source):
        self.source = source

        # A list of compiled tags
        self.compiled_tags = []
        self.filter_functions = {}

        self.lexer = lg.build()
        self.parser = pg.build()

        code = self.parse()
        ast.fix_missing_locations(code)
        self.func = compile(code, filename="<template>", mode="eval")

    def _token_to_code(self, token):
        '''Given a Token instance, convert it to AST'''
        code = None
        if token.mode == TOKEN_TEXT:
            code = ast.Str(s=token.content)
        elif token.mode == TOKEN_VAR:
            # parse
            code = self.parser.parse(self.lexer.lex(token.content))
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
                    slice=ast.Index(value=ast.Num(n=len(self.compiled_tags)-1), ctx=ast.Load()),
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
        '''Convert the parsed tokens into a list of expressions
        Then join them'''
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
        return u''.join(eval(self.func, {}, {
            'context': context,
            'compiled_tags': self.compiled_tags,
            'filters': self.filter_functions,
        }))
